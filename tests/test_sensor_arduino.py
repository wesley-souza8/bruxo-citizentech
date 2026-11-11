import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.assistente import AssistenteBruxo
from src.config import SAUDACAO_TOTEM
from src.ia_groq import ClienteIA
from src.reconhecimento import GerenciadorFacial
from src.sensor_arduino import SensorArduino
from src.servicos import ServicosWeb


class TestSensorArduino(unittest.TestCase):
    def test_extrair_distancia_formatos_validos(self):
        self.assertAlmostEqual(SensorArduino.extrair_distancia("DISTANCIA:35.4\r\n"), 35.4)
        self.assertAlmostEqual(SensorArduino.extrair_distancia("42"), 42.0)
        self.assertAlmostEqual(SensorArduino.extrair_distancia("Distancia: 18.7 cm"), 18.7)

    def test_extrair_distancia_rejeita_invalidos_e_fora_de_faixa(self):
        self.assertIsNone(SensorArduino.extrair_distancia(""))
        self.assertIsNone(SensorArduino.extrair_distancia("0"))
        self.assertIsNone(SensorArduino.extrair_distancia("-10"))
        self.assertIsNone(SensorArduino.extrair_distancia("DISTANCIA:-5"))
        self.assertIsNone(SensorArduino.extrair_distancia("DISTANCIA:999.9"))
        self.assertIsNone(SensorArduino.extrair_distancia("lixo_serial_" * 10))
        self.assertIsNone(SensorArduino.extrair_distancia("SEM_LEITURA"))

    def test_detectar_porta_ignora_com1_legado_e_prefere_arduino_usb(self):
        sensor = SensorArduino(callback_aproximacao=lambda d: None)
        porta_legada = SimpleNamespace(
            device="COM1",
            description="Porta de comunicação (COM1)",
            manufacturer="(Tipos de porta padrão)",
            hwid="ACPI\\PNP0501\\0",
            vid=None,
        )
        porta_arduino = SimpleNamespace(
            device="COM4",
            description="Arduino Uno (COM4)",
            manufacturer="Arduino LLC",
            hwid="USB VID:PID=2341:0043",
            vid=0x2341,
        )

        with patch("serial.tools.list_ports.comports", return_value=[porta_legada]):
            self.assertIsNone(sensor.detectar_porta())

        with patch("serial.tools.list_ports.comports", return_value=[porta_legada, porta_arduino]):
            self.assertEqual(sensor.detectar_porta(), "COM4")

    def test_dispara_saudacao_e_afastamento_com_histerese_e_cooldown(self):
        chamadas = []
        afastamentos = []
        sensor = SensorArduino(
            callback_aproximacao=lambda d: chamadas.append(d),
            callback_afastamento=lambda: afastamentos.append(True),
            distancia_limite_cm=50.0,
            cooldown_segundos=30.0,
            timeout_ausencia_segundos=5.0,
        )

        # >= 50 cm (Standby) não deve disparar
        self.assertFalse(sensor.processar_leitura(50.0, agora=100.0))
        self.assertFalse(sensor.processar_leitura(80.0, agora=101.0))
        self.assertEqual(chamadas, [])
        self.assertEqual(afastamentos, [])

        # Primeira aproximação < 50 cm deve disparar
        self.assertTrue(sensor.processar_leitura(42.5, agora=102.0))
        self.assertEqual(chamadas, [42.5])

        # Leituras contínuas enquanto cidadão permanece na frente não devem repetir
        self.assertFalse(sensor.processar_leitura(38.0, agora=103.0))
        self.assertFalse(sensor.processar_leitura(49.5, agora=104.0))

        # Ao se afastar (>= 60 cm), notifica retorno ao standby e respeita cooldown de 30 s
        self.assertFalse(sensor.processar_leitura(65.0, agora=110.0))
        self.assertEqual(len(afastamentos), 1)
        self.assertFalse(sensor.processar_leitura(30.0, agora=120.0))
        self.assertEqual(chamadas, [42.5])

        # Após se afastar (>= 60 cm) e vencer o cooldown (>= 30 s), dispara novamente
        self.assertFalse(sensor.processar_leitura(70.0, agora=131.0))
        self.assertTrue(sensor.processar_leitura(29.0, agora=133.0))
        self.assertEqual(chamadas, [42.5, 29.0])

    def test_reset_por_timeout_de_ausencia(self):
        chamadas = []
        afastamentos = []
        sensor = SensorArduino(
            callback_aproximacao=lambda d: chamadas.append(d),
            callback_afastamento=lambda: afastamentos.append(True),
            distancia_limite_cm=50.0,
            cooldown_segundos=10.0,
            timeout_ausencia_segundos=5.0,
        )

        self.assertTrue(sensor.processar_leitura(25.0, agora=10.0))
        # Sem novas leituras por >= 5 s e cooldown vencido (>= 10 s), deve encerrar sessão anterior e saudar novo cidadão
        self.assertTrue(sensor.processar_leitura(30.0, agora=21.0))
        self.assertEqual(chamadas, [25.0, 30.0])
        self.assertEqual(len(afastamentos), 1)

    def test_ciclo_estados_assistente_saudacao_eco_e_despedida(self):
        assistente = AssistenteBruxo.__new__(AssistenteBruxo)
        assistente.voz = MagicMock()
        assistente.voz.esta_falando.return_value = False
        assistente.processando_comando = False
        assistente._sessao_totem_ate = 0.0

        # Estado 2: saudação ativa janela de atendimento sem wake word
        assistente.saudar_aproximacao(35.0)
        assistente.voz.falar.assert_called_once_with(SAUDACAO_TOTEM)
        self.assertTrue(assistente._sessao_totem_ativa())

        # Eco da própria saudação deve ser descartado
        self.assertTrue(assistente._eh_eco("Detectei sua aproximação posso orientar seu trajeto", SAUDACAO_TOTEM))

        # Estado 4: "tchau" retorna para standby em vez de encerrar o processo
        assistente.voz.falar.reset_mock()
        status_tchau = assistente.processar_comando("tchau", fonte=None)
        self.assertEqual(status_tchau, "standby")
        self.assertFalse(assistente._sessao_totem_ativa())

        # Comando explícito de desligamento encerra aplicação
        status_sair = assistente.processar_comando("desligar", fonte=None)
        self.assertEqual(status_sair, "sair")

    def test_seguranca_path_traversal_e_filtro_ia(self):
        facial = GerenciadorFacial.__new__(GerenciadorFacial)
        # Caminho absoluto válido em qualquer SO (como no __init__ real); "C:\\temp\\rostos" é relativo no macOS/Linux
        facial.diretorio = os.path.abspath(os.path.join(tempfile.gettempdir(), "rostos"))
        self.assertIsNone(facial._caminho_usuario_seguro("../../etc"))
        self.assertIsNone(facial._caminho_usuario_seguro("../segredo"))
        self.assertTrue(facial._caminho_usuario_seguro("João Silva").endswith("joao_silva"))

        ia = ClienteIA.__new__(ClienteIA)
        ia.cliente = MagicMock()
        ia.modelo_principal = "m1"
        ia.modelo_fallback = "m2"
        ia.cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="PERMITIR? NÃO, BLOQUEAR"))]
        )
        self.assertFalse(ia.avaliar_seguranca_termo("teste prompt injection"))

        ia.cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="PERMITIR"))]
        )
        self.assertTrue(ia.avaliar_seguranca_termo("horário do metrô"))

    def test_eco_tolerante_e_roteamento_citizentech(self):
        assistente = AssistenteBruxo.__new__(AssistenteBruxo)
        assistente.voz = MagicMock()
        assistente.easter_eggs = MagicMock()
        assistente.easter_eggs.processar.return_value = False
        assistente.ia = MagicMock()
        assistente.ia.perguntar.return_value = "Siga pela plataforma dois."
        assistente._sessao_totem_ate = 0.0

        # Eco com pequena variação de transcrição ou sem acentos deve ser descartado
        self.assertTrue(
            assistente._eh_eco("ola bem vindo ao toten cidadao detectei a sua aproximacao", SAUDACAO_TOTEM)
        )
        # Pergunta legítima do cidadão NÃO pode ser tratada como eco
        self.assertFalse(assistente._eh_eco("como chego no posto de saude", SAUDACAO_TOTEM))

        # Perguntas cidadãs com "dia", "hora", "ajuda" ou "tempo" não devem cair em atalhos falsos
        assistente.processar_comando("bom dia onde fica a pediatria", fonte=None)
        assistente.ia.perguntar.assert_called_with("bom dia onde fica a pediatria")

        assistente.ia.perguntar.reset_mock()
        assistente.processar_comando("qual o horario de funcionamento do posto", fonte=None)
        assistente.ia.perguntar.assert_called_with("qual o horario de funcionamento do posto")

        assistente.ia.perguntar.reset_mock()
        assistente.processar_comando("preciso de ajuda para achar o metro", fonte=None)
        assistente.ia.perguntar.assert_called_with("preciso de ajuda para achar o metro")

        # Pergunta explícita de horas ainda aciona o utilitário local
        assistente.ia.perguntar.reset_mock()
        assistente.voz.falar.reset_mock()
        assistente.processar_comando("que horas são", fonte=None)
        assistente.ia.perguntar.assert_not_called()
        assistente.voz.falar.assert_called_once()

        # Formatação da cotação do dólar mantém ponto final correto
        with patch("src.servicos.requests.get", return_value=SimpleNamespace(json=lambda: {"USDBRL": {"bid": "5.55"}})):
            msg_dolar = ServicosWeb().obter_cotacao_dolar()
        self.assertEqual(msg_dolar, "A cotação atual do dólar é de 5,55 reais.")


if __name__ == "__main__":
    unittest.main()

import math
import re
import threading
import time
from typing import Callable

import serial
import serial.tools.list_ports

from src.config import (
    ARDUINO_BAUDRATE,
    ARDUINO_PORTA,
    COOLDOWN_TOTEM_SEGUNDOS,
    DISTANCIA_ATIVACAO_CM,
)


class SensorArduino:
    """
    Leitor serial não-bloqueante para integração do Arduino Uno + HC-SR04 com o Bruxo.

    Responsabilidades:
    - Detectar automaticamente a porta COM do Arduino (ou usar ARDUINO_PORTA configurada).
    - Escutar leituras de distância em thread daemon separada sem travar o assistente de voz.
    - Registrar telemetria de Standby (> 50 cm) de forma controlada e disparar saudação (< 50 cm)
      com histerese, cooldown e callback de afastamento (confirmado por leituras distantes contínuas,
      para que um eco falso isolado não encerre o atendimento).
    """

    _PADRAO_DISTANCIA = re.compile(
        r"^\s*(?:DIST(?:ANCIA)?\s*[:=]\s*)?(-?\d+(?:\.\d+)?)\s*(?:cm)?\s*$",
        re.IGNORECASE,
    )
    _PALAVRAS_ARDUINO = (
        "arduino",
        "uno",
        "ch340",
        "cp210",
        "ftdi",
        "usb serial",
        "usb-serial",
        "ttyacm",
        "ttyusb",
        "usbmodem",
    )
    _TAMANHO_MAX_LINHA = 64
    _DISTANCIA_MAX_VALIDA_CM = 400.0

    def __init__(
        self,
        callback_aproximacao: Callable[[float], None],
        callback_afastamento: Callable[[], None] | None = None,
        porta: str = ARDUINO_PORTA,
        baudrate: int = ARDUINO_BAUDRATE,
        distancia_limite_cm: float = DISTANCIA_ATIVACAO_CM,
        cooldown_segundos: float = COOLDOWN_TOTEM_SEGUNDOS,
        timeout_ausencia_segundos: float = 5.0,
        intervalo_log_standby_segundos: float = 2.0,
        confirmacao_afastamento_segundos: float = 0.0,
    ):
        self.callback_aproximacao = callback_aproximacao
        self.callback_afastamento = callback_afastamento
        self.porta = porta.strip() if porta else ""
        self.baudrate = baudrate
        self.distancia_limite_cm = float(distancia_limite_cm)
        self.cooldown_segundos = max(0.0, float(cooldown_segundos))
        self.timeout_ausencia_segundos = max(1.0, float(timeout_ausencia_segundos))
        self.intervalo_log_standby_segundos = max(0.5, float(intervalo_log_standby_segundos))
        # Tempo de leituras distantes contínuas para confirmar o afastamento (0 = imediato)
        self.confirmacao_afastamento_segundos = max(0.0, float(confirmacao_afastamento_segundos))

        self._lock = threading.Lock()
        self._parar_evento = threading.Event()
        self._thread: threading.Thread | None = None
        self._conexao: serial.Serial | None = None

        self._em_presenca = False
        self._ultimo_disparo = -math.inf
        self._ultima_deteccao = -math.inf
        self._ultimo_log_standby = -math.inf
        self._afastamento_desde: float | None = None

    @classmethod
    def extrair_distancia(cls, linha: str) -> float | None:
        """
        Extrai e valida a distância em centímetros de uma linha recebida via Serial.
        Aceita formatos como 'DISTANCIA:34.5', '34.5' ou 'Distancia: 34.5 cm'.
        Retorna None para linhas inválidas, corrompidas ou fora do alcance físico do HC-SR04.
        """
        if not isinstance(linha, str):
            return None

        texto = linha.strip()
        if not texto or len(texto) > cls._TAMANHO_MAX_LINHA:
            return None

        correspondencia = cls._PADRAO_DISTANCIA.search(texto)
        if not correspondencia:
            return None

        try:
            distancia = float(correspondencia.group(1))
        except ValueError:
            return None

        if not math.isfinite(distancia) or distancia <= 0.0 or distancia > cls._DISTANCIA_MAX_VALIDA_CM:
            return None

        return distancia

    def detectar_porta(self) -> str | None:
        """Retorna a porta configurada ou tenta identificar o Arduino USB via list_ports."""
        if self.porta:
            return self.porta

        portas = list(serial.tools.list_ports.comports())
        if not portas:
            return None

        for p in portas:
            descricao = f"{p.device} {p.description} {p.manufacturer} {p.hwid}".lower()
            if any(palavra in descricao for palavra in self._PALAVRAS_ARDUINO):
                return p.device

        # Fallback para qualquer adaptador USB-Serial com VID/HWID USB (ignora COM1 legado ACPI\PNP0501)
        for p in portas:
            hwid = (p.hwid or "").lower()
            if getattr(p, "vid", None) is not None or "usb" in hwid or "ttyacm" in p.device.lower():
                return p.device

        return None

    def _atualizar_ausencia(self, agora: float) -> bool:
        """
        Reseta o estado de presença caso não cheguem detecções dentro do timeout de ausência.
        Retorna True quando houve transição de presença ativa para standby.
        """
        if self._em_presenca and (agora - self._ultima_deteccao) >= self.timeout_ausencia_segundos:
            self._em_presenca = False
            self._afastamento_desde = None
            return True
        return False

    def processar_leitura(self, distancia_cm: float | None, agora: float | None = None) -> bool:
        """
        Avalia uma leitura de distância e aciona o callback na aproximação (< limite cm).
        Retorna True se o callback de saudação foi disparado.
        """
        if distancia_cm is None or not math.isfinite(distancia_cm) or distancia_cm <= 0.0:
            return False

        instante = time.monotonic() if agora is None else float(agora)
        disparar = False
        notificar_afastamento = False
        logar_standby = False

        with self._lock:
            if self._atualizar_ausencia(instante):
                notificar_afastamento = True

            if distancia_cm < self.distancia_limite_cm:
                self._ultima_deteccao = instante
                self._afastamento_desde = None
                if not self._em_presenca:
                    self._em_presenca = True
                    if (instante - self._ultimo_disparo) >= self.cooldown_segundos:
                        self._ultimo_disparo = instante
                        disparar = True
            else:
                if (instante - self._ultimo_log_standby) >= self.intervalo_log_standby_segundos:
                    self._ultimo_log_standby = instante
                    logar_standby = True

                if self._em_presenca and distancia_cm >= self.distancia_limite_cm + 10.0:
                    # Só confirma o afastamento após leituras distantes contínuas (eco falso isolado não encerra)
                    if self._afastamento_desde is None:
                        self._afastamento_desde = instante
                    if (instante - self._afastamento_desde) >= self.confirmacao_afastamento_segundos:
                        self._em_presenca = False
                        self._afastamento_desde = None
                        notificar_afastamento = True

        if logar_standby:
            print(
                f"[STANDBY HC-SR04]: Distância {distancia_cm:.0f} cm "
                f"(>= {self.distancia_limite_cm:.0f} cm) — LED apagado, aguardando aproximação."
            )

        if notificar_afastamento and self.callback_afastamento:
            try:
                self.callback_afastamento()
            except Exception as e:
                print(f"[ERRO SENSOR ARDUINO]: Falha ao executar callback de afastamento: {e}")

        if disparar and self.callback_aproximacao:
            try:
                self.callback_aproximacao(distancia_cm)
            except Exception as e:
                print(f"[ERRO SENSOR ARDUINO]: Falha ao executar callback de aproximação: {e}")
                return False
            return True

        return False

    def _fechar_conexao(self):
        if self._conexao is not None:
            try:
                if self._conexao.is_open:
                    self._conexao.close()
            except Exception:
                pass
            finally:
                self._conexao = None

    def _loop_leitura(self):
        aviso_sem_porta_exibido = False

        while not self._parar_evento.is_set():
            porta_alvo = self.detectar_porta()

            if not porta_alvo:
                if not aviso_sem_porta_exibido:
                    print("[SENSOR ARDUINO]: Nenhuma porta COM/Arduino detectada. Aguardando conexão...")
                    aviso_sem_porta_exibido = True
                self._parar_evento.wait(3.0)
                continue

            try:
                self._conexao = serial.Serial(porta_alvo, self.baudrate, timeout=0.2)
                aviso_sem_porta_exibido = False
                # Aguarda estabilização após auto-reset do Arduino Uno ao abrir porta serial
                self._parar_evento.wait(1.5)
                if not self._parar_evento.is_set():
                    try:
                        self._conexao.reset_input_buffer()
                    except Exception:
                        pass
                print(f"[SENSOR ARDUINO]: Escutando porta {porta_alvo} ({self.baudrate} baud) — limiar < {self.distancia_limite_cm:.0f} cm.")

                while not self._parar_evento.is_set():
                    saiu_por_ausencia = False
                    with self._lock:
                        saiu_por_ausencia = self._atualizar_ausencia(time.monotonic())

                    if saiu_por_ausencia and self.callback_afastamento:
                        try:
                            self.callback_afastamento()
                        except Exception as e:
                            print(f"[ERRO SENSOR ARDUINO]: Falha ao executar callback de afastamento: {e}")

                    raw = self._conexao.readline()
                    if not raw:
                        continue

                    linha = raw.decode("utf-8", errors="ignore")
                    distancia = self.extrair_distancia(linha)
                    if distancia is not None:
                        self.processar_leitura(distancia)

            except serial.SerialException as e:
                if not self._parar_evento.is_set():
                    print(f"[AVISO SENSOR ARDUINO]: Erro na porta {porta_alvo}: {e}. Tentando reconectar...")
                self._fechar_conexao()
                self._parar_evento.wait(3.0)
            except Exception as e:
                if not self._parar_evento.is_set():
                    print(f"[AVISO SENSOR ARDUINO]: Erro inesperado na leitura serial: {e}")
                self._fechar_conexao()
                self._parar_evento.wait(3.0)
            finally:
                self._fechar_conexao()

    def iniciar(self):
        """Inicia o leitor serial em background de forma não-bloqueante."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._parar_evento.clear()
        self._thread = threading.Thread(
            target=self._loop_leitura,
            name="SensorArduinoSerialThread",
            daemon=True,
        )
        self._thread.start()

    def parar(self):
        """Encerra a leitura serial e fecha a porta COM com segurança."""
        self._parar_evento.set()
        self._fechar_conexao()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()


def _ler_int_env(nome: str, padrao: int) -> int:
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao
    try:
        return int(valor)
    except ValueError:
        return padrao


def _ler_float_env(nome: str, padrao: float) -> float:
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao
    try:
        return float(valor)
    except ValueError:
        return padrao


# Caminhos base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_AGENDA = os.path.join(BASE_DIR, "agenda.txt")
PASTA_IMG = os.path.join(BASE_DIR, "img", "prints")

# Configurações do Assistente
NOME_ASSISTENTE = "bruxo"
NOMES_GATILHO = [NOME_ASSISTENTE, "o bruxo", "bruxão", "bruxao"]

# Configurações de Voz (Edge-TTS Neural)
VOZ_NEURAL = "pt-BR-AntonioNeural"
PITCH_GRAVE = "-12Hz"
VELOCIDADE_FALA = "+0%"

# Configurações de IA e APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELO_GROQ_PRINCIPAL = "openai/gpt-oss-120b"
MODELO_GROQ_FALLBACK = "qwen/qwen3.6-27b"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

# Configurações de Captação e Microfone (Timeouts em segundos)
TIMEOUT_PADRAO_ESCUTA = 5        # Timeout do loop contínuo de escuta (wake word)
TIMEOUT_RESPOSTA = 10            # Delay/tempo limite para o usuário responder a uma pergunta
LIMITE_FALA_PADRAO = 7           # Duração máxima de fala em escuta contínua
LIMITE_FALA_CURTA = 7            # Duração máxima para respostas curtas (ex: nomes, cidades, opções)
LIMITE_FALA_LONGA = 12           # Duração máxima para descrições longas (ex: eventos, buscas)

# Configurações do Totem CitizenTech (Arduino + Sensor Ultrassônico HC-SR04)
ARDUINO_PORTA = (os.getenv("ARDUINO_PORTA", "") or os.getenv("PORTA_SERIAL_ARDUINO", "")).strip()
ARDUINO_BAUDRATE = _ler_int_env("ARDUINO_BAUDRATE", 9600)
DISTANCIA_ATIVACAO_CM = _ler_float_env("DISTANCIA_ATIVACAO_CM", 50.0)
COOLDOWN_TOTEM_SEGUNDOS = _ler_float_env("COOLDOWN_TOTEM_SEGUNDOS", 30.0)
DURACAO_SESSAO_TOTEM_SEGUNDOS = _ler_float_env("DURACAO_SESSAO_TOTEM_SEGUNDOS", 45.0)
SAUDACAO_TOTEM = (
    "Olá! Bem-vindo ao Totem Cidadão. Detectei sua aproximação. "
    "Posso orientar seu trajeto, informar serviços ou ler um documento para você. Como posso ajudar?"
)

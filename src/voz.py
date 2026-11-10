import asyncio
import io
import threading
import time
import edge_tts
from gtts import gTTS
from pygame import mixer
from src.config import VOZ_NEURAL, PITCH_GRAVE, VELOCIDADE_FALA


class SintetizadorVoz:
    """
    Classe responsável pela síntese e reprodução de voz do assistente.
    Utiliza Edge-TTS (voz neural masculina grave) com fallback para gTTS.
    Permite reprodução assíncrona (não-bloqueante) e interrupção imediata.
    """

    def __init__(self):
        mixer.init()
        self.lock_audio = threading.Lock()
        self.thread_fala = None
        self._gerando_audio = False
        self._token_geracao = 0
        self._edge_disponivel = True
        self.ultimo_texto = ""

    async def _gerar_audio_edge(self, texto: str, velocidade: str = None) -> io.BytesIO:
        """Gera o áudio usando o serviço Neural Edge-TTS da Microsoft."""
        rate_usado = velocidade if velocidade else VELOCIDADE_FALA
        comunicador = edge_tts.Communicate(
            text=texto,
            voice=VOZ_NEURAL,
            pitch=PITCH_GRAVE,
            rate=rate_usado
        )
        buffer = io.BytesIO()
        async for chunk in comunicador.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        buffer.seek(0)
        return buffer

    def esta_falando(self) -> bool:
        """Verifica se o sintetizador está gerando ou reproduzindo áudio."""
        try:
            return bool(self._gerando_audio or (mixer.get_init() and mixer.music.get_busy()))
        except Exception:
            return bool(self._gerando_audio)

    def parar(self):
        """Interrompe imediatamente qualquer áudio em reprodução."""
        self._token_geracao += 1
        try:
            if mixer.get_init() and mixer.music.get_busy():
                mixer.music.stop()
        except Exception:
            pass

    def _tocar_audio(self, texto: str, velocidade: str = None, token: int | None = None):
        """Gera e toca o áudio diretamente na memória RAM."""
        with self.lock_audio:
            if token is not None and token != self._token_geracao:
                return
            self._gerando_audio = True
            try:
                buffer_audio = None
                if self._edge_disponivel:
                    try:
                        buffer_audio = asyncio.run(self._gerar_audio_edge(texto, velocidade=velocidade))
                    except Exception as e:
                        self._edge_disponivel = False
                        print(f"[AVISO VOZ]: Edge-TTS indisponível ({type(e).__name__}); usando fallback gTTS.")

                if buffer_audio is None:
                    buffer_audio = io.BytesIO()
                    tts = gTTS(text=texto, lang="pt", tld="com.br")
                    tts.write_to_fp(buffer_audio)
                    buffer_audio.seek(0)

                if token is not None and token != self._token_geracao:
                    return

                mixer.music.load(buffer_audio, "mp3")
                mixer.music.play()
                self._gerando_audio = False

                while mixer.music.get_busy():
                    time.sleep(0.05)

            except Exception as e:
                print(f"[ERRO VOZ]: {type(e).__name__}")
            finally:
                self._gerando_audio = False

    def falar(self, texto: str, prefixo: str = "BRUXO", aguardar: bool = False, velocidade: str = None):
        """
        Fala um texto.
        - aguardar=False: Executa em segundo plano sem travar o microfone.
        - aguardar=True: Espera o término da reprodução.
        - velocidade: Taxa de velocidade pontual (ex: "+25%"). Se omitido, usa o padrão do sistema.
        """
        texto_limpo = texto.strip()
        # Tratamento para evitar quebra do console com caracteres não reconhecidos (ex: hifens especiais)
        try:
            print(f"[{prefixo}]: \"{texto_limpo}\"")
        except UnicodeEncodeError:
            texto_ascii = texto_limpo.encode('ascii', 'replace').decode('ascii')
            print(f"[{prefixo}]: \"{texto_ascii}\"")
            
        if not texto_limpo:
            return

        self.ultimo_texto = texto_limpo
        self.parar()
        token_atual = self._token_geracao

        if aguardar:
            self._tocar_audio(texto_limpo, velocidade=velocidade, token=token_atual)
        else:
            self._gerando_audio = True
            self.thread_fala = threading.Thread(
                target=self._tocar_audio,
                args=(texto_limpo, velocidade, token_atual),
                daemon=True
            )
            self.thread_fala.start()

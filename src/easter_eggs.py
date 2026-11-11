import re
import webbrowser


class GerenciadorEasterEggs:
    """
    Classe responsável por gerenciar e responder aos Easter Eggs e piadas do Bruxo.
    Isola conteúdos de humor da lógica de negócio e orquestração do assistente.
    """

    def processar(self, comando: str, voz) -> bool:
        """
        Verifica se o comando corresponde a um Easter Egg registrado.
        Retorna True se processou um Easter Egg, ou False caso contrário.
        """
        comando_limpo = comando.strip().lower()

        # 1. EASTER EGG: ALANZOKA
        if re.search(r"\b(alanzoka|alan zoka|alanzo)\b", comando_limpo):
            voz.falar("Nextage, bebê!")
            return True

        # 2. EASTER EGG: PEGA NO BREU
        elif any(t in comando_limpo for t in [
            "pega no breu", "gaitaço", "gaitaco",
            "agro pesca jacaré", "agro pesca jacare", "pega no bre"
        ]):
            webbrowser.open("https://www.youtube.com/watch?v=TFdO7oqkMzI")
            return True

        return False

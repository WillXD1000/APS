"""Integração com o Google Gemini (IA generativa).

Responsável por:
    - interpretar a qualidade do ar em linguagem natural;
    - gerar recomendações personalizadas pelo perfil de saúde;
    - responder perguntas do chatbot ambiental.

Projetado para degradar com elegância: se a chave não estiver configurada ou
a API falhar, cai em respostas locais (fallback) para não quebrar o fluxo. O
motivo da falha é registrado no terminal do backend e usado na mensagem do chat.

Para economizar a cota gratuita, a interpretação de cada combinação de local,
categoria e perfil é reaproveitada por CACHE_INTERPRETACAO_SEGUNDOS.

Documentação do SDK: https://github.com/googleapis/python-genai
"""

import logging
import threading
import time

from app.core.config import settings

logger = logging.getLogger("airia.gemini")

# Tempo de reaproveitamento de uma interpretação já gerada (30 minutos).
CACHE_INTERPRETACAO_SEGUNDOS = 30 * 60

# Cache em memória, compartilhado entre as requisições deste processo.
_cache_interpretacao: dict[tuple, tuple[float, tuple[str, str]]] = {}
_cache_lock = threading.Lock()

# Mensagens do chat conforme o motivo da falha.
MENSAGENS_FALHA_CHAT = {
    "cota": (
        "O limite gratuito de uso da IA foi atingido por hoje. "
        "Tente novamente mais tarde."
    ),
    "modelo": (
        "O modelo de IA configurado não está disponível. "
        "Verifique o GEMINI_MODEL no backend."
    ),
    "chave": (
        "A chave do Gemini é inválida ou não tem permissão. "
        "Verifique o GEMINI_API_KEY no backend."
    ),
    "outro": (
        "Não consegui responder agora devido a uma instabilidade no serviço "
        "de IA. Tente novamente em instantes."
    ),
}


def classificar_erro(erro: Exception) -> str:
    """Traduz o erro da API em um motivo: cota, modelo, chave ou outro."""
    codigo = getattr(erro, "code", None)
    if codigo == 429:
        return "cota"
    if codigo == 404:
        return "modelo"
    # Chave inválida costuma vir como 400 ("API key not valid"); sem permissão, 401/403.
    if codigo in (401, 403) or (codigo == 400 and "API key" in str(erro)):
        return "chave"
    return "outro"

# Descrições amigáveis de cada perfil de saúde para enriquecer o prompt.
PERFIS_DESCRICAO = {
    "geral": "uma pessoa sem condições de saúde específicas",
    "asmatico": "uma pessoa asmática (sensível a poluentes do ar)",
    "idoso": "uma pessoa idosa",
    "atleta": "um atleta que pratica exercícios ao ar livre",
    "crianca": "uma criança",
}

# Mensagens de fallback por categoria do IQAr (usadas quando a IA não responde).
FALLBACK_POR_CATEGORIA = {
    "Boa": "A qualidade do ar está boa. Condições ideais para atividades ao ar livre.",
    "Moderada": (
        "A qualidade do ar está moderada. Pessoas sensíveis devem ficar atentas a "
        "sintomas ao se exercitarem ao ar livre."
    ),
    "Ruim": (
        "A qualidade do ar está ruim. Grupos sensíveis devem evitar esforço físico "
        "ao ar livre."
    ),
    "Muito Ruim": (
        "A qualidade do ar está muito ruim. Evite atividades ao ar livre e, se "
        "possível, permaneça em ambientes fechados."
    ),
    "Péssima": (
        "A qualidade do ar está péssima. Evite sair; o ar representa risco à saúde "
        "de todos."
    ),
}


class GeminiService:
    """Cliente do Gemini com fallback local."""

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.modelo = settings.gemini_model
        self._client = None  # inicializado sob demanda (lazy)
        self.ultimo_erro: str | None = None  # motivo da última falha

    @property
    def disponivel(self) -> bool:
        """Indica se há chave configurada para usar o Gemini."""
        return bool(self.api_key)

    def _get_client(self):
        """Instancia o client do Gemini sob demanda.

        O import é local para que a aplicação suba mesmo sem o pacote/chave.
        """
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _gerar(self, prompt: str) -> str | None:
        """Chama o Gemini e retorna o texto, ou None em caso de falha."""
        self.ultimo_erro = None
        if not self.disponivel:
            return None
        try:
            client = self._get_client()
            resposta = client.models.generate_content(
                model=self.modelo,
                contents=prompt,
            )
            texto = (resposta.text or "").strip()
            return texto or None
        except Exception as erro:
            # Qualquer falha cai no fallback, mas o motivo fica registrado.
            self.ultimo_erro = classificar_erro(erro)
            logger.warning(
                "Falha ao chamar o Gemini (modelo=%s, motivo=%s): %s",
                self.modelo,
                self.ultimo_erro,
                str(erro)[:300],
            )
            return None

    # ------------------------------------------------------------------ #
    # Interpretação + recomendação da qualidade do ar
    # ------------------------------------------------------------------ #
    def interpretar_qualidade_ar(
        self,
        cidade: str | None,
        categoria: str | None,
        poluentes: dict[str, float | None],
        perfil_saude: str,
    ) -> tuple[str, str]:
        """Gera (interpretacao, recomendacao) para uma medição.

        Sempre retorna textos úteis: usa o Gemini quando possível e, caso
        contrário, mensagens locais baseadas na categoria.
        """
        local = cidade or "sua região"
        perfil_desc = PERFIS_DESCRICAO.get(perfil_saude, PERFIS_DESCRICAO["geral"])

        # Monta uma lista legível dos poluentes disponíveis.
        medidos = ", ".join(
            f"{k.upper()}={v}" for k, v in poluentes.items() if v is not None
        )
        medidos = medidos or "sem poluentes medidos"

        prompt = (
            "Você é um assistente de qualidade do ar. Responda em português do "
            "Brasil, de forma simples e acolhedora.\n"
            f"Local: {local}.\n"
            f"Categoria do ar: {categoria}.\n"
            f"Poluentes (µg/m³): {medidos}.\n"
            f"Perfil do usuário: {perfil_desc}.\n\n"
            "Responda em DUAS partes, exatamente neste formato:\n"
            "INTERPRETACAO: <uma frase explicando como está o ar hoje>\n"
            "RECOMENDACAO: <uma frase com uma recomendação prática para este "
            "perfil>"
        )

        # Reaproveita uma interpretação recente para economizar a cota.
        chave_cache = (local, categoria, perfil_saude)
        agora = time.monotonic()
        with _cache_lock:
            em_cache = _cache_interpretacao.get(chave_cache)
        if em_cache and em_cache[0] > agora:
            return em_cache[1]

        texto = self._gerar(prompt)
        if texto:
            interpretacao, recomendacao = self._separar_partes(texto)
            if interpretacao and recomendacao:
                with _cache_lock:
                    _cache_interpretacao[chave_cache] = (
                        agora + CACHE_INTERPRETACAO_SEGUNDOS,
                        (interpretacao, recomendacao),
                    )
                return interpretacao, recomendacao

        # Fallback local.
        return self._fallback_interpretacao(categoria, perfil_saude)

    @staticmethod
    def _separar_partes(texto: str) -> tuple[str | None, str | None]:
        """Extrai INTERPRETACAO e RECOMENDACAO do texto gerado."""
        interpretacao = None
        recomendacao = None
        for linha in texto.splitlines():
            limpa = linha.strip()
            upper = limpa.upper()
            if upper.startswith("INTERPRETACAO:"):
                interpretacao = limpa.split(":", 1)[1].strip()
            elif upper.startswith("RECOMENDACAO:"):
                recomendacao = limpa.split(":", 1)[1].strip()
        return interpretacao, recomendacao

    @staticmethod
    def _fallback_interpretacao(
        categoria: str | None, perfil_saude: str
    ) -> tuple[str, str]:
        """Interpretação/recomendação locais quando a IA não está disponível."""
        interpretacao = FALLBACK_POR_CATEGORIA.get(
            categoria or "",
            "Não foi possível avaliar a qualidade do ar no momento.",
        )
        recomendacoes_perfil = {
            "asmatico": "Como você é sensível a poluentes, tenha sempre a medicação por perto.",
            "idoso": "Prefira atividades em horários de ar mais limpo e hidrate-se bem.",
            "atleta": "Avalie treinar em ambiente fechado se o ar não estiver bom.",
            "crianca": "Fique atento a sintomas respiratórios em crianças.",
            "geral": "Acompanhe a evolução da qualidade do ar ao longo do dia.",
        }
        recomendacao = recomendacoes_perfil.get(
            perfil_saude, recomendacoes_perfil["geral"]
        )
        return interpretacao, recomendacao

    # ------------------------------------------------------------------ #
    # Chatbot ambiental
    # ------------------------------------------------------------------ #
    def responder_chat(
        self, pergunta: str, contexto_ar: str | None = None
    ) -> str:
        """Responde a uma pergunta do usuário sobre qualidade do ar/ambiente."""
        contexto = (
            f"\nContexto da última medição do usuário: {contexto_ar}."
            if contexto_ar
            else ""
        )
        prompt = (
            "Você é um assistente ambiental especializado em qualidade do ar e "
            "saúde. Responda em português do Brasil, de forma clara, objetiva e "
            "acolhedora, em no máximo 4 frases."
            f"{contexto}\n\n"
            f"Pergunta do usuário: {pergunta}"
        )

        texto = self._gerar(prompt)
        if texto:
            return texto

        # Fallback quando a IA está indisponível.
        if not self.disponivel:
            return (
                "O assistente de IA não está configurado no momento. "
                "Configure a chave do Gemini para usar o chat."
            )
        return MENSAGENS_FALHA_CHAT.get(
            self.ultimo_erro or "outro", MENSAGENS_FALHA_CHAT["outro"]
        )

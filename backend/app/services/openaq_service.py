"""Integração com a API da OpenAQ (dados de qualidade do ar).

Documentação: https://docs.openaq.org (API v3).

Fluxo:
    1. Busca a estação (location) mais próxima das coordenadas.
    2. Lê as medições mais recentes (latest) dos sensores dessa estação.
    3. Normaliza os poluentes em um dicionário padronizado.

A chave de API é lida de settings.openaq_api_key e enviada no header X-API-Key.
"""

import httpx

from app.core.config import settings

OPENAQ_BASE_URL = "https://api.openaq.org/v3"
# Raio máximo de busca aceito pela API (25 km).
RAIO_BUSCA_METROS = 25000
TIMEOUT_SEGUNDOS = 10.0

# Mapeia os nomes de parâmetros da OpenAQ para as chaves usadas no sistema.
MAPA_PARAMETROS = {
    "pm25": "pm25",
    "pm10": "pm10",
    "o3": "o3",
    "no2": "no2",
    "co": "co",
}


class OpenAQError(Exception):
    """Erro ao consultar a OpenAQ (com mensagem amigável)."""

    def __init__(self, mensagem: str) -> None:
        self.mensagem = mensagem
        super().__init__(mensagem)


class DadosQualidadeAr:
    """Estrutura simples com os dados retornados pela OpenAQ."""

    def __init__(
        self,
        cidade: str | None,
        poluentes: dict[str, float],
        estacao: str | None,
    ) -> None:
        self.cidade = cidade
        self.poluentes = poluentes  # ex.: {"pm25": 12.3, "o3": 45.0}
        self.estacao = estacao


class OpenAQService:
    """Cliente da API OpenAQ v3."""

    def __init__(self) -> None:
        self.api_key = settings.openaq_api_key

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise OpenAQError(
                "Chave da OpenAQ não configurada. Defina OPENAQ_API_KEY no .env."
            )
        return {"X-API-Key": self.api_key}

    def buscar_por_coordenadas(self, lat: float, lon: float) -> DadosQualidadeAr:
        """Busca a qualidade do ar na estação mais próxima das coordenadas.

        Levanta OpenAQError em caso de falha ou ausência de estação.
        """
        try:
            with httpx.Client(timeout=TIMEOUT_SEGUNDOS) as client:
                location = self._buscar_estacao_proxima(client, lat, lon)
                poluentes = self._buscar_medicoes_recentes(client, location["id"])
        except httpx.TimeoutException:
            raise OpenAQError("A OpenAQ demorou para responder. Tente novamente.")
        except httpx.HTTPError as erro:
            raise OpenAQError(f"Falha ao consultar a OpenAQ: {erro}")

        if not poluentes:
            raise OpenAQError(
                "A estação mais próxima não possui medições recentes de poluentes."
            )

        # Extrai nome da cidade/localidade quando disponível.
        cidade = location.get("locality") or location.get("name")

        return DadosQualidadeAr(
            cidade=cidade,
            poluentes=poluentes,
            estacao=location.get("name"),
        )

    def _buscar_estacao_proxima(
        self, client: httpx.Client, lat: float, lon: float
    ) -> dict:
        """Retorna a estação (location) mais próxima das coordenadas."""
        url = f"{OPENAQ_BASE_URL}/locations"
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": RAIO_BUSCA_METROS,
            "limit": 1,
        }
        resp = client.get(url, params=params, headers=self._headers())

        if resp.status_code == 401:
            raise OpenAQError("Chave da OpenAQ inválida (401). Verifique OPENAQ_API_KEY.")
        resp.raise_for_status()

        resultados = resp.json().get("results", [])
        if not resultados:
            raise OpenAQError(
                "Nenhuma estação de monitoramento encontrada num raio de 25 km "
                "desta localização."
            )
        return resultados[0]

    def _buscar_medicoes_recentes(
        self, client: httpx.Client, location_id: int
    ) -> dict[str, float]:
        """Retorna os poluentes mais recentes de uma estação, já normalizados."""
        url = f"{OPENAQ_BASE_URL}/locations/{location_id}/latest"
        resp = client.get(url, headers=self._headers())
        resp.raise_for_status()

        poluentes: dict[str, float] = {}
        for medicao in resp.json().get("results", []):
            # Cada resultado traz o sensor e seu valor mais recente.
            parametro = self._extrair_parametro(medicao)
            valor = medicao.get("value")
            if parametro in MAPA_PARAMETROS and valor is not None:
                chave = MAPA_PARAMETROS[parametro]
                # Mantém o primeiro valor por poluente (o mais recente).
                poluentes.setdefault(chave, float(valor))
        return poluentes

    @staticmethod
    def _extrair_parametro(medicao: dict) -> str | None:
        """Extrai o nome do parâmetro (ex.: 'pm25') de um registro latest.

        A estrutura pode variar entre 'sensor.parameter.name' e 'parameter.name',
        então tratamos ambos os formatos de forma defensiva.
        """
        sensor = medicao.get("sensor") or {}
        parametro = sensor.get("parameter") or medicao.get("parameter") or {}
        nome = parametro.get("name")
        return nome.lower() if isinstance(nome, str) else None

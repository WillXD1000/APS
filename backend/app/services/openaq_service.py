"""Integração com a API da OpenAQ (dados de qualidade do ar).

Documentação: https://docs.openaq.org (API v3).

Fluxo:
    1. Busca estações (locations) próximas das coordenadas, ordenadas por distância.
    2. Para cada estação, monta o mapa sensorsId -> parâmetro (a partir da lista
       de 'sensors' da própria location).
    3. Lê as medições mais recentes (/latest) e cruza pelo sensorsId para
       descobrir qual poluente é cada valor.
    4. Usa a primeira estação que tiver medições válidas dos poluentes de interesse.

A chave de API é lida de settings.openaq_api_key e enviada no header X-API-Key.
"""

import httpx

from app.core.config import settings

OPENAQ_BASE_URL = "https://api.openaq.org/v3"
# Raio máximo de busca aceito pela API (25 km).
RAIO_BUSCA_METROS = 25000
# Quantas estações próximas tentar antes de desistir.
MAX_ESTACOES = 10
TIMEOUT_SEGUNDOS = 15.0

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
        """Busca a qualidade do ar na estação válida mais próxima das coordenadas.

        Percorre as estações por ordem de proximidade e usa a primeira que
        possuir medições recentes dos poluentes de interesse.

        Levanta OpenAQError em caso de falha ou ausência de dados.
        """
        try:
            with httpx.Client(timeout=TIMEOUT_SEGUNDOS) as client:
                estacoes = self._buscar_estacoes_proximas(client, lat, lon)

                if not estacoes:
                    raise OpenAQError(
                        "Nenhuma estação de monitoramento encontrada num raio de "
                        "25 km desta localização."
                    )

                for estacao in estacoes:
                    poluentes = self._buscar_medicoes_recentes(client, estacao)
                    if poluentes:
                        cidade = estacao.get("locality") or estacao.get("name")
                        return DadosQualidadeAr(
                            cidade=cidade,
                            poluentes=poluentes,
                            estacao=estacao.get("name"),
                        )
        except httpx.TimeoutException:
            raise OpenAQError("A OpenAQ demorou para responder. Tente novamente.")
        except httpx.HTTPStatusError as erro:
            # Repassa o detalhe do corpo de erro da OpenAQ, quando houver,
            # para facilitar a identificação do problema.
            detalhe = ""
            try:
                corpo = erro.response.json()
                detalhe = corpo.get("detail") or corpo.get("message") or ""
            except Exception:
                detalhe = erro.response.text[:200] if erro.response is not None else ""
            sufixo = f" Detalhe: {detalhe}" if detalhe else ""
            raise OpenAQError(
                f"Falha ao consultar a OpenAQ (HTTP {erro.response.status_code})."
                f"{sufixo}"
            )
        except httpx.HTTPError as erro:
            raise OpenAQError(f"Falha ao consultar a OpenAQ: {erro}")

        # Chegou aqui: havia estações, mas nenhuma com dados recentes dos
        # poluentes que monitoramos.
        raise OpenAQError(
            "As estações próximas não possuem medições recentes dos poluentes "
            "monitorados (PM2.5, PM10, O3, NO2, CO). Tente novamente mais tarde."
        )

    def _buscar_estacoes_proximas(
        self, client: httpx.Client, lat: float, lon: float
    ) -> list[dict]:
        """Retorna estações próximas, ordenadas por distância (mais perto primeiro)."""
        url = f"{OPENAQ_BASE_URL}/locations"
        # Ao informar coordinates + radius, a API já retorna as estações
        # ordenadas por proximidade. Não usamos order_by=distance porque esse
        # endpoint não aceita esse valor (retorna HTTP 422).
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": RAIO_BUSCA_METROS,
            "limit": MAX_ESTACOES,
        }
        resp = client.get(url, params=params, headers=self._headers())

        if resp.status_code == 401:
            raise OpenAQError(
                "Chave da OpenAQ inválida (401). Verifique OPENAQ_API_KEY."
            )
        resp.raise_for_status()

        return resp.json().get("results", [])

    def _mapa_sensores(self, estacao: dict) -> dict[int, str]:
        """Monta o mapa {sensorsId: nome_parametro} a partir da location.

        Cada estação traz uma lista 'sensors', e cada sensor informa qual
        parâmetro (pm25, o3, ...) ele mede.
        """
        mapa: dict[int, str] = {}
        for sensor in estacao.get("sensors") or []:
            sensor_id = sensor.get("id")
            parametro = sensor.get("parameter") or {}
            nome = parametro.get("name")
            if sensor_id is not None and isinstance(nome, str):
                mapa[sensor_id] = nome.lower()
        return mapa

    def _buscar_medicoes_recentes(
        self, client: httpx.Client, estacao: dict
    ) -> dict[str, float]:
        """Retorna os poluentes mais recentes de uma estação, já normalizados.

        Cruza os valores do endpoint /latest com o parâmetro de cada sensor
        (via sensorsId). Como fallback, tenta ler o parâmetro embutido no
        próprio registro, caso a API o forneça.
        """
        location_id = estacao.get("id")
        if location_id is None:
            return {}

        mapa_sensores = self._mapa_sensores(estacao)

        url = f"{OPENAQ_BASE_URL}/locations/{location_id}/latest"
        resp = client.get(url, headers=self._headers())
        resp.raise_for_status()

        poluentes: dict[str, float] = {}
        for medicao in resp.json().get("results", []):
            valor = medicao.get("value")
            if valor is None:
                continue

            # 1) tenta descobrir o parâmetro pelo sensorsId (caminho principal)
            parametro = None
            sensor_id = medicao.get("sensorsId")
            if sensor_id is not None:
                parametro = mapa_sensores.get(sensor_id)

            # 2) fallback: parâmetro embutido no próprio registro
            if parametro is None:
                parametro = self._extrair_parametro(medicao)

            if parametro in MAPA_PARAMETROS:
                chave = MAPA_PARAMETROS[parametro]
                # Mantém o primeiro valor por poluente (o mais recente).
                poluentes.setdefault(chave, float(valor))

        return poluentes

    @staticmethod
    def _extrair_parametro(medicao: dict) -> str | None:
        """Extrai o nome do parâmetro embutido num registro, se existir.

        Trata os formatos 'sensor.parameter.name' e 'parameter.name'.
        """
        sensor = medicao.get("sensor") or {}
        parametro = sensor.get("parameter") or medicao.get("parameter") or {}
        nome = parametro.get("name")
        return nome.lower() if isinstance(nome, str) else None

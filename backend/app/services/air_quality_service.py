"""Serviço de orquestração da qualidade do ar.

Reúne a busca na OpenAQ, o cálculo do IQAr e a persistência no histórico.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.medicao import Medicao
from app.repositories.medicao_repository import MedicaoRepository
from app.schemas.medicao import Poluentes, QualidadeArResponse
from app.services.gemini_service import GeminiService
from app.services.iqar_service import calcular_iqar
from app.services.openaq_service import OpenAQError, OpenAQService


class AirQualityService:
    """Orquestra a consulta de qualidade do ar e o histórico."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MedicaoRepository(db)
        self.openaq = OpenAQService()
        self.gemini = GeminiService()

    def consultar(
        self,
        lat: float,
        lon: float,
        usuario_id: int | None = None,
        perfil_saude: str = "geral",
    ) -> QualidadeArResponse:
        """Consulta a qualidade do ar, calcula o IQAr, interpreta com IA e salva.

        Levanta OpenAQError se a consulta externa falhar.
        """
        dados = self.openaq.buscar_por_coordenadas(lat, lon)
        p = dados.poluentes

        resultado = calcular_iqar(
            pm25=p.get("pm25"),
            pm10=p.get("pm10"),
            o3=p.get("o3"),
            no2=p.get("no2"),
            co=p.get("co"),
        )

        categoria = resultado.categoria if resultado else None

        # Interpretação e recomendação da IA (com fallback local).
        interpretacao, recomendacao = self.gemini.interpretar_qualidade_ar(
            cidade=dados.cidade,
            categoria=categoria,
            poluentes=p,
            perfil_saude=perfil_saude,
        )

        agora = datetime.now(timezone.utc)

        # Persiste no histórico (vinculado ao usuário, quando logado).
        medicao = Medicao(
            usuario_id=usuario_id,
            latitude=lat,
            longitude=lon,
            cidade=dados.cidade,
            pm25=p.get("pm25"),
            pm10=p.get("pm10"),
            o3=p.get("o3"),
            no2=p.get("no2"),
            co=p.get("co"),
            indice_geral=resultado.indice_geral if resultado else None,
            categoria=categoria,
            coletado_em=agora,
        )
        self.repo.criar(medicao)

        return QualidadeArResponse(
            latitude=lat,
            longitude=lon,
            cidade=dados.cidade,
            estacao=dados.estacao,
            poluentes=Poluentes(**p),
            indice_geral=resultado.indice_geral if resultado else None,
            categoria=categoria,
            poluente_critico=resultado.poluente_critico if resultado else None,
            interpretacao=interpretacao,
            recomendacao=recomendacao,
            coletado_em=agora,
        )

    def historico(self, usuario_id: int, limite: int = 50) -> list[Medicao]:
        """Retorna o histórico de medições de um usuário."""
        return self.repo.listar_por_usuario(usuario_id, limite)

    def contexto_ar_usuario(self, usuario_id: int) -> str | None:
        """Monta uma descrição curta da última medição do usuário (p/ o chat)."""
        medicao = self.repo.ultima_por_usuario(usuario_id)
        if medicao is None:
            return None
        local = medicao.cidade or "sua região"
        categoria = medicao.categoria or "desconhecida"
        return f"em {local}, a qualidade do ar mais recente foi '{categoria}'"


# Reexporta OpenAQError para a camada de rotas tratar o erro.
__all__ = ["AirQualityService", "OpenAQError"]

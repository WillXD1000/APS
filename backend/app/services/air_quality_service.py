"""Serviço de orquestração da qualidade do ar.

Reúne a busca na OpenAQ, o cálculo do IQAr, a interpretação por IA, os alertas,
a persistência no histórico e o relatório agregado por dia.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.medicao import Medicao
from app.repositories.medicao_repository import MedicaoRepository
from app.schemas.alerta import AlertaAtual
from app.schemas.medicao import (
    Poluentes,
    QualidadeArResponse,
    RelatorioDia,
    RelatorioResponse,
)
from app.services.alert_service import AlertService
from app.services.gemini_service import GeminiService
from app.services.iqar_service import calcular_iqar, categoria_por_indice
from app.services.openaq_service import OpenAQError, OpenAQService

# Fuso usado para agrupar as consultas por dia no relatório (horário de Brasília).
FUSO_RELATORIO = timezone(timedelta(hours=-3))


def agregar_por_dia(
    registros: list[tuple[datetime, int | None]], dias: int, hoje: date
) -> RelatorioResponse:
    """Agrupa (coletado_em, indice) por dia, incluindo dias sem consultas.

    Função pura (sem banco), para facilitar testes.
    """
    inicio = hoje - timedelta(days=dias - 1)
    por_dia: dict[date, list[int]] = {}
    totais: dict[date, int] = {}

    for coletado_em, indice in registros:
        if coletado_em.tzinfo is None:
            coletado_em = coletado_em.replace(tzinfo=timezone.utc)
        dia = coletado_em.astimezone(FUSO_RELATORIO).date()
        if dia < inicio or dia > hoje:
            continue
        totais[dia] = totais.get(dia, 0) + 1
        if indice is not None:
            por_dia.setdefault(dia, []).append(indice)

    itens: list[RelatorioDia] = []
    todos_indices: list[int] = []
    for i in range(dias):
        dia = inicio + timedelta(days=i)
        indices = por_dia.get(dia, [])
        todos_indices.extend(indices)
        media = round(sum(indices) / len(indices)) if indices else None
        itens.append(
            RelatorioDia(
                data=dia,
                total=totais.get(dia, 0),
                indice_medio=media,
                indice_maximo=max(indices) if indices else None,
                categoria=categoria_por_indice(media) if media is not None else None,
            )
        )

    media_periodo = (
        round(sum(todos_indices) / len(todos_indices)) if todos_indices else None
    )
    return RelatorioResponse(
        dias=dias,
        inicio=inicio,
        fim=hoje,
        total_consultas=sum(item.total for item in itens),
        indice_medio_periodo=media_periodo,
        itens=itens,
    )


class AirQualityService:
    """Orquestra a consulta de qualidade do ar e o histórico."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MedicaoRepository(db)
        self.openaq = OpenAQService()
        self.gemini = GeminiService()
        self.alertas = AlertService(db)

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

        # Alerta conforme o perfil de saúde (gravado sem repetir em sequência).
        alerta = None
        if usuario_id is not None:
            avaliacao, novo = self.alertas.processar(
                usuario_id=usuario_id,
                perfil_saude=perfil_saude,
                categoria=categoria,
                cidade=dados.cidade,
            )
            if avaliacao is not None:
                alerta = AlertaAtual(
                    nivel=avaliacao.nivel, mensagem=avaliacao.mensagem, novo=novo
                )

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
            alerta=alerta,
            coletado_em=agora,
        )

    def historico(self, usuario_id: int, limite: int = 50) -> list[Medicao]:
        """Retorna o histórico de medições de um usuário."""
        return self.repo.listar_por_usuario(usuario_id, limite)

    def relatorio(self, usuario_id: int, dias: int = 7) -> RelatorioResponse:
        """Relatório dos últimos 'dias' dias, agrupado por dia (Brasília)."""
        hoje = datetime.now(FUSO_RELATORIO).date()
        inicio = hoje - timedelta(days=dias - 1)
        desde = datetime.combine(inicio, datetime.min.time(), tzinfo=FUSO_RELATORIO)
        medicoes = self.repo.listar_desde(usuario_id, desde)
        registros = [(m.coletado_em, m.indice_geral) for m in medicoes]
        return agregar_por_dia(registros, dias, hoje)

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

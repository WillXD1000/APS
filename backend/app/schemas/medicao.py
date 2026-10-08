"""Schemas Pydantic para qualidade do ar, histórico e relatório."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alerta import AlertaAtual


class Poluentes(BaseModel):
    """Concentrações de poluentes (µg/m³). Campos ausentes vêm como None."""

    pm25: float | None = None
    pm10: float | None = None
    o3: float | None = None
    no2: float | None = None
    co: float | None = None


class QualidadeArResponse(BaseModel):
    """Resposta do endpoint de qualidade do ar."""

    latitude: float
    longitude: float
    cidade: str | None = None
    estacao: str | None = None
    poluentes: Poluentes
    indice_geral: int | None = None
    categoria: str | None = None
    poluente_critico: str | None = None
    # Textos gerados pela IA (ou fallback local) — Etapa 3.
    interpretacao: str | None = None
    recomendacao: str | None = None
    # Alerta para o perfil do usuário, quando o ar exige atenção — Etapa 5.
    alerta: AlertaAtual | None = None
    coletado_em: datetime


class RelatorioDia(BaseModel):
    """Resumo das consultas de um dia (dias sem consulta vêm com total 0)."""

    data: date
    total: int
    indice_medio: int | None = None
    indice_maximo: int | None = None
    categoria: str | None = None  # categoria do índice médio


class RelatorioResponse(BaseModel):
    """Relatório agregado por dia, usado no gráfico do app."""

    dias: int
    inicio: date
    fim: date
    total_consultas: int
    indice_medio_periodo: int | None = None
    itens: list[RelatorioDia]


class MedicaoOut(BaseModel):
    """Item do histórico de medições retornado pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: float
    longitude: float
    cidade: str | None
    pm25: float | None
    pm10: float | None
    o3: float | None
    no2: float | None
    co: float | None
    indice_geral: int | None
    categoria: str | None
    coletado_em: datetime


class Coordenadas(BaseModel):
    """Validação das coordenadas recebidas na query."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 a 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 a 180)")

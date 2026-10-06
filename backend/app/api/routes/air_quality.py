"""Rotas de qualidade do ar: consulta atual e histórico."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_atual
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.medicao import MedicaoOut, QualidadeArResponse
from app.services.air_quality_service import AirQualityService, OpenAQError

router = APIRouter(tags=["Qualidade do Ar"])


@router.get("/air-quality", response_model=QualidadeArResponse)
def consultar_qualidade_ar(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> QualidadeArResponse:
    """Retorna a qualidade do ar da localização informada (dados + IQAr).

    Requer autenticação. A medição é salva no histórico do usuário.
    """
    service = AirQualityService(db)
    try:
        return service.consultar(lat=lat, lon=lon, usuario_id=usuario.id)
    except OpenAQError as erro:
        # 502: falha ao obter dados de um serviço externo.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=erro.mensagem
        )


@router.get("/history", response_model=list[MedicaoOut])
def historico(
    limite: int = Query(50, ge=1, le=200, description="Máximo de registros"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> list[MedicaoOut]:
    """Retorna o histórico de medições do usuário logado."""
    service = AirQualityService(db)
    medicoes = service.historico(usuario_id=usuario.id, limite=limite)
    return [MedicaoOut.model_validate(m) for m in medicoes]

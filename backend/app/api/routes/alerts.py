"""Rotas de alertas de qualidade do ar."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_atual
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.alerta import AlertaOut
from app.services.alert_service import AlertService

router = APIRouter(tags=["Alertas"])


@router.get("/alerts", response_model=list[AlertaOut])
def listar_alertas(
    limite: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> list[AlertaOut]:
    """Retorna os alertas do usuário logado, mais recentes primeiro."""
    alertas = AlertService(db).listar(usuario.id, limite)
    return [AlertaOut.model_validate(a) for a in alertas]

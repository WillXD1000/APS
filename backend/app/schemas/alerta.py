"""Schemas Pydantic para alertas de qualidade do ar."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertaAtual(BaseModel):
    """Alerta referente à consulta atual (incluído na resposta de /air-quality).

    'novo' indica que o alerta acabou de ser registrado no histórico; o app usa
    esse campo para decidir se mostra o popup ou apenas o banner.
    """

    nivel: str
    mensagem: str
    novo: bool = False


class AlertaOut(BaseModel):
    """Item do histórico de alertas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nivel: str
    mensagem: str
    enviado_em: datetime

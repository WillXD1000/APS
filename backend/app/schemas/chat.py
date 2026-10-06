"""Schemas Pydantic para o chatbot ambiental."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Pergunta enviada ao chatbot."""

    pergunta: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    """Resposta do chatbot."""

    pergunta: str
    resposta: str


class ConversaOut(BaseModel):
    """Item do histórico de conversas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pergunta: str
    resposta: str
    criado_em: datetime

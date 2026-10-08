"""Rota do chatbot ambiental (Gemini)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_atual
from app.core.database import get_db
from app.models.usuario import Usuario
from app.repositories.conversa_repository import ConversaRepository
from app.schemas.chat import ChatRequest, ChatResponse, ConversaOut
from app.services.air_quality_service import AirQualityService
from app.services.gemini_service import GeminiService

router = APIRouter(tags=["Chatbot Ambiental"])


@router.post("/chat", response_model=ChatResponse)
def conversar(
    dados: ChatRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> ChatResponse:
    """Responde a uma pergunta do usuário sobre qualidade do ar/ambiente.

    Usa a última medição do usuário como contexto, quando disponível, e salva
    a conversa no histórico.
    """
    gemini = GeminiService()

    # Contexto: última medição do usuário (enriquece a resposta).
    contexto = AirQualityService(db).contexto_ar_usuario(usuario.id)

    resposta = gemini.responder_chat(pergunta=dados.pergunta, contexto_ar=contexto)

    # Persiste a conversa.
    ConversaRepository(db).criar(
        usuario_id=usuario.id,
        pergunta=dados.pergunta,
        resposta=resposta,
    )

    return ChatResponse(pergunta=dados.pergunta, resposta=resposta)


@router.get("/chat/history", response_model=list[ConversaOut])
def historico_chat(
    limite: int = Query(50, ge=1, le=200, description="Máximo de registros"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> list[ConversaOut]:
    """Retorna o histórico de conversas do usuário logado."""
    conversas = ConversaRepository(db).listar_por_usuario(usuario.id, limite)
    return [ConversaOut.model_validate(c) for c in conversas]

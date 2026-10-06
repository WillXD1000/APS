"""Modelo da tabela de conversas do chatbot ambiental."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversa(Base):
    """Guarda cada par pergunta/resposta do chatbot (Gemini).

    Preenchida a partir da Etapa 3 (integração com o Gemini).
    """

    __tablename__ = "conversas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario = relationship("Usuario", back_populates="conversas")

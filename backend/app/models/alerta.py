"""Modelo da tabela de alertas enviados ao usuário."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alerta(Base):
    """Registra um alerta enviado ao usuário (ex.: qualidade do ar perigosa).

    Preenchida a partir da Etapa 5 (notificações).
    """

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    # Nível do alerta: 'info', 'atencao', 'perigo'.
    nivel: Mapped[str] = mapped_column(String(20), default="info", nullable=False)

    enviado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario = relationship("Usuario", back_populates="alertas")

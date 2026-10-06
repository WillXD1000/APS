"""Modelo da tabela de usuários."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    """Representa um usuário do aplicativo e seu perfil de saúde."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(160), unique=True, index=True, nullable=False
    )
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Perfil de saúde influencia as recomendações da IA (Etapa 3).
    # Ex.: 'geral', 'asmatico', 'idoso', 'atleta', 'crianca'.
    perfil_saude: Mapped[str] = mapped_column(
        String(40), default="geral", nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos (um usuário tem muitas medições, alertas e conversas).
    medicoes = relationship("Medicao", back_populates="usuario")
    alertas = relationship("Alerta", back_populates="usuario")
    conversas = relationship("Conversa", back_populates="usuario")

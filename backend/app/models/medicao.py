"""Modelo da tabela de medições de qualidade do ar."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Medicao(Base):
    """Armazena uma consulta de qualidade do ar feita pelo usuário.

    Preenchida a partir da Etapa 2 (integração com a OpenAQ).
    """

    __tablename__ = "medicoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    cidade: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Poluentes (µg/m³). Podem ser nulos quando a estação não mede algum deles.
    pm25: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True)
    o3: Mapped[float | None] = mapped_column(Float, nullable=True)
    no2: Mapped[float | None] = mapped_column(Float, nullable=True)
    co: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Índice geral calculado (IQAr) e sua categoria textual.
    indice_geral: Mapped[int | None] = mapped_column(Integer, nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(30), nullable=True)

    coletado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario = relationship("Usuario", back_populates="medicoes")

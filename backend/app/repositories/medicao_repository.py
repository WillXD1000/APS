"""Camada de acesso a dados (repositório) para a entidade Medicao."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.medicao import Medicao


class MedicaoRepository:
    """Operações de persistência para medições de qualidade do ar."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, medicao: Medicao) -> Medicao:
        """Persiste uma nova medição."""
        self.db.add(medicao)
        self.db.commit()
        self.db.refresh(medicao)
        return medicao

    def listar_por_usuario(
        self, usuario_id: int, limite: int = 50
    ) -> list[Medicao]:
        """Lista o histórico de medições de um usuário, mais recentes primeiro."""
        stmt = (
            select(Medicao)
            .where(Medicao.usuario_id == usuario_id)
            .order_by(Medicao.coletado_em.desc())
            .limit(limite)
        )
        return list(self.db.execute(stmt).scalars().all())

    def ultima_por_usuario(self, usuario_id: int) -> Medicao | None:
        """Retorna a medição mais recente de um usuário, ou None."""
        stmt = (
            select(Medicao)
            .where(Medicao.usuario_id == usuario_id)
            .order_by(Medicao.coletado_em.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

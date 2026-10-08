"""Camada de acesso a dados (repositório) para a entidade Alerta."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta


class AlertaRepository:
    """Operações de persistência para alertas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, usuario_id: int, mensagem: str, nivel: str) -> Alerta:
        """Persiste um novo alerta."""
        alerta = Alerta(usuario_id=usuario_id, mensagem=mensagem, nivel=nivel)
        self.db.add(alerta)
        self.db.commit()
        self.db.refresh(alerta)
        return alerta

    def existe_recente(self, usuario_id: int, nivel: str, desde: datetime) -> bool:
        """Indica se já existe alerta do mesmo nível para o usuário desde 'desde'."""
        stmt = (
            select(Alerta.id)
            .where(
                Alerta.usuario_id == usuario_id,
                Alerta.nivel == nivel,
                Alerta.enviado_em >= desde,
            )
            .limit(1)
        )
        return self.db.execute(stmt).first() is not None

    def listar_por_usuario(self, usuario_id: int, limite: int = 20) -> list[Alerta]:
        """Lista os alertas de um usuário, mais recentes primeiro."""
        stmt = (
            select(Alerta)
            .where(Alerta.usuario_id == usuario_id)
            .order_by(Alerta.enviado_em.desc())
            .limit(limite)
        )
        return list(self.db.execute(stmt).scalars().all())

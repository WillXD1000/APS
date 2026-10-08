"""Camada de acesso a dados (repositório) para a entidade Conversa."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversa import Conversa


class ConversaRepository:
    """Operações de persistência para conversas do chatbot."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, usuario_id: int, pergunta: str, resposta: str) -> Conversa:
        """Persiste um par pergunta/resposta."""
        conversa = Conversa(
            usuario_id=usuario_id,
            pergunta=pergunta,
            resposta=resposta,
        )
        self.db.add(conversa)
        self.db.commit()
        self.db.refresh(conversa)
        return conversa

    def listar_por_usuario(
        self, usuario_id: int, limite: int = 50
    ) -> list[Conversa]:
        """Lista o histórico de conversas de um usuário, mais recentes primeiro."""
        stmt = (
            select(Conversa)
            .where(Conversa.usuario_id == usuario_id)
            .order_by(Conversa.criado_em.desc())
            .limit(limite)
        )
        return list(self.db.execute(stmt).scalars().all())

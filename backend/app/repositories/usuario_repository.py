"""Camada de acesso a dados (repositório) para a entidade Usuario.

Isola as operações de banco, mantendo os serviços livres de detalhes de SQL.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    """Operações de persistência para usuários."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Retorna o usuário com o e-mail informado, ou None."""
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Retorna o usuário pelo id, ou None."""
        return self.db.get(Usuario, usuario_id)

    def criar(
        self, nome: str, email: str, senha_hash: str, perfil_saude: str
    ) -> Usuario:
        """Cria e persiste um novo usuário."""
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            perfil_saude=perfil_saude,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def atualizar_perfil(self, usuario: Usuario, perfil_saude: str) -> Usuario:
        """Altera o perfil de saúde de um usuário e persiste."""
        usuario.perfil_saude = perfil_saude
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

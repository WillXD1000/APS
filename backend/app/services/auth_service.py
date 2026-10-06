"""Regras de negócio de autenticação: cadastro, login e emissão de token."""

from sqlalchemy.orm import Session

from app.core.security import criar_token_acesso, hash_senha, verificar_senha
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import Token, UsuarioCreate, UsuarioLogin, UsuarioOut


class AuthError(Exception):
    """Erro de autenticação com mensagem amigável para a camada de API."""

    def __init__(self, mensagem: str) -> None:
        self.mensagem = mensagem
        super().__init__(mensagem)


class AuthService:
    """Orquestra o fluxo de autenticação usando o repositório de usuários."""

    def __init__(self, db: Session) -> None:
        self.repo = UsuarioRepository(db)

    def registrar(self, dados: UsuarioCreate) -> UsuarioOut:
        """Cadastra um novo usuário, garantindo e-mail único."""
        if self.repo.buscar_por_email(dados.email):
            raise AuthError("Já existe um usuário com este e-mail.")

        usuario = self.repo.criar(
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            perfil_saude=dados.perfil_saude.value,
        )
        return UsuarioOut.model_validate(usuario)

    def login(self, dados: UsuarioLogin) -> Token:
        """Valida credenciais e retorna um token de acesso."""
        usuario = self.repo.buscar_por_email(dados.email)
        if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
            raise AuthError("E-mail ou senha inválidos.")

        token = criar_token_acesso(subject=usuario.id)
        return Token(
            access_token=token,
            usuario=UsuarioOut.model_validate(usuario),
        )

    def buscar_usuario(self, usuario_id: int) -> Usuario | None:
        """Busca um usuário pelo id (usado pela dependência de token)."""
        return self.repo.buscar_por_id(usuario_id)

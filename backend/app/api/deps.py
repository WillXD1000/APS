"""Dependências reutilizáveis da camada de API."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario
from app.services.auth_service import AuthService

# Define que o token vem no header Authorization: Bearer <token>.
# tokenUrl aponta para a rota OAuth2 (/auth/token), usada pelo botão
# "Authorize" do Swagger para obter o token automaticamente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Extrai e valida o usuário logado a partir do token JWT.

    Levanta 401 se o token for inválido ou o usuário não existir.
    """
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    sub = decodificar_token(token)
    if sub is None:
        raise credenciais_invalidas

    service = AuthService(db)
    usuario = service.buscar_usuario(int(sub))
    if usuario is None:
        raise credenciais_invalidas

    return usuario

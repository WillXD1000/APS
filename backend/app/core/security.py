"""Funções de segurança: hash de senha e geração/validação de tokens JWT."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto de hashing de senhas usando bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera o hash seguro de uma senha em texto puro."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara uma senha em texto puro com o hash armazenado."""
    return pwd_context.verify(senha, senha_hash)


def criar_token_acesso(subject: str | int) -> str:
    """Cria um token JWT de acesso.

    Args:
        subject: identificador do usuário (geralmente o id), gravado no claim 'sub'.

    Returns:
        O token JWT assinado como string.
    """
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"sub": str(subject), "exp": expira_em}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> str | None:
    """Decodifica e valida um token JWT.

    Returns:
        O 'sub' (id do usuário) se o token for válido; None caso contrário.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None

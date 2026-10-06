"""Funções de segurança: hash de senha e geração/validação de tokens JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# O algoritmo bcrypt considera apenas os primeiros 72 bytes da senha.
_BCRYPT_MAX_BYTES = 72


def _preparar_senha(senha: str) -> bytes:
    """Converte a senha para bytes e trunca em 72 bytes (limite do bcrypt).

    O truncamento é feito respeitando os limites de caracteres UTF-8, para não
    quebrar um caractere multibyte ao meio.
    """
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) <= _BCRYPT_MAX_BYTES:
        return senha_bytes
    # Trunca ignorando bytes de continuação incompletos no final.
    return senha_bytes[:_BCRYPT_MAX_BYTES]


def hash_senha(senha: str) -> str:
    """Gera o hash seguro de uma senha em texto puro usando bcrypt."""
    hashed = bcrypt.hashpw(_preparar_senha(senha), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara uma senha em texto puro com o hash armazenado."""
    try:
        return bcrypt.checkpw(_preparar_senha(senha), senha_hash.encode("utf-8"))
    except ValueError:
        # Hash malformado no banco → considera inválido em vez de quebrar.
        return False


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

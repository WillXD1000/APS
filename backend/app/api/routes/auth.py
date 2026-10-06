"""Rotas de autenticação: cadastro, login e dados do usuário logado."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_atual
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioLogin, UsuarioOut
from app.services.auth_service import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioOut:
    """Cadastra um novo usuário."""
    service = AuthService(db)
    try:
        return service.registrar(dados)
    except AuthError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=erro.mensagem
        )


@router.post("/login", response_model=Token)
def login(dados: UsuarioLogin, db: Session = Depends(get_db)) -> Token:
    """Autentica o usuário via JSON e retorna um token de acesso (JWT).

    Usada pelo aplicativo mobile. Corpo: {"email": "...", "senha": "..."}.
    """
    service = AuthService(db)
    try:
        return service.login(dados)
    except AuthError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=erro.mensagem
        )


@router.post("/token", response_model=Token)
def login_oauth2(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """Login no padrão OAuth2 (formulário), usado pelo botão 'Authorize' do Swagger.

    O campo 'username' deve conter o e-mail do usuário, e 'password' a senha.
    Reaproveita a mesma lógica do /auth/login.
    """
    service = AuthService(db)
    try:
        return service.login(UsuarioLogin(email=form.username, senha=form.password))
    except AuthError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=erro.mensagem
        )


@router.get("/me", response_model=UsuarioOut)
def meus_dados(usuario: Usuario = Depends(get_usuario_atual)) -> UsuarioOut:
    """Retorna os dados do usuário autenticado (valida o token)."""
    return UsuarioOut.model_validate(usuario)

"""Schemas Pydantic para entrada e saída de dados de usuário e autenticação."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PerfilSaude(str, Enum):
    """Perfis de saúde suportados (usados para personalizar recomendações)."""

    GERAL = "geral"
    ASMATICO = "asmatico"
    IDOSO = "idoso"
    ATLETA = "atleta"
    CRIANCA = "crianca"


class UsuarioCreate(BaseModel):
    """Dados recebidos no cadastro de um novo usuário."""

    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=72)
    perfil_saude: PerfilSaude = PerfilSaude.GERAL


class UsuarioLogin(BaseModel):
    """Dados recebidos no login."""

    email: EmailStr
    senha: str


class UsuarioOut(BaseModel):
    """Dados de usuário retornados pela API (nunca inclui a senha)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    perfil_saude: str
    criado_em: datetime


class PerfilUpdate(BaseModel):
    """Dados para alterar o perfil de saúde do usuário logado."""

    perfil_saude: PerfilSaude


class Token(BaseModel):
    """Resposta do login contendo o token de acesso."""

    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut

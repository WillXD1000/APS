"""Ponto de entrada da aplicação FastAPI do AirIA."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa os modelos para que o SQLAlchemy conheça todas as tabelas.
from app import models  # noqa: F401
from app.api.routes import air_quality, auth, chat
from app.core.config import settings
from app.core.database import Base, engine


def criar_tabelas() -> None:
    """Cria as tabelas no banco caso ainda não existam.

    Em produção, o ideal é usar migrações (Alembic). Para o escopo da APS,
    a criação automática é suficiente.
    """
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=f"{settings.app_name} API",
    description="API do assistente inteligente de qualidade do ar.",
    version="0.1.0",
)

# CORS liberado para desenvolvimento (o app mobile acessa de outra origem).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Executa a criação das tabelas na inicialização da aplicação."""
    criar_tabelas()


@app.get("/", tags=["Health"])
def health_check() -> dict:
    """Verifica se a API está no ar."""
    return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}


# Registra as rotas da aplicação.
app.include_router(auth.router)
app.include_router(air_quality.router)
app.include_router(chat.router)

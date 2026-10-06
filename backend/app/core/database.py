"""Configuração da conexão com o banco de dados (SQLAlchemy)."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Engine: gerencia o pool de conexões com o PostgreSQL.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # verifica a conexão antes de usar (evita conexões "mortas")
    echo=settings.debug,  # loga as queries SQL quando em modo debug
)

# Fábrica de sessões: cada requisição usa uma sessão própria.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Classe base da qual todos os modelos (tabelas) herdam."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependência do FastAPI que fornece uma sessão de banco por requisição.

    Garante que a sessão seja sempre fechada ao final, mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

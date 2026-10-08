"""Configurações da aplicação, carregadas a partir de variáveis de ambiente (.env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centraliza todas as configurações do backend.

    Os valores são lidos do arquivo .env (ou de variáveis de ambiente do sistema).
    """

    # Aplicação
    app_name: str = "AirIA"
    debug: bool = True

    # Banco de dados
    database_url: str = "postgresql://postgres:postgres@localhost:5432/airia"

    # Segurança / JWT
    jwt_secret: str = "troque-por-um-segredo-forte-e-aleatorio"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 horas

    # Serviços externos (usados nas próximas etapas)
    gemini_api_key: str = ""
    # Cada modelo tem a sua própria cota gratuita diária.
    gemini_model: str = "gemini-3.5-flash-lite"
    openaq_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instância única reutilizada em toda a aplicação.
settings = Settings()

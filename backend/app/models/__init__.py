"""Importa todos os modelos para que o SQLAlchemy os registre na metadata.

Importante: ao importar este pacote, todas as tabelas ficam conhecidas pela
Base, permitindo que Base.metadata.create_all() crie todas de uma vez.
"""

from app.models.alerta import Alerta
from app.models.conversa import Conversa
from app.models.medicao import Medicao
from app.models.usuario import Usuario

__all__ = ["Usuario", "Medicao", "Alerta", "Conversa"]

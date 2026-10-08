"""Regras e persistência de alertas de qualidade do ar.

A cada consulta, o sistema avalia se a qualidade do ar exige um alerta para o
perfil de saúde do usuário. Perfis sensíveis (asmático, idoso, criança) são
alertados a partir da categoria "Moderada"; os demais, a partir de "Ruim".

Para não repetir o mesmo aviso a cada consulta, um alerta do mesmo nível só é
gravado novamente depois de JANELA_SEM_REPETICAO.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.alerta_repository import AlertaRepository

# Ordem das categorias do IQAr, da melhor para a pior.
ORDEM_CATEGORIAS = ["Boa", "Moderada", "Ruim", "Muito Ruim", "Péssima"]

# Perfis mais vulneráveis à poluição: alertados mais cedo.
PERFIS_SENSIVEIS = {"asmatico", "idoso", "crianca"}

# Intervalo mínimo entre dois alertas do mesmo nível para o mesmo usuário.
JANELA_SEM_REPETICAO = timedelta(hours=3)


@dataclass
class AvaliacaoAlerta:
    """Resultado da regra de alerta para uma medição."""

    nivel: str  # 'atencao' ou 'perigo'
    mensagem: str


def avaliar_alerta(
    categoria: str | None, perfil_saude: str, cidade: str | None
) -> AvaliacaoAlerta | None:
    """Aplica a regra de alerta. Retorna None quando não há o que alertar."""
    if categoria not in ORDEM_CATEGORIAS:
        return None

    sensivel = perfil_saude in PERFIS_SENSIVEIS
    limiar = "Moderada" if sensivel else "Ruim"
    if ORDEM_CATEGORIAS.index(categoria) < ORDEM_CATEGORIAS.index(limiar):
        return None

    nivel = "perigo" if categoria in ("Muito Ruim", "Péssima") else "atencao"
    local = cidade or "sua região"

    if nivel == "perigo":
        conselho = "Evite sair e, se possível, mantenha as janelas fechadas."
    elif categoria == "Moderada":
        conselho = (
            "Como seu perfil é sensível à poluição, evite esforço físico "
            "prolongado ao ar livre."
        )
    else:
        conselho = "Evite atividades físicas intensas ao ar livre."

    mensagem = f"Qualidade do ar {categoria.lower()} em {local}. {conselho}"
    return AvaliacaoAlerta(nivel=nivel, mensagem=mensagem)


class AlertService:
    """Avalia, deduplica e grava alertas."""

    def __init__(self, db: Session) -> None:
        self.repo = AlertaRepository(db)

    def processar(
        self,
        usuario_id: int,
        perfil_saude: str,
        categoria: str | None,
        cidade: str | None,
    ) -> tuple[AvaliacaoAlerta | None, bool]:
        """Avalia a medição e grava o alerta se ainda não houver um recente.

        Returns:
            (avaliacao, novo): a avaliação atual (ou None) e se ela gerou um
            alerta novo no histórico (usado pelo app para exibir o popup).
        """
        avaliacao = avaliar_alerta(categoria, perfil_saude, cidade)
        if avaliacao is None:
            return None, False

        desde = datetime.now(timezone.utc) - JANELA_SEM_REPETICAO
        if self.repo.existe_recente(usuario_id, avaliacao.nivel, desde):
            return avaliacao, False

        self.repo.criar(usuario_id, avaliacao.mensagem, avaliacao.nivel)
        return avaliacao, True

    def listar(self, usuario_id: int, limite: int = 20):
        """Lista os alertas do usuário, mais recentes primeiro."""
        return self.repo.listar_por_usuario(usuario_id, limite)

"""Cálculo do Índice de Qualidade do Ar (IQAr).

Converte as concentrações de poluentes (µg/m³) em um índice de 0 a 500 e uma
categoria textual, seguindo o padrão brasileiro adotado pela CETESB/MMA.

Referência de faixas (índice final e categoria):
    0–40    → Boa
    41–80   → Moderada
    81–120  → Ruim
    121–200 → Muito Ruim
    > 200   → Péssima

O índice geral de uma medição é o MAIOR índice entre todos os poluentes
disponíveis (o poluente mais crítico define a categoria).
"""

from dataclasses import dataclass

# Categorias e seus limites superiores de índice.
CATEGORIAS = [
    (40, "Boa"),
    (80, "Moderada"),
    (120, "Ruim"),
    (200, "Muito Ruim"),
    (float("inf"), "Péssima"),
]

# Pontos de quebra (breakpoints) por poluente.
# Cada tupla: (conc_min, conc_max, indice_min, indice_max).
# Concentrações em µg/m³ (CO em mg/m³, convertido quando necessário).
# Baseado nas faixas do IQAr da CETESB.
BREAKPOINTS: dict[str, list[tuple[float, float, int, int]]] = {
    # Material particulado fino (média 24h)
    "pm25": [
        (0, 25, 0, 40),
        (25, 50, 41, 80),
        (50, 75, 81, 120),
        (75, 125, 121, 200),
        (125, 300, 201, 400),
    ],
    # Material particulado inalável (média 24h)
    "pm10": [
        (0, 50, 0, 40),
        (50, 100, 41, 80),
        (100, 150, 81, 120),
        (150, 250, 121, 200),
        (250, 600, 201, 400),
    ],
    # Ozônio (média 8h)
    "o3": [
        (0, 100, 0, 40),
        (100, 130, 41, 80),
        (130, 160, 81, 120),
        (160, 200, 121, 200),
        (200, 800, 201, 400),
    ],
    # Dióxido de nitrogênio (média 1h)
    "no2": [
        (0, 200, 0, 40),
        (200, 240, 41, 80),
        (240, 320, 81, 120),
        (320, 1130, 121, 200),
        (1130, 3750, 201, 400),
    ],
    # Monóxido de carbono (média 8h, em µg/m³; faixas originais em mg/m³)
    "co": [
        (0, 9000, 0, 40),
        (9000, 11000, 41, 80),
        (11000, 13000, 81, 120),
        (13000, 15000, 121, 200),
        (15000, 50000, 201, 400),
    ],
}


@dataclass
class ResultadoIQAr:
    """Resultado do cálculo do IQAr para uma medição."""

    indice_geral: int
    categoria: str
    poluente_critico: str | None  # qual poluente definiu o índice


def _indice_por_poluente(poluente: str, concentracao: float) -> int | None:
    """Calcula o índice (0–400) de um único poluente por interpolação linear."""
    faixas = BREAKPOINTS.get(poluente)
    if faixas is None or concentracao is None or concentracao < 0:
        return None

    for conc_min, conc_max, idx_min, idx_max in faixas:
        if conc_min <= concentracao <= conc_max:
            # Interpolação linear dentro da faixa.
            proporcao = (
                (concentracao - conc_min) / (conc_max - conc_min)
                if conc_max > conc_min
                else 0
            )
            return round(idx_min + proporcao * (idx_max - idx_min))

    # Acima da maior faixa: satura no índice máximo.
    return 500


def _categoria_por_indice(indice: int) -> str:
    """Retorna a categoria textual para um índice."""
    for limite, nome in CATEGORIAS:
        if indice <= limite:
            return nome
    return "Péssima"


def calcular_iqar(
    pm25: float | None = None,
    pm10: float | None = None,
    o3: float | None = None,
    no2: float | None = None,
    co: float | None = None,
) -> ResultadoIQAr | None:
    """Calcula o IQAr geral a partir dos poluentes disponíveis.

    O índice geral é o maior entre os poluentes informados (o mais crítico).

    Returns:
        ResultadoIQAr, ou None se nenhum poluente válido foi fornecido.
    """
    valores = {"pm25": pm25, "pm10": pm10, "o3": o3, "no2": no2, "co": co}

    indices: dict[str, int] = {}
    for poluente, concentracao in valores.items():
        if concentracao is None:
            continue
        indice = _indice_por_poluente(poluente, concentracao)
        if indice is not None:
            indices[poluente] = indice

    if not indices:
        return None

    poluente_critico = max(indices, key=indices.get)
    indice_geral = indices[poluente_critico]

    return ResultadoIQAr(
        indice_geral=indice_geral,
        categoria=_categoria_por_indice(indice_geral),
        poluente_critico=poluente_critico,
    )

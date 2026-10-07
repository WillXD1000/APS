// Paleta de cores do app e mapeamento de cores por categoria do IQAr.

export const COLORS = {
  primary: "#2E7D5B",
  primaryDark: "#1B5E3F",
  background: "#F4F6F5",
  surface: "#FFFFFF",
  text: "#1A1A1A",
  textMuted: "#667085",
  border: "#E4E7EC",
  danger: "#D32F2F",
  white: "#FFFFFF",
};

// Cores oficiais por categoria do Índice de Qualidade do Ar (IQAr).
export const CATEGORIA_CORES = {
  Boa: "#2E9E4F",
  Moderada: "#F2C200",
  Ruim: "#F28500",
  "Muito Ruim": "#D32F2F",
  Péssima: "#7B1FA2",
};

export function corDaCategoria(categoria) {
  return CATEGORIA_CORES[categoria] || COLORS.textMuted;
}

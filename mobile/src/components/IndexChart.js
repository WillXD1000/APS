// Gráfico de barras do índice médio por dia (sem biblioteca externa).
// Cada barra recebe a cor da categoria do IQAr do dia.

import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { COLORS, corDaCategoria } from "../config/theme";

const ALTURA_GRAFICO = 120;
const DIAS_SEMANA = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];

// Converte "AAAA-MM-DD" em dia da semana sem sofrer com fuso horário.
function diaDaSemana(dataIso) {
  const [ano, mes, dia] = dataIso.split("-").map(Number);
  return DIAS_SEMANA[new Date(ano, mes - 1, dia).getDay()];
}

export default function IndexChart({ relatorio }) {
  const itens = relatorio?.itens || [];
  if (itens.length === 0) return null;

  const maiorValor = Math.max(100, ...itens.map((i) => i.indice_medio || 0));

  return (
    <View style={styles.card}>
      <Text style={styles.titulo}>Índice médio — últimos {relatorio.dias} dias</Text>
      <Text style={styles.subtitulo}>
        {relatorio.total_consultas} consulta(s)
        {relatorio.indice_medio_periodo != null
          ? ` · média do período: ${relatorio.indice_medio_periodo}`
          : ""}
      </Text>

      <View style={styles.grafico}>
        {itens.map((item) => {
          const temDado = item.indice_medio != null;
          const altura = temDado
            ? Math.max(6, (item.indice_medio / maiorValor) * ALTURA_GRAFICO)
            : 4;
          return (
            <View key={item.data} style={styles.coluna}>
              <Text style={styles.valor}>{temDado ? item.indice_medio : "–"}</Text>
              <View
                style={[
                  styles.barra,
                  {
                    height: altura,
                    backgroundColor: temDado
                      ? corDaCategoria(item.categoria)
                      : COLORS.border,
                  },
                ]}
              />
              <Text style={styles.dia}>{diaDaSemana(item.data)}</Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 16,
  },
  titulo: { fontSize: 15, fontWeight: "700", color: COLORS.text },
  subtitulo: { fontSize: 12, color: COLORS.textMuted, marginTop: 2 },
  grafico: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    height: ALTURA_GRAFICO + 44,
    marginTop: 12,
  },
  coluna: { flex: 1, alignItems: "center", justifyContent: "flex-end" },
  valor: { fontSize: 11, color: COLORS.textMuted, marginBottom: 4 },
  barra: { width: 18, borderRadius: 6 },
  dia: { fontSize: 11, color: COLORS.textMuted, marginTop: 6 },
});

// Card que exibe o resultado da qualidade do ar: índice, categoria (com cor),
// poluentes e os textos gerados pela IA (interpretação e recomendação).

import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { COLORS, corDaCategoria } from "../config/theme";

// 'local' é o nome do lugar onde o usuário está (vem do GPS do celular).
// A estação usada na medição aparece embaixo, como "Estação mais próxima".
export default function AirQualityCard({ dados, local }) {
  if (!dados) return null;

  const cor = corDaCategoria(dados.categoria);
  const poluentes = dados.poluentes || {};

  // Monta a lista de poluentes efetivamente medidos.
  const medidos = Object.entries(poluentes).filter(
    ([, valor]) => valor !== null && valor !== undefined
  );

  return (
    <View style={styles.card}>
      {/* Faixa de categoria */}
      <View style={[styles.badge, { backgroundColor: cor }]}>
        <Text style={styles.badgeText}>{dados.categoria || "Sem dados"}</Text>
      </View>

      <Text style={styles.cidade}>{local || dados.cidade || "Sua localização"}</Text>
      {dados.estacao || dados.cidade ? (
        <Text style={styles.estacao}>
          Estação mais próxima: {dados.estacao || dados.cidade}
        </Text>
      ) : null}

      {/* Índice geral */}
      <View style={styles.indiceBox}>
        <Text style={[styles.indiceValor, { color: cor }]}>
          {dados.indice_geral ?? "--"}
        </Text>
        <Text style={styles.indiceLabel}>Índice IQAr</Text>
      </View>

      {/* Interpretação da IA */}
      {dados.interpretacao ? (
        <View style={styles.iaBox}>
          <Text style={styles.iaTitulo}>🌬️ Como está o ar</Text>
          <Text style={styles.iaTexto}>{dados.interpretacao}</Text>
        </View>
      ) : null}

      {/* Recomendação da IA */}
      {dados.recomendacao ? (
        <View style={styles.iaBox}>
          <Text style={styles.iaTitulo}>💡 Recomendação</Text>
          <Text style={styles.iaTexto}>{dados.recomendacao}</Text>
        </View>
      ) : null}

      {/* Poluentes */}
      {medidos.length > 0 ? (
        <View style={styles.poluentesBox}>
          <Text style={styles.poluentesTitulo}>Poluentes (µg/m³)</Text>
          <View style={styles.poluentesLista}>
            {medidos.map(([nome, valor]) => (
              <View key={nome} style={styles.poluenteItem}>
                <Text style={styles.poluenteNome}>{nome.toUpperCase()}</Text>
                <Text style={styles.poluenteValor}>{valor}</Text>
              </View>
            ))}
          </View>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.surface,
    borderRadius: 16,
    padding: 20,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 999,
    marginBottom: 8,
  },
  badgeText: { color: COLORS.white, fontWeight: "700", fontSize: 13 },
  cidade: { fontSize: 22, fontWeight: "700", color: COLORS.text },
  estacao: { fontSize: 13, color: COLORS.textMuted, marginTop: 2 },
  indiceBox: { alignItems: "center", marginVertical: 12 },
  indiceValor: { fontSize: 56, fontWeight: "800" },
  indiceLabel: { fontSize: 13, color: COLORS.textMuted },
  iaBox: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 12,
    marginTop: 10,
  },
  iaTitulo: { fontSize: 14, fontWeight: "700", color: COLORS.text },
  iaTexto: { fontSize: 14, color: COLORS.text, marginTop: 4, lineHeight: 20 },
  poluentesBox: { marginTop: 14 },
  poluentesTitulo: {
    fontSize: 13,
    fontWeight: "700",
    color: COLORS.textMuted,
    marginBottom: 6,
  },
  poluentesLista: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  poluenteItem: {
    backgroundColor: COLORS.background,
    borderRadius: 10,
    paddingVertical: 6,
    paddingHorizontal: 10,
    minWidth: 64,
    alignItems: "center",
  },
  poluenteNome: { fontSize: 11, color: COLORS.textMuted, fontWeight: "600" },
  poluenteValor: { fontSize: 16, color: COLORS.text, fontWeight: "700" },
});

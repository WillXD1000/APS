// Seletor horizontal de cidade (coordenadas fixas).

import React from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity } from "react-native";

import { CITIES } from "../config/cities";
import { COLORS } from "../config/theme";

export default function CitySelector({ selecionada, onSelecionar }) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {CITIES.map((cidade) => {
        const ativa = selecionada?.id === cidade.id;
        return (
          <TouchableOpacity
            key={cidade.id}
            style={[styles.chip, ativa && styles.chipAtiva]}
            onPress={() => onSelecionar(cidade)}
          >
            <Text style={[styles.texto, ativa && styles.textoAtivo]}>
              {cidade.nome}
            </Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { gap: 8, paddingVertical: 4 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  chipAtiva: { backgroundColor: COLORS.primary, borderColor: COLORS.primary },
  texto: { color: COLORS.text, fontWeight: "600", fontSize: 14 },
  textoAtivo: { color: COLORS.white },
});

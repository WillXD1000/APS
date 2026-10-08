// Seletor de perfil de saúde: um cartão por perfil, com ícone e descrição.

import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

import { PERFIS } from "../config/perfis";
import { COLORS } from "../config/theme";

export default function HealthProfilePicker({ valor, onChange, desabilitado }) {
  return (
    <View style={styles.lista}>
      {PERFIS.map((perfil) => {
        const ativo = valor === perfil.valor;
        return (
          <TouchableOpacity
            key={perfil.valor}
            style={[styles.cartao, ativo && styles.cartaoAtivo]}
            onPress={() => onChange(perfil.valor)}
            disabled={desabilitado}
            accessibilityRole="radio"
            accessibilityState={{ selected: ativo }}
          >
            <View style={[styles.icone, ativo && styles.iconeAtivo]}>
              <Ionicons
                name={perfil.icone}
                size={22}
                color={ativo ? COLORS.white : COLORS.primary}
              />
            </View>
            <View style={styles.textos}>
              <Text style={styles.rotulo}>{perfil.rotulo}</Text>
              <Text style={styles.descricao}>{perfil.descricao}</Text>
            </View>
            <Ionicons
              name={ativo ? "radio-button-on" : "radio-button-off"}
              size={22}
              color={ativo ? COLORS.primary : COLORS.border}
            />
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  lista: { gap: 8, marginTop: 8 },
  cartao: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 12,
  },
  cartaoAtivo: { borderColor: COLORS.primary, backgroundColor: "#EEF7F2" },
  icone: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#EEF7F2",
    alignItems: "center",
    justifyContent: "center",
  },
  iconeAtivo: { backgroundColor: COLORS.primary },
  textos: { flex: 1 },
  rotulo: { fontSize: 15, fontWeight: "700", color: COLORS.text },
  descricao: { fontSize: 13, color: COLORS.textMuted, marginTop: 2, lineHeight: 18 },
});

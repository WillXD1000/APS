// Banner de alerta de qualidade do ar (nível 'atencao' ou 'perigo').

import React from "react";
import { StyleSheet, Text, View } from "react-native";

const ESTILOS_NIVEL = {
  atencao: {
    titulo: "⚠️ Atenção",
    fundo: "#FFF4E5",
    borda: "#F28500",
    texto: "#7A4100",
  },
  perigo: {
    titulo: "🚨 Perigo",
    fundo: "#FDECEA",
    borda: "#D32F2F",
    texto: "#8E1B1B",
  },
};

export function tituloDoAlerta(nivel) {
  return (ESTILOS_NIVEL[nivel] || ESTILOS_NIVEL.atencao).titulo;
}

export default function AlertBanner({ alerta }) {
  if (!alerta) return null;
  const estilo = ESTILOS_NIVEL[alerta.nivel] || ESTILOS_NIVEL.atencao;

  return (
    <View
      style={[styles.banner, { backgroundColor: estilo.fundo, borderColor: estilo.borda }]}
      accessibilityRole="alert"
    >
      <Text style={[styles.titulo, { color: estilo.texto }]}>{estilo.titulo}</Text>
      <Text style={[styles.mensagem, { color: estilo.texto }]}>{alerta.mensagem}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    borderWidth: 1,
    borderLeftWidth: 5,
    borderRadius: 12,
    padding: 14,
    marginTop: 14,
  },
  titulo: { fontSize: 15, fontWeight: "800" },
  mensagem: { fontSize: 14, marginTop: 4, lineHeight: 20 },
});

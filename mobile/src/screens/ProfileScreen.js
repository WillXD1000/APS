// Tela de perfil do usuário + logout.

import React from "react";
import { Alert, StyleSheet, Text, TouchableOpacity, View } from "react-native";

import { useAuth } from "../contexts/AuthContext";
import { COLORS } from "../config/theme";

const PERFIL_ROTULO = {
  geral: "Geral",
  asmatico: "Asmático",
  idoso: "Idoso",
  atleta: "Atleta",
  crianca: "Criança",
};

export default function ProfileScreen() {
  const { usuario, sair } = useAuth();

  function confirmarSaida() {
    Alert.alert("Sair", "Deseja realmente sair da sua conta?", [
      { text: "Cancelar", style: "cancel" },
      { text: "Sair", style: "destructive", onPress: sair },
    ]);
  }

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Perfil</Text>

      <View style={styles.avatar}>
        <Text style={styles.avatarTexto}>
          {usuario?.nome?.charAt(0)?.toUpperCase() || "?"}
        </Text>
      </View>

      <View style={styles.card}>
        <Linha rotulo="Nome" valor={usuario?.nome} />
        <Linha rotulo="E-mail" valor={usuario?.email} />
        <Linha
          rotulo="Perfil de saúde"
          valor={PERFIL_ROTULO[usuario?.perfil_saude] || usuario?.perfil_saude}
        />
      </View>

      <TouchableOpacity style={styles.botaoSair} onPress={confirmarSaida}>
        <Text style={styles.botaoSairTexto}>Sair da conta</Text>
      </TouchableOpacity>
    </View>
  );
}

function Linha({ rotulo, valor }) {
  return (
    <View style={styles.linha}>
      <Text style={styles.linhaRotulo}>{rotulo}</Text>
      <Text style={styles.linhaValor}>{valor || "--"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  titulo: { fontSize: 28, fontWeight: "800", color: COLORS.text },
  avatar: {
    alignSelf: "center",
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: COLORS.primary,
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 24,
  },
  avatarTexto: { color: COLORS.white, fontSize: 40, fontWeight: "800" },
  card: {
    backgroundColor: COLORS.surface,
    borderRadius: 14,
    padding: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  linha: {
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: COLORS.border,
  },
  linhaRotulo: { fontSize: 13, color: COLORS.textMuted },
  linhaValor: { fontSize: 16, color: COLORS.text, fontWeight: "600", marginTop: 2 },
  botaoSair: {
    marginTop: 30,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: COLORS.danger,
  },
  botaoSairTexto: { color: COLORS.danger, fontSize: 16, fontWeight: "700" },
});

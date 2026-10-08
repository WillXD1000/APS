// Tela de perfil: dados do usuário, troca do perfil de saúde e logout.

import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import HealthProfilePicker from "../components/HealthProfilePicker";
import { extrairErro } from "../api/client";
import { rotuloDoPerfil } from "../config/perfis";
import { COLORS } from "../config/theme";
import { useAuth } from "../contexts/AuthContext";

export default function ProfileScreen() {
  const { usuario, sair, atualizarPerfil } = useAuth();
  const [perfil, setPerfil] = useState(usuario?.perfil_saude || "geral");
  const [salvando, setSalvando] = useState(false);

  // Mantém a seleção alinhada com a sessão (ex.: após salvar).
  useEffect(() => {
    if (usuario?.perfil_saude) setPerfil(usuario.perfil_saude);
  }, [usuario?.perfil_saude]);

  const alterado = perfil !== usuario?.perfil_saude;

  async function salvarPerfil() {
    setSalvando(true);
    try {
      await atualizarPerfil(perfil);
      Alert.alert(
        "Perfil atualizado",
        `Seu perfil agora é ${rotuloDoPerfil(perfil)}. As próximas recomendações e alertas vão considerar essa escolha.`
      );
    } catch (error) {
      Alert.alert("Erro ao salvar", extrairErro(error));
    } finally {
      setSalvando(false);
    }
  }

  function confirmarSaida() {
    Alert.alert("Sair", "Deseja realmente sair da sua conta?", [
      { text: "Cancelar", style: "cancel" },
      { text: "Sair", style: "destructive", onPress: sair },
    ]);
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.titulo}>Perfil</Text>

      <View style={styles.avatar}>
        <Text style={styles.avatarTexto}>
          {usuario?.nome?.charAt(0)?.toUpperCase() || "?"}
        </Text>
      </View>

      <View style={styles.card}>
        <Linha rotulo="Nome" valor={usuario?.nome} />
        <Linha rotulo="E-mail" valor={usuario?.email} />
        <Linha rotulo="Perfil de saúde" valor={rotuloDoPerfil(usuario?.perfil_saude)} />
      </View>

      <Text style={styles.secaoTitulo}>Perfil de saúde</Text>
      <Text style={styles.secaoAjuda}>
        Ele personaliza as recomendações da IA e define quando você recebe alertas.
      </Text>
      <HealthProfilePicker valor={perfil} onChange={setPerfil} desabilitado={salvando} />

      <TouchableOpacity
        style={[styles.botaoSalvar, (!alterado || salvando) && styles.botaoDesabilitado]}
        onPress={salvarPerfil}
        disabled={!alterado || salvando}
      >
        {salvando ? (
          <ActivityIndicator color={COLORS.white} />
        ) : (
          <Text style={styles.botaoSalvarTexto}>
            {alterado ? "Salvar perfil" : "Perfil salvo"}
          </Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity style={styles.botaoSair} onPress={confirmarSaida}>
        <Text style={styles.botaoSairTexto}>Sair da conta</Text>
      </TouchableOpacity>
    </ScrollView>
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
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { paddingTop: 60, paddingHorizontal: 20, paddingBottom: 30 },
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
  secaoTitulo: {
    fontSize: 18,
    fontWeight: "800",
    color: COLORS.text,
    marginTop: 24,
  },
  secaoAjuda: { fontSize: 13, color: COLORS.textMuted, marginTop: 4 },
  botaoSalvar: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 16,
  },
  botaoDesabilitado: { opacity: 0.5 },
  botaoSalvarTexto: { color: COLORS.white, fontSize: 16, fontWeight: "700" },
  botaoSair: {
    marginTop: 14,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: COLORS.danger,
  },
  botaoSairTexto: { color: COLORS.danger, fontSize: 16, fontWeight: "700" },
});

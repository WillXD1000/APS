// Tela de cadastro.

import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
} from "react-native";

import HealthProfilePicker from "../components/HealthProfilePicker";
import { useAuth } from "../contexts/AuthContext";
import { extrairErro } from "../api/client";
import { COLORS } from "../config/theme";

export default function RegisterScreen({ navigation }) {
  const { cadastrar } = useAuth();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState("geral");
  const [carregando, setCarregando] = useState(false);

  async function handleCadastro() {
    if (!nome || !email || !senha) {
      Alert.alert("Atenção", "Preencha todos os campos.");
      return;
    }
    if (senha.length < 6) {
      Alert.alert("Atenção", "A senha deve ter ao menos 6 caracteres.");
      return;
    }
    setCarregando(true);
    try {
      await cadastrar(nome.trim(), email.trim(), senha, perfil);
    } catch (error) {
      Alert.alert("Erro ao cadastrar", extrairErro(error));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior="padding"
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.titulo}>Criar conta</Text>

        <Text style={styles.label}>Nome</Text>
        <TextInput
          style={styles.input}
          placeholder="Seu nome"
          value={nome}
          onChangeText={setNome}
        />

        <Text style={styles.label}>E-mail</Text>
        <TextInput
          style={styles.input}
          placeholder="seu@email.com"
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />

        <Text style={styles.label}>Senha</Text>
        <TextInput
          style={styles.input}
          placeholder="mínimo 6 caracteres"
          secureTextEntry
          value={senha}
          onChangeText={setSenha}
        />

        <Text style={styles.label}>Perfil de saúde</Text>
        <Text style={styles.ajuda}>
          Escolha o que melhor descreve você. Dá para mudar depois na aba Perfil.
        </Text>
        <HealthProfilePicker valor={perfil} onChange={setPerfil} />

        <TouchableOpacity
          style={styles.botao}
          onPress={handleCadastro}
          disabled={carregando}
        >
          {carregando ? (
            <ActivityIndicator color={COLORS.white} />
          ) : (
            <Text style={styles.botaoTexto}>Cadastrar</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.link}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.linkTexto}>
            Já tem conta? <Text style={styles.linkDestaque}>Entrar</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scroll: { padding: 24, paddingTop: 60 },
  titulo: {
    fontSize: 28,
    fontWeight: "800",
    color: COLORS.text,
    marginBottom: 16,
  },
  label: { fontSize: 14, color: COLORS.text, fontWeight: "600", marginTop: 12 },
  input: {
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    marginTop: 4,
  },
  ajuda: { fontSize: 13, color: COLORS.textMuted, marginTop: 2 },
  botao: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center",
    marginTop: 24,
  },
  botaoTexto: { color: COLORS.white, fontSize: 16, fontWeight: "700" },
  link: { alignItems: "center", marginTop: 18 },
  linkTexto: { color: COLORS.textMuted, fontSize: 14 },
  linkDestaque: { color: COLORS.primary, fontWeight: "700" },
});

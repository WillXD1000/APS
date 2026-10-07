// Tela principal: seleciona a cidade e consulta a qualidade do ar.

import React, { useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import AirQualityCard from "../components/AirQualityCard";
import CitySelector from "../components/CitySelector";
import { consultarQualidadeAr } from "../api/airQuality";
import { extrairErro } from "../api/client";
import { DEFAULT_CITY } from "../config/cities";
import { COLORS } from "../config/theme";
import { useAuth } from "../contexts/AuthContext";

export default function HomeScreen() {
  const { usuario } = useAuth();
  const [cidade, setCidade] = useState(DEFAULT_CITY);
  const [dados, setDados] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  async function consultar(cidadeAlvo) {
    const alvo = cidadeAlvo || cidade;
    setCarregando(true);
    setErro(null);
    try {
      const resposta = await consultarQualidadeAr(alvo.lat, alvo.lon);
      setDados(resposta);
    } catch (error) {
      setErro(extrairErro(error));
      setDados(null);
    } finally {
      setCarregando(false);
    }
  }

  function selecionarCidade(nova) {
    setCidade(nova);
    consultar(nova);
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={carregando} onRefresh={() => consultar()} />
      }
    >
      <Text style={styles.saudacao}>Olá, {usuario?.nome?.split(" ")[0]} 👋</Text>
      <Text style={styles.titulo}>Qualidade do ar</Text>

      <Text style={styles.secao}>Escolha a cidade</Text>
      <CitySelector selecionada={cidade} onSelecionar={selecionarCidade} />

      <TouchableOpacity
        style={styles.botao}
        onPress={() => consultar()}
        disabled={carregando}
      >
        {carregando ? (
          <ActivityIndicator color={COLORS.white} />
        ) : (
          <Text style={styles.botaoTexto}>Consultar {cidade.nome}</Text>
        )}
      </TouchableOpacity>

      {erro ? (
        <View style={styles.erroBox}>
          <Text style={styles.erroTexto}>{erro}</Text>
        </View>
      ) : null}

      {dados ? <AirQualityCard dados={dados} /> : null}

      {!dados && !erro && !carregando ? (
        <View style={styles.vazio}>
          <Text style={styles.vazioTexto}>
            Selecione uma cidade e toque em consultar para ver a qualidade do ar.
          </Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: 20, paddingTop: 60 },
  saudacao: { fontSize: 15, color: COLORS.textMuted },
  titulo: {
    fontSize: 28,
    fontWeight: "800",
    color: COLORS.text,
    marginBottom: 16,
  },
  secao: {
    fontSize: 14,
    fontWeight: "700",
    color: COLORS.textMuted,
    marginBottom: 8,
  },
  botao: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 14,
  },
  botaoTexto: { color: COLORS.white, fontSize: 16, fontWeight: "700" },
  erroBox: {
    backgroundColor: "#FDECEA",
    borderRadius: 12,
    padding: 14,
    marginTop: 14,
    borderWidth: 1,
    borderColor: "#F5C6C2",
  },
  erroTexto: { color: COLORS.danger, fontSize: 14 },
  vazio: { marginTop: 30, alignItems: "center" },
  vazioTexto: {
    color: COLORS.textMuted,
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
});

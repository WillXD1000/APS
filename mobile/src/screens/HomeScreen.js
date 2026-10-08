// Tela principal: usa a localização do celular para consultar a qualidade do ar.

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  AppState,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import AirQualityCard from "../components/AirQualityCard";
import AlertBanner, { tituloDoAlerta } from "../components/AlertBanner";
import { consultarQualidadeAr } from "../api/airQuality";
import { extrairErro } from "../api/client";
import { COLORS } from "../config/theme";
import { useAuth } from "../contexts/AuthContext";
import {
  abrirConfiguracoes,
  LocalizacaoError,
  obterLocalizacao,
} from "../services/localizacao";

// Erros que podem ser resolvidos fora do app (configurações): ao voltar para o
// app, a tela tenta de novo sozinha.
const ERROS_RESOLVIDOS_FORA = ["permissao_bloqueada", "gps_desligado"];

const TEXTO_ETAPA = {
  localizando: "Obtendo sua localização...",
  consultando: "Consultando a qualidade do ar...",
};

export default function HomeScreen() {
  const { usuario } = useAuth();
  const [etapa, setEtapa] = useState("localizando"); // localizando | consultando | pronto
  const [local, setLocal] = useState(null);
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState(null); // { tipo, mensagem }

  const ocupadoRef = useRef(false);
  const erroRef = useRef(null);
  erroRef.current = erro;

  const atualizar = useCallback(async () => {
    if (ocupadoRef.current) return;
    ocupadoRef.current = true;
    setErro(null);
    setEtapa("localizando");
    try {
      const posicao = await obterLocalizacao();
      setLocal(posicao.nomeLocal);
      setEtapa("consultando");

      const resposta = await consultarQualidadeAr(posicao.lat, posicao.lon);
      setDados(resposta);
      // Popup apenas para alertas novos (o banner aparece sempre).
      if (resposta.alerta?.novo) {
        Alert.alert(tituloDoAlerta(resposta.alerta.nivel), resposta.alerta.mensagem);
      }
    } catch (error) {
      setDados(null);
      if (error instanceof LocalizacaoError) {
        setErro({ tipo: error.tipo, mensagem: error.message });
      } else {
        setErro({ tipo: "api", mensagem: extrairErro(error) });
      }
    } finally {
      setEtapa("pronto");
      ocupadoRef.current = false;
    }
  }, []);

  // Consulta automaticamente ao abrir a tela.
  useEffect(() => {
    atualizar();
  }, [atualizar]);

  // Ao voltar das configurações do celular, tenta de novo se o problema era
  // a permissão bloqueada ou o GPS desligado.
  useEffect(() => {
    const assinatura = AppState.addEventListener("change", (estado) => {
      if (estado === "active" && ERROS_RESOLVIDOS_FORA.includes(erroRef.current?.tipo)) {
        atualizar();
      }
    });
    return () => assinatura.remove();
  }, [atualizar]);

  const ocupado = etapa !== "pronto";

  function botaoDoErro() {
    if (!erro) return null;
    if (erro.tipo === "permissao_bloqueada") {
      return { texto: "Abrir configurações", acao: abrirConfiguracoes };
    }
    if (erro.tipo === "permissao_negada") {
      return { texto: "Permitir localização", acao: atualizar };
    }
    return { texto: "Tentar novamente", acao: atualizar };
  }
  const botaoErro = botaoDoErro();

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={false} onRefresh={atualizar} />
      }
    >
      <Text style={styles.saudacao}>Olá, {usuario?.nome?.split(" ")[0]} 👋</Text>
      <Text style={styles.titulo}>Qualidade do ar</Text>

      <View style={styles.localLinha}>
        <Text style={styles.localTexto} numberOfLines={1}>
          📍 {local ? `Você está em ${local}` : "Sua localização atual"}
        </Text>
        <TouchableOpacity
          style={[styles.botaoAtualizar, ocupado && styles.botaoDesabilitado]}
          onPress={atualizar}
          disabled={ocupado}
        >
          <Text style={styles.botaoAtualizarTexto}>Atualizar</Text>
        </TouchableOpacity>
      </View>

      {ocupado ? (
        <View style={styles.carregando}>
          <ActivityIndicator color={COLORS.primary} />
          <Text style={styles.carregandoTexto}>{TEXTO_ETAPA[etapa]}</Text>
        </View>
      ) : null}

      {erro && !ocupado ? (
        <View style={styles.erroBox}>
          <Text style={styles.erroTexto}>{erro.mensagem}</Text>
          {botaoErro ? (
            <TouchableOpacity style={styles.botaoErro} onPress={botaoErro.acao}>
              <Text style={styles.botaoErroTexto}>{botaoErro.texto}</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      ) : null}

      {dados?.alerta ? <AlertBanner alerta={dados.alerta} /> : null}

      {dados ? <AirQualityCard dados={dados} local={local} /> : null}
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
    marginBottom: 12,
  },
  localLinha: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    paddingVertical: 10,
    paddingLeft: 14,
    paddingRight: 10,
  },
  localTexto: { flex: 1, fontSize: 14, color: COLORS.text, fontWeight: "600" },
  botaoAtualizar: {
    backgroundColor: COLORS.primary,
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  botaoDesabilitado: { opacity: 0.5 },
  botaoAtualizarTexto: { color: COLORS.white, fontWeight: "700", fontSize: 13 },
  carregando: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginTop: 16,
  },
  carregandoTexto: { color: COLORS.textMuted, fontSize: 14 },
  erroBox: {
    backgroundColor: "#FDECEA",
    borderRadius: 12,
    padding: 14,
    marginTop: 14,
    borderWidth: 1,
    borderColor: "#F5C6C2",
  },
  erroTexto: { color: COLORS.danger, fontSize: 14, lineHeight: 20 },
  botaoErro: {
    alignSelf: "flex-start",
    marginTop: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: COLORS.danger,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  botaoErroTexto: { color: COLORS.danger, fontWeight: "700" },
});

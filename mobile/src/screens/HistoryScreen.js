// Tela de histórico: gráfico dos últimos dias, alertas recentes e consultas.

import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from "react-native";

import IndexChart from "../components/IndexChart";
import { historico, relatorio } from "../api/airQuality";
import { listarAlertas } from "../api/alerts";
import { extrairErro } from "../api/client";
import { COLORS, corDaCategoria } from "../config/theme";

const COR_NIVEL = { atencao: "#F28500", perigo: "#D32F2F" };

function formatarData(iso) {
  try {
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function HistoryScreen() {
  const [itens, setItens] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [rel, setRel] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [atualizando, setAtualizando] = useState(false);
  const [erro, setErro] = useState(null);

  const carregar = useCallback(async () => {
    setErro(null);
    try {
      const [medicoes, listaAlertas, dadosRelatorio] = await Promise.all([
        historico(50),
        listarAlertas(5),
        relatorio(7),
      ]);
      setItens(medicoes);
      setAlertas(listaAlertas);
      setRel(dadosRelatorio);
    } catch (error) {
      setErro(extrairErro(error));
    } finally {
      setCarregando(false);
      setAtualizando(false);
    }
  }, []);

  // Recarrega sempre que a tela ganha foco.
  useFocusEffect(
    useCallback(() => {
      carregar();
    }, [carregar])
  );

  function renderItem({ item }) {
    const cor = corDaCategoria(item.categoria);
    return (
      <View style={styles.item}>
        <View style={[styles.indicador, { backgroundColor: cor }]} />
        <View style={styles.itemInfo}>
          <Text style={styles.itemCidade}>{item.cidade || "Localização"}</Text>
          <Text style={styles.itemData}>{formatarData(item.coletado_em)}</Text>
        </View>
        <View style={styles.itemDireita}>
          <Text style={[styles.itemIndice, { color: cor }]}>
            {item.indice_geral ?? "--"}
          </Text>
          <Text style={styles.itemCategoria}>{item.categoria || ""}</Text>
        </View>
      </View>
    );
  }

  const cabecalho = (
    <View>
      <Text style={styles.titulo}>Histórico</Text>
      {erro ? <Text style={styles.erro}>{erro}</Text> : null}

      <IndexChart relatorio={rel} />

      {alertas.length > 0 ? (
        <View style={styles.secao}>
          <Text style={styles.secaoTitulo}>Alertas recentes</Text>
          {alertas.map((a) => (
            <View key={a.id} style={styles.alerta}>
              <View
                style={[
                  styles.alertaPonto,
                  { backgroundColor: COR_NIVEL[a.nivel] || COLORS.textMuted },
                ]}
              />
              <View style={styles.alertaTextos}>
                <Text style={styles.alertaMensagem}>{a.mensagem}</Text>
                <Text style={styles.itemData}>{formatarData(a.enviado_em)}</Text>
              </View>
            </View>
          ))}
        </View>
      ) : null}

      <Text style={styles.secaoTitulo}>Consultas</Text>
    </View>
  );

  if (carregando) {
    return (
      <View style={styles.centro}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <FlatList
      style={styles.container}
      data={itens}
      keyExtractor={(item) => String(item.id)}
      renderItem={renderItem}
      ListHeaderComponent={cabecalho}
      ListEmptyComponent={
        erro ? null : (
          <Text style={styles.vazio}>
            Nenhuma consulta ainda. Faça uma consulta na aba Início.
          </Text>
        )
      }
      contentContainerStyle={styles.lista}
      refreshControl={
        <RefreshControl
          refreshing={atualizando}
          onRefresh={() => {
            setAtualizando(true);
            carregar();
          }}
        />
      }
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  centro: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: COLORS.background,
  },
  lista: { paddingHorizontal: 20, paddingTop: 60, paddingBottom: 20 },
  titulo: {
    fontSize: 28,
    fontWeight: "800",
    color: COLORS.text,
    marginBottom: 12,
  },
  secao: { marginBottom: 16 },
  secaoTitulo: {
    fontSize: 14,
    fontWeight: "700",
    color: COLORS.textMuted,
    marginBottom: 8,
  },
  alerta: {
    flexDirection: "row",
    gap: 10,
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  alertaPonto: { width: 10, height: 10, borderRadius: 5, marginTop: 5 },
  alertaTextos: { flex: 1 },
  alertaMensagem: { fontSize: 14, color: COLORS.text, lineHeight: 20 },
  item: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  indicador: { width: 10, height: 40, borderRadius: 5, marginRight: 12 },
  itemInfo: { flex: 1 },
  itemCidade: { fontSize: 16, fontWeight: "700", color: COLORS.text },
  itemData: { fontSize: 13, color: COLORS.textMuted, marginTop: 2 },
  itemDireita: { alignItems: "flex-end" },
  itemIndice: { fontSize: 22, fontWeight: "800" },
  itemCategoria: { fontSize: 12, color: COLORS.textMuted },
  erro: { color: COLORS.danger, marginBottom: 12 },
  vazio: { color: COLORS.textMuted, textAlign: "center", marginTop: 20 },
});

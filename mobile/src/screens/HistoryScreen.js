// Tela de histórico de medições.

import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { historico } from "../api/airQuality";
import { extrairErro } from "../api/client";
import { COLORS, corDaCategoria } from "../config/theme";

export default function HistoryScreen() {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const dados = await historico(50);
      setItens(dados);
    } catch (error) {
      setErro(extrairErro(error));
    } finally {
      setCarregando(false);
    }
  }, []);

  // Recarrega sempre que a tela ganha foco.
  useFocusEffect(
    useCallback(() => {
      carregar();
    }, [carregar])
  );

  function formatarData(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  }

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

  if (carregando) {
    return (
      <View style={styles.centro}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Histórico</Text>
      {erro ? (
        <Text style={styles.erro}>{erro}</Text>
      ) : itens.length === 0 ? (
        <Text style={styles.vazio}>
          Nenhuma consulta ainda. Faça uma consulta na aba Início.
        </Text>
      ) : (
        <FlatList
          data={itens}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
          contentContainerStyle={styles.lista}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background, paddingTop: 60 },
  centro: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: COLORS.background,
  },
  titulo: {
    fontSize: 28,
    fontWeight: "800",
    color: COLORS.text,
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  lista: { paddingHorizontal: 20, paddingBottom: 20 },
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
  erro: { color: COLORS.danger, paddingHorizontal: 20 },
  vazio: {
    color: COLORS.textMuted,
    paddingHorizontal: 20,
    textAlign: "center",
    marginTop: 20,
  },
});

// Tela do chatbot ambiental.

import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Keyboard,
  KeyboardAvoidingView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { enviarPergunta } from "../api/chat";
import { extrairErro } from "../api/client";
import { COLORS } from "../config/theme";

export default function ChatScreen() {
  const [mensagens, setMensagens] = useState([
    {
      id: "intro",
      autor: "bot",
      texto:
        "Olá! Sou seu assistente de qualidade do ar. Pergunte, por exemplo: " +
        '"posso correr ao ar livre hoje?"',
    },
  ]);
  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const listaRef = useRef(null);

  // Ao abrir o teclado, rola até a última mensagem para ela não ficar escondida.
  useEffect(() => {
    const assinatura = Keyboard.addListener("keyboardDidShow", () => {
      setTimeout(() => listaRef.current?.scrollToEnd({ animated: true }), 50);
    });
    return () => assinatura.remove();
  }, []);

  async function enviar() {
    const pergunta = texto.trim();
    if (!pergunta || enviando) return;

    const msgUsuario = { id: `u${Date.now()}`, autor: "user", texto: pergunta };
    setMensagens((prev) => [...prev, msgUsuario]);
    setTexto("");
    setEnviando(true);

    try {
      const resposta = await enviarPergunta(pergunta);
      setMensagens((prev) => [
        ...prev,
        { id: `b${Date.now()}`, autor: "bot", texto: resposta.resposta },
      ]);
    } catch (error) {
      setMensagens((prev) => [
        ...prev,
        { id: `e${Date.now()}`, autor: "bot", texto: extrairErro(error) },
      ]);
    } finally {
      setEnviando(false);
      setTimeout(() => listaRef.current?.scrollToEnd({ animated: true }), 100);
    }
  }

  function renderItem({ item }) {
    const ehUsuario = item.autor === "user";
    return (
      <View
        style={[
          styles.bolha,
          ehUsuario ? styles.bolhaUsuario : styles.bolhaBot,
        ]}
      >
        <Text style={ehUsuario ? styles.textoUsuario : styles.textoBot}>
          {item.texto}
        </Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      // "padding" também no Android: com o modo edge-to-edge (padrão desde o
      // SDK 53) a janela não encolhe quando o teclado abre, então a própria
      // tela precisa ganhar espaço embaixo para o campo de texto subir.
      behavior="padding"
    >
      <FlatList
        ref={listaRef}
        data={mensagens}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.lista}
        onContentSizeChange={() =>
          listaRef.current?.scrollToEnd({ animated: true })
        }
      />

      {enviando ? (
        <View style={styles.digitando}>
          <ActivityIndicator size="small" color={COLORS.primary} />
          <Text style={styles.digitandoTexto}>Pensando...</Text>
        </View>
      ) : null}

      <View style={styles.inputArea}>
        <TextInput
          style={styles.input}
          placeholder="Digite sua pergunta..."
          value={texto}
          onChangeText={setTexto}
          multiline
        />
        <TouchableOpacity
          style={styles.enviarBtn}
          onPress={enviar}
          disabled={enviando}
        >
          <Text style={styles.enviarTexto}>➤</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  lista: { padding: 16, paddingTop: 50 },
  bolha: {
    maxWidth: "82%",
    padding: 12,
    borderRadius: 16,
    marginVertical: 5,
  },
  bolhaUsuario: {
    alignSelf: "flex-end",
    backgroundColor: COLORS.primary,
    borderBottomRightRadius: 4,
  },
  bolhaBot: {
    alignSelf: "flex-start",
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderBottomLeftRadius: 4,
  },
  textoUsuario: { color: COLORS.white, fontSize: 15, lineHeight: 21 },
  textoBot: { color: COLORS.text, fontSize: 15, lineHeight: 21 },
  digitando: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 16,
    paddingBottom: 4,
  },
  digitandoTexto: { color: COLORS.textMuted, fontSize: 13 },
  inputArea: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 10,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    backgroundColor: COLORS.surface,
  },
  input: {
    flex: 1,
    backgroundColor: COLORS.background,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 100,
  },
  enviarBtn: {
    backgroundColor: COLORS.primary,
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  enviarTexto: { color: COLORS.white, fontSize: 18 },
});

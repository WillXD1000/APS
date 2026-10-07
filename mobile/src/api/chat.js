// Chamadas do chatbot ambiental ao backend.

import client from "./client";

export async function enviarPergunta(pergunta) {
  const { data } = await client.post("/chat", { pergunta });
  return data; // { pergunta, resposta }
}

export async function historicoChat(limite = 50) {
  const { data } = await client.get("/chat/history", { params: { limite } });
  return data; // ConversaOut[]
}

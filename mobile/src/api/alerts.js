// Chamadas de alertas ao backend.

import client from "./client";

export async function listarAlertas(limite = 20) {
  const { data } = await client.get("/alerts", { params: { limite } });
  return data; // AlertaOut[]
}

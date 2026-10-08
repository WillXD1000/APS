// Chamadas de qualidade do ar ao backend.

import client from "./client";

export async function consultarQualidadeAr(lat, lon) {
  const { data } = await client.get("/air-quality", {
    params: { lat, lon },
  });
  return data; // QualidadeArResponse
}

export async function historico(limite = 50) {
  const { data } = await client.get("/history", { params: { limite } });
  return data; // MedicaoOut[]
}

// Chamadas de autenticação ao backend.

import client from "./client";

export async function login(email, senha) {
  const { data } = await client.post("/auth/login", { email, senha });
  return data; // { access_token, token_type, usuario }
}

export async function register(nome, email, senha, perfilSaude) {
  const { data } = await client.post("/auth/register", {
    nome,
    email,
    senha,
    perfil_saude: perfilSaude,
  });
  return data; // UsuarioOut
}

export async function me() {
  const { data } = await client.get("/auth/me");
  return data; // UsuarioOut
}

export async function atualizarPerfil(perfilSaude) {
  const { data } = await client.put("/auth/me/perfil", {
    perfil_saude: perfilSaude,
  });
  return data; // UsuarioOut
}

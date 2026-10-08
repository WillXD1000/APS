// Contexto global de autenticação.
// Guarda o usuário logado e o token, e expõe funções de login/logout.

import React, { createContext, useContext, useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

import client, { TOKEN_KEY } from "../api/client";
import * as authApi from "../api/auth";

const USER_KEY = "@airia:user";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  // Ao abrir o app, tenta restaurar a sessão salva.
  useEffect(() => {
    (async () => {
      try {
        const [token, userJson] = await Promise.all([
          AsyncStorage.getItem(TOKEN_KEY),
          AsyncStorage.getItem(USER_KEY),
        ]);
        if (token && userJson) {
          setUsuario(JSON.parse(userJson));
        }
      } catch (e) {
        // Ignora falhas de leitura do storage.
      } finally {
        setCarregando(false);
      }
    })();
  }, []);

  async function entrar(email, senha) {
    const dados = await authApi.login(email, senha);
    await AsyncStorage.setItem(TOKEN_KEY, dados.access_token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(dados.usuario));
    setUsuario(dados.usuario);
    return dados.usuario;
  }

  async function cadastrar(nome, email, senha, perfilSaude) {
    await authApi.register(nome, email, senha, perfilSaude);
    // Após cadastrar, já faz login automaticamente.
    return entrar(email, senha);
  }

  async function sair() {
    await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
    setUsuario(null);
  }

  // Altera o perfil de saúde no backend e atualiza a sessão salva.
  async function atualizarPerfil(perfilSaude) {
    const atualizado = await authApi.atualizarPerfil(perfilSaude);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(atualizado));
    setUsuario(atualizado);
    return atualizado;
  }

  return (
    <AuthContext.Provider
      value={{ usuario, carregando, entrar, cadastrar, sair, atualizarPerfil }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
}

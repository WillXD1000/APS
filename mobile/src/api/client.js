// Cliente HTTP central (axios) para falar com o backend AirIA.
// Injeta o token JWT automaticamente em todas as requisições.

import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Lê a URL do backend das variáveis de ambiente do Expo.
const API_URL =
  process.env.EXPO_PUBLIC_API_URL || "http://192.168.0.10:8000";

export const TOKEN_KEY = "@airia:token";

const client = axios.create({
  baseURL: API_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// Interceptor: adiciona o token (quando houver) no cabeçalho Authorization.
client.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Converte erros do axios em mensagens amigáveis.
export function extrairErro(error) {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    // FastAPI pode retornar string ou lista de erros de validação.
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  }
  if (error.code === "ECONNABORTED") {
    return "Tempo de conexão esgotado. Verifique se o servidor está acessível.";
  }
  if (error.message === "Network Error") {
    return "Não foi possível conectar ao servidor. Confira a URL da API e a rede.";
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

export { API_URL };
export default client;

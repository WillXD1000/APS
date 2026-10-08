// Localização do celular (expo-location).
//
// Privacidade: as coordenadas enviadas ao backend são arredondadas para 2 casas
// decimais (cerca de 1 km). Isso não altera o resultado, porque a estação é
// buscada num raio de 25 km, e evita gravar no histórico a posição exata do
// usuário. O nome do lugar é obtido no próprio aparelho, com a posição precisa.

import * as Location from "expo-location";
import { Linking } from "react-native";

const CASAS_DECIMAIS = 2;
const TEMPO_MAXIMO_GPS_MS = 15000;
const TEMPO_MAXIMO_ENDERECO_MS = 5000;
// Posição recente aceita sem esperar o GPS (deixa a abertura da tela rápida).
const IDADE_POSICAO_RECENTE_MS = 2 * 60 * 1000;
// Se o GPS não responder, aceita uma posição antiga de até 1 hora.
const IDADE_POSICAO_RESERVA_MS = 60 * 60 * 1000;

// Erro com um 'tipo' que a tela usa para decidir qual botão mostrar.
// Tipos: permissao_negada, permissao_bloqueada, gps_desligado, indisponivel.
export class LocalizacaoError extends Error {
  constructor(tipo, mensagem) {
    super(mensagem);
    this.tipo = tipo;
  }
}

export function arredondar(valor, casas = CASAS_DECIMAIS) {
  const fator = 10 ** casas;
  return Math.round(valor * fator) / fator;
}

function comTempoLimite(promessa, ms) {
  return Promise.race([
    promessa,
    new Promise((_, rejeitar) =>
      setTimeout(() => rejeitar(new Error("tempo esgotado")), ms)
    ),
  ]);
}

async function garantirPermissao() {
  let { status, canAskAgain } = await Location.getForegroundPermissionsAsync();
  if (status === "granted") return;

  if (canAskAgain) {
    ({ status, canAskAgain } = await Location.requestForegroundPermissionsAsync());
    if (status === "granted") return;
  }

  if (canAskAgain) {
    throw new LocalizacaoError(
      "permissao_negada",
      "O AirIA precisa da sua localização para mostrar a qualidade do ar perto de você."
    );
  }
  throw new LocalizacaoError(
    "permissao_bloqueada",
    "A permissão de localização foi negada. Libere-a nas configurações do celular para continuar."
  );
}

async function lerPosicao() {
  const ligado = await Location.hasServicesEnabledAsync();
  if (!ligado) {
    throw new LocalizacaoError(
      "gps_desligado",
      "A localização do celular está desligada. Ative-a e toque em Tentar novamente."
    );
  }

  const recente = await Location.getLastKnownPositionAsync({
    maxAge: IDADE_POSICAO_RECENTE_MS,
  });
  if (recente) return recente;

  try {
    return await comTempoLimite(
      Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }),
      TEMPO_MAXIMO_GPS_MS
    );
  } catch {
    const reserva = await Location.getLastKnownPositionAsync({
      maxAge: IDADE_POSICAO_RESERVA_MS,
    });
    if (reserva) return reserva;
    throw new LocalizacaoError(
      "indisponivel",
      "Não foi possível obter sua localização. Tente novamente, de preferência perto de uma janela ou ao ar livre."
    );
  }
}

// Nome do lugar ("Vila Mariana, São Paulo"). Se falhar, retorna null e a tela
// segue funcionando sem ele.
async function nomeDoLugar(latitude, longitude) {
  try {
    const enderecos = await comTempoLimite(
      Location.reverseGeocodeAsync({ latitude, longitude }),
      TEMPO_MAXIMO_ENDERECO_MS
    );
    const e = enderecos?.[0];
    if (!e) return null;
    const partes = [e.district, e.city || e.subregion || e.region].filter(Boolean);
    return [...new Set(partes)].join(", ") || null;
  } catch {
    return null;
  }
}

// Retorna { lat, lon, nomeLocal }, com lat/lon já arredondadas para envio.
export async function obterLocalizacao() {
  await garantirPermissao();
  const posicao = await lerPosicao();
  const { latitude, longitude } = posicao.coords;
  return {
    lat: arredondar(latitude),
    lon: arredondar(longitude),
    nomeLocal: await nomeDoLugar(latitude, longitude),
  };
}

export function abrirConfiguracoes() {
  return Linking.openSettings();
}

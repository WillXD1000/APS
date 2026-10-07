// Lista de cidades com coordenadas fixas.
// Usada na seleção manual de localização (sem GPS por enquanto).
// Todas têm boa cobertura de estações na OpenAQ.

export const CITIES = [
  { id: "sp", nome: "São Paulo", lat: -23.55, lon: -46.63 },
  { id: "diadema", nome: "Diadema", lat: -23.69, lon: -46.62 },
  { id: "rj", nome: "Rio de Janeiro", lat: -22.91, lon: -43.2 },
  { id: "bh", nome: "Belo Horizonte", lat: -19.92, lon: -43.94 },
  { id: "curitiba", nome: "Curitiba", lat: -25.43, lon: -49.27 },
  { id: "poa", nome: "Porto Alegre", lat: -30.03, lon: -51.23 },
];

export const DEFAULT_CITY = CITIES[0];

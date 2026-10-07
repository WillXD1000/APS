// Configuração do Metro bundler para o Expo.
// Estende a configuração padrão do Expo (recomendado pela documentação).
// Ter este arquivo explícito evita problemas de resolução do transformer.

const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);

module.exports = config;

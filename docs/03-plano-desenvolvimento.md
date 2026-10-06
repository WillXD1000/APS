# 🗺️ Plano de Desenvolvimento — AirIA

> Roteiro incremental de implementação, organizado em etapas (sprints).

---

## Visão Geral das Etapas

| Etapa | Foco | Entrega |
|---|---|---|
| 0 | Preparação | Ambiente, repositório, chaves de API |
| 1 | Backend base | FastAPI + PostgreSQL + autenticação |
| 2 | Integração OpenAQ | Consulta de qualidade do ar |
| 3 | Integração Gemini | Interpretação e recomendação por IA |
| 4 | Mobile base | App React Native + telas principais |
| 5 | Funcionalidades IA no app | Chatbot, recomendações, alertas |
| 6 | Relatórios e refinamentos | Gráficos, mapa de calor, histórico |
| 7 | Testes, deploy e apresentação | Empacotamento e demonstração |

---

## 🧱 Etapa 0 — Preparação do Ambiente

- [ ] Criar repositório Git (estrutura `backend/` e `mobile/`)
- [ ] Obter chave gratuita da **API do Gemini** (Google AI Studio)
- [ ] Registrar conta na **OpenAQ** (se necessária chave)
- [ ] Instalar PostgreSQL (ou subir via Docker)
- [ ] Definir arquivo `.env` com segredos
- [ ] Configurar ambiente Python (venv) e Node (Expo)

**Entrega:** ambiente de desenvolvimento pronto.

---

## 🔧 Etapa 1 — Backend Base (FastAPI + PostgreSQL)

- [ ] Estrutura do projeto FastAPI (camadas: api / services / repositories / models)
- [ ] Conexão com PostgreSQL (SQLAlchemy + Alembic para migrações)
- [ ] Modelos: `usuarios`, `medicoes`, `alertas`, `conversas`
- [ ] Endpoints de autenticação: `/auth/register`, `/auth/login` (JWT)
- [ ] Hash de senha com bcrypt
- [ ] Documentação automática (Swagger em `/docs`)

**Entrega:** API rodando com cadastro/login e banco conectado.

---

## 🌍 Etapa 2 — Integração com OpenAQ

- [ ] `AirQualityService`: consumir OpenAQ por lat/long
- [ ] Mapear poluentes (PM2.5, PM10, O3, NO2, CO)
- [ ] Calcular o **IQAr** (índice geral + categoria)
- [ ] Endpoint `GET /air-quality?lat=&lon=`
- [ ] Persistir medições no histórico
- [ ] Tratamento de falha (região sem estação → estação mais próxima)

**Entrega:** backend retorna qualidade do ar de qualquer coordenada.

---

## 🤖 Etapa 3 — Integração com Gemini

- [ ] `GeminiService`: cliente da API (SDK `google-genai`)
- [ ] Montagem de prompt estruturado (dados + perfil do usuário)
- [ ] Interpretação em linguagem natural
- [ ] Recomendação personalizada por perfil de saúde
- [ ] Endpoint `POST /chat` (chatbot ambiental)
- [ ] Fallback quando o Gemini estiver indisponível (interpretação por faixas)
- [ ] Cache de respostas por região (economizar cota do free tier)

**Entrega:** respostas de IA integradas à qualidade do ar e ao chatbot.

---

## 📱 Etapa 4 — Mobile Base (React Native)

- [ ] Projeto Expo + navegação (React Navigation)
- [ ] Telas: Login, Cadastro, Home (qualidade do ar), Perfil
- [ ] Serviço HTTP (axios) + armazenamento de token
- [ ] Permissão e captura de **geolocalização**
- [ ] Consumo do endpoint `/air-quality` e exibição dos índices

**Entrega:** app exibindo a qualidade do ar da localização do usuário.

---

## 💬 Etapa 5 — Funcionalidades de IA no App

- [ ] Tela de **recomendação** (texto da IA destacado)
- [ ] Tela de **chatbot** (conversa com histórico)
- [ ] Configuração de **perfil de saúde** (afeta a recomendação)
- [ ] **Notificações push** (Expo Notifications) para alertas
- [ ] Lógica de disparo de alerta quando categoria = ruim/perigo

**Entrega:** chatbot, recomendações personalizadas e alertas funcionando.

---

## 📊 Etapa 6 — Relatórios e Refinamentos

- [ ] Endpoint `GET /report` (agregação do histórico)
- [ ] **Gráficos** no app (evolução dos poluentes no tempo)
- [ ] **Mapa de calor** da poluição por região (opcional)
- [ ] Melhorias de UI/UX e acessibilidade
- [ ] Tratamento de erros amigável no app (offline, falhas)

**Entrega:** relatórios visuais e experiência refinada (pontos de diferencial).

---

## 🚀 Etapa 7 — Testes, Deploy e Apresentação

- [ ] Testes manuais de todos os fluxos
- [ ] (Opcional) Testes automatizados nos serviços principais
- [ ] **Dockerizar** backend + PostgreSQL (`docker-compose`)
- [ ] Deploy do backend (Render / Railway / GCP)
- [ ] Gerar build do app (Expo)
- [ ] Preparar **roteiro de demonstração** para a banca
- [ ] Revisar documentação final

**Entrega:** sistema completo, publicado e pronto para apresentação.

---

## 📌 Observações sobre o Gemini (free tier)

- Usar o modelo **Flash** (gratuito, com cota diária) para desenvolvimento;
- Implementar **cache por região** para não estourar o limite de requisições;
- Manter prompts curtos e objetivos (economia de tokens);
- Chave sempre no backend, nunca no app.

---

## ✅ Checklist dos Diferenciais (critérios de nota da APS)

- [ ] Chatbot ambiental com IA
- [ ] Recomendação personalizada por perfil
- [ ] Relatórios com gráficos
- [ ] Sistema de alertas (push)
- [ ] Mapa de calor
- [ ] Tratamento robusto de erros/falhas

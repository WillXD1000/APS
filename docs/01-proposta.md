# 📄 Proposta de Projeto — APS

> Documento para submissão à análise e aprovação do **Coordenador Auxiliar**.

---

## 1. Identificação

| Campo | Descrição |
|---|---|
| **Título** | AirIA — Assistente Inteligente de Qualidade do Ar |
| **Domínio** | Gerenciamento de Informações Ambientais Urbanas |
| **Subtema** | Poluição do ar / Qualidade do ar urbano |
| **Disciplina vinculada** | Sistemas Distribuídos |
| **Plataforma-alvo** | Dispositivo móvel (Android/iOS via React Native) |

---

## 2. Descrição do Projeto

O **AirIA** é um aplicativo móvel distribuído que coleta, armazena e interpreta dados de **qualidade do ar** em áreas urbanas. O sistema consome dados de poluição de uma API pública (OpenAQ) por geolocalização e utiliza a **API do Google Gemini (IA generativa)** para converter indicadores técnicos de poluição em **recomendações acessíveis e personalizadas** ao cidadão.

A aplicação segue uma arquitetura cliente-servidor com múltiplos nós (aplicativo móvel, servidor backend, banco de dados e serviços externos de terceiros), caracterizando um **sistema distribuído**.

---

## 3. Justificativa

A poluição atmosférica é um problema ambiental urbano crítico, associado a doenças respiratórias e cardiovasculares. Embora os dados de monitoramento existam e sejam públicos, eles são **técnicos e de difícil interpretação** pelo cidadão comum.

O AirIA preenche essa lacuna ao:
- Traduzir dados brutos (PM2.5, PM10, O3, NO2, CO) em **linguagem natural**;
- Oferecer **recomendações de saúde personalizadas** com apoio de IA;
- Promover **conscientização ambiental** e apoio à tomada de decisão cotidiana.

---

## 4. Objetivos

### 4.1 Objetivo Geral
Desenvolver uma aplicação móvel distribuída que forneça informações de qualidade do ar interpretadas por inteligência artificial, apoiando decisões de saúde e conscientização ambiental.

### 4.2 Objetivos Específicos
- Consumir dados de qualidade do ar em tempo real por geolocalização;
- Armazenar histórico de medições e perfis de usuário em banco de dados;
- Integrar a API do Gemini para interpretação e recomendação personalizada;
- Disponibilizar um chatbot ambiental para dúvidas do usuário;
- Emitir alertas quando a qualidade do ar atingir níveis de risco;
- Gerar relatórios e visualizações gráficas do histórico.

---

## 5. Funcionalidades Principais

| # | Funcionalidade | Descrição |
|---|---|---|
| F1 | Consulta de qualidade do ar | Exibe índices atuais por geolocalização |
| F2 | Interpretação por IA | Gemini traduz os números em linguagem simples |
| F3 | Recomendação personalizada | Sugestões conforme perfil de saúde do usuário |
| F4 | Chatbot ambiental | Usuário faz perguntas em linguagem natural |
| F5 | Alertas | Notificação push quando a qualidade piora |
| F6 | Histórico e relatórios | Gráficos e relatórios de evolução |
| F7 | Perfil de usuário | Cadastro de perfil (idade, condições de saúde) |

---

## 6. Diferenciais (Refinamentos para avaliação)

Conforme os critérios de pontuação da APS, o projeto prevê:
- 🤖 **Chatbot ambiental** com IA generativa;
- 👤 **Personalização** por perfil de saúde;
- 📊 **Relatórios adicionais** com gráficos de histórico;
- 🔔 **Sistema de alertas** por notificação push;
- 🗺️ **Mapa de calor** da poluição por região;
- 🛡️ **Tratamento de erros** (indisponibilidade de API, ausência de dados na região, falha de rede).

---

## 7. Tecnologias

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Mobile | React Native (Expo) | Multiplataforma, ágil para protótipo |
| Backend | Python + FastAPI | API REST moderna, async, documentação automática |
| Banco | PostgreSQL | Robusto, suporte geoespacial (PostGIS) |
| IA | Google Gemini (Flash) | Multimodal, free tier sem custo para o projeto |
| Dados | OpenAQ | API pública e gratuita de qualidade do ar |

---

## 8. Relação com Sistemas Distribuídos

O projeto implementa e demonstra:
- **Modelo cliente-servidor** (REST entre mobile e backend);
- **Comunicação entre nós distribuídos** (backend ↔ OpenAQ ↔ Gemini);
- **Persistência distribuída** (servidor de banco de dados independente);
- **Transparência de acesso** (o cliente não conhece a origem dos dados);
- **Tratamento de falhas** de componentes remotos.

---

## 9. Resultados Esperados

Um aplicativo funcional, demonstrável ao vivo, capaz de:
- Mostrar a qualidade do ar da localização do usuário;
- Explicar e recomendar ações via IA;
- Responder a perguntas pelo chatbot;
- Exibir histórico e alertas.

---

## 10. Equipe

| Nome | RA |
|---|---|
| Gustavo Teixeira de Lima | G873270 |
| Northon Dias Conceição | R022FD7 |
| Willyam Oliveira de Lima | R022FF3 |

---

**Data:** ____/____/______
**Assinatura do Coordenador Auxiliar:** ___________________________

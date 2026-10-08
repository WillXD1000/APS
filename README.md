# 🌬️ AirIA — Assistente Inteligente de Qualidade do Ar

> **APS — 7º/8º Semestre — Ciência da Computação**
> Aplicação distribuída para dispositivo móvel no domínio de **Gerenciamento de Informações Ambientais Urbanas**, com uso de **Inteligência Artificial (Google Gemini)**.

---

## 📖 Sobre o Projeto

O **AirIA** é um aplicativo móvel que coleta dados de **qualidade do ar** em tempo real por geolocalização, armazena histórico e usa a **API do Google Gemini** para transformar números técnicos de poluição em **informação útil e personalizada** para o cidadão.

Em vez de apenas exibir índices crus (ex.: `PM2.5 = 48 µg/m³`), o AirIA:
- **Interpreta** os dados em linguagem simples;
- **Recomenda** ações personalizadas conforme o perfil de saúde do usuário (asmático, idoso, atleta, criança);
- Oferece um **chatbot ambiental** para tirar dúvidas ("posso levar meu filho ao parque hoje?");
- Envia **alertas** quando a qualidade do ar piora;
- Gera **relatórios e gráficos** de histórico.

---

## 🧩 Problema que resolve

A poluição do ar é um dos principais problemas ambientais urbanos, com impacto direto na saúde. Os dados existem (estações de monitoramento, APIs públicas), mas são **técnicos e pouco acessíveis** ao cidadão comum. O AirIA faz a ponte entre o **dado bruto** e a **decisão do dia a dia**.

---

## 🏗️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Mobile (cliente)** | React Native (Expo) |
| **Backend (servidor)** | Python + FastAPI |
| **Banco de dados** | PostgreSQL |
| **IA** | Google Gemini API (modelo Flash — free tier) |
| **Dados ambientais** | OpenAQ (API pública de qualidade do ar) |
| **Deploy** | Docker + Cloud (Render / Railway / GCP) |

---

## 🌐 Caráter de Sistema Distribuído

O projeto demonstra conceitos de Sistemas Distribuídos:
- **Arquitetura cliente-servidor** (mobile ↔ backend via REST);
- **Integração com serviços remotos de terceiros** (OpenAQ e Gemini);
- **Persistência em servidor de banco de dados independente** (PostgreSQL);
- **Comunicação assíncrona e notificações push**;
- **Separação de responsabilidades** entre nós da arquitetura.

> ⚠️ A chave da API do Gemini fica **protegida no backend** — o app mobile nunca a acessa diretamente. Isso reforça a segurança e caracteriza o nó intermediário do sistema distribuído.

---

## 📂 Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| [`backend/`](backend/) | API REST (FastAPI + PostgreSQL + OpenAQ + Gemini) |
| [`mobile/`](mobile/) | Aplicativo React Native (Expo) |
| [`docs/`](docs/) | Documentação do projeto |

## 📄 Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/01-proposta.md`](docs/01-proposta.md) | Proposta do projeto para submissão ao coordenador |
| [`docs/02-arquitetura.md`](docs/02-arquitetura.md) | Arquitetura do sistema distribuído |
| [`docs/03-plano-desenvolvimento.md`](docs/03-plano-desenvolvimento.md) | Plano de desenvolvimento em etapas |
| [`backend/README.md`](backend/README.md) | Como rodar o backend |
| [`mobile/README.md`](mobile/README.md) | Como rodar o app mobile |
| [`docs/trabalho/`](docs/trabalho/) | Trabalho escrito da APS (texto, diagramas e gerador do `.docx`) |

---

## 👥 Equipe

| Nome | RA |
|---|---|
| Gustavo Teixeira de Lima | G873270 |
| Northon Dias Conceição | R022FD7 |
| Willyam Oliveira de Lima | R022FF3 |

Ciência da Computação – 7º semestre – UNIP, campus Paulista. Professora: Jacqueline Reis.

---

## 📅 Status

🟢 **Em desenvolvimento** — backend completo (auth, OpenAQ, Gemini) e app mobile (login, consulta, chatbot, histórico, perfil).

### Progresso
- ✅ Etapa 1 — Backend base (autenticação JWT)
- ✅ Etapa 2 — Qualidade do ar (OpenAQ + IQAr)
- ✅ Etapa 3 — IA (Gemini: interpretação, recomendação, chatbot)
- ✅ Etapa 4 — App mobile (React Native)
- ✅ Etapa 5 — Alertas por perfil de saúde, relatório com gráfico e troca do perfil

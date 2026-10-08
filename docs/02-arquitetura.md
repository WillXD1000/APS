# 🏗️ Arquitetura do Sistema — AirIA

> Documento técnico de arquitetura, com ênfase nos conceitos de **Sistemas Distribuídos**.

---

## 1. Visão Geral

O AirIA adota uma arquitetura **cliente-servidor em camadas**, com múltiplos nós independentes que se comunicam por rede. Cada nó tem responsabilidade bem definida.

```
┌───────────────────┐
│   APP MOBILE      │  Cliente (React Native / Expo)
│  - UI/UX          │
│  - Geolocalização │
│  - Push notif.    │
└─────────┬─────────┘
          │  HTTPS / REST (JSON)
          ▼
┌───────────────────────────────────────┐
│         BACKEND (FastAPI)              │  Servidor de aplicação
│  ┌─────────────────────────────────┐  │
│  │  Camada de API (rotas REST)     │  │
│  ├─────────────────────────────────┤  │
│  │  Camada de Serviços (regras)    │  │
│  │   - AirQualityService           │  │
│  │   - GeminiService               │  │
│  │   - AlertService                │  │
│  ├─────────────────────────────────┤  │
│  │  Camada de Dados (repositórios) │  │
│  └─────────────────────────────────┘  │
└───┬───────────────┬───────────────┬───┘
    │               │               │
    │ SQL           │ HTTPS         │ HTTPS
    ▼               ▼               ▼
┌─────────┐   ┌───────────┐   ┌───────────┐
│PostgreSQL│  │  OpenAQ   │   │ Gemini API│
│(histórico│  │  (dados   │   │   (IA)    │
│ perfis)  │  │  de ar)   │   │           │
└─────────┘   └───────────┘   └───────────┘
```

---

## 2. Nós do Sistema Distribuído

| Nó | Papel | Tecnologia |
|---|---|---|
| **Cliente Mobile** | Interface, geolocalização, exibição | React Native |
| **Servidor de Aplicação** | Lógica de negócio, orquestração, segurança | FastAPI |
| **Servidor de Banco de Dados** | Persistência de histórico e perfis | PostgreSQL |
| **Serviço de Dados Ambientais** | Fonte de dados de qualidade do ar | OpenAQ (externo) |
| **Serviço de IA** | Interpretação e recomendação | Gemini (externo) |

---

## 3. Fluxo de Comunicação (exemplo: consulta de qualidade do ar)

```
1. Usuário abre o app → mobile obtém coordenadas (lat/long) via GPS.
2. Mobile → Backend:  GET /air-quality?lat=-23.5&lon=-46.6
3. Backend → OpenAQ:  busca medições mais próximas.
4. Backend → PostgreSQL:  grava a medição no histórico.
5. Backend → Gemini:  envia os dados + perfil do usuário,
                       pede interpretação e recomendação.
6. Gemini → Backend:  retorna texto interpretado.
7. Backend → Mobile:  JSON { indices, interpretacao, recomendacao }
8. Mobile:  exibe os dados e a recomendação da IA.
```

---

## 4. Conceitos de Sistemas Distribuídos Aplicados

| Conceito | Como aparece no AirIA |
|---|---|
| **Transparência de acesso** | O cliente faz uma única requisição; o backend esconde a origem (OpenAQ, Gemini, banco). |
| **Transparência de localização** | O app não sabe onde está hospedado o backend nem as APIs externas. |
| **Comunicação por mensagens** | REST/JSON sobre HTTPS entre os nós. |
| **Escalabilidade** | Serviços no backend são independentes e podem ser escalados/separados. |
| **Tolerância a falhas** | Tratamento de indisponibilidade de OpenAQ/Gemini com respostas de fallback. |
| **Concorrência** | FastAPI assíncrono atende múltiplos clientes simultâneos. |
| **Segurança** | Chaves de API protegidas no servidor; comunicação por HTTPS. |

---

## 5. Modelo de Dados (PostgreSQL)

```sql
-- Usuários e seu perfil de saúde
CREATE TABLE usuarios (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(120) NOT NULL,
    email         VARCHAR(160) UNIQUE NOT NULL,
    senha_hash    VARCHAR(255) NOT NULL,
    perfil_saude  VARCHAR(40),          -- ex.: 'asmatico', 'idoso', 'atleta', 'crianca', 'geral'
    criado_em     TIMESTAMP DEFAULT NOW()
);

-- Histórico de medições de qualidade do ar
CREATE TABLE medicoes (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER REFERENCES usuarios(id),
    latitude      DOUBLE PRECISION NOT NULL,
    longitude     DOUBLE PRECISION NOT NULL,
    cidade        VARCHAR(120),
    pm25          DOUBLE PRECISION,
    pm10          DOUBLE PRECISION,
    o3            DOUBLE PRECISION,
    no2           DOUBLE PRECISION,
    co            DOUBLE PRECISION,
    indice_geral  INTEGER,              -- IQAr calculado
    categoria     VARCHAR(30),          -- 'bom', 'moderado', 'ruim', etc.
    coletado_em   TIMESTAMP DEFAULT NOW()
);

-- Alertas enviados ao usuário
CREATE TABLE alertas (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER REFERENCES usuarios(id),
    mensagem      TEXT NOT NULL,
    nivel         VARCHAR(20),          -- 'info', 'atencao', 'perigo'
    enviado_em    TIMESTAMP DEFAULT NOW()
);

-- Histórico de conversas do chatbot (opcional)
CREATE TABLE conversas (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER REFERENCES usuarios(id),
    pergunta      TEXT NOT NULL,
    resposta      TEXT NOT NULL,
    criado_em     TIMESTAMP DEFAULT NOW()
);
```

---

## 6. Endpoints da API (FastAPI)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/register` | Cadastro de usuário |
| `POST` | `/auth/login` | Login (retorna token JWT) |
| `GET` | `/air-quality` | Qualidade do ar por lat/long (+ interpretação IA) |
| `GET` | `/history` | Histórico de medições do usuário |
| `POST` | `/chat` | Pergunta ao chatbot ambiental |
| `GET` | `/alerts` | Lista de alertas do usuário |
| `GET` | `/report` | Relatório agregado (gráficos) |
| `GET` | `/profile` / `PUT /profile` | Perfil de saúde |

---

## 7. Integração com o Gemini (padrão de uso)

```
Backend monta um prompt estruturado:

"Você é um assistente de qualidade do ar. Dados atuais:
PM2.5=48, PM10=70, O3=30 (µg/m³), categoria=RUIM.
Perfil do usuário: asmático.
Explique em 2 frases simples e dê uma recomendação prática."

Gemini responde em linguagem natural → backend repassa ao app.
```

> A chave da API fica em variável de ambiente (`GEMINI_API_KEY`) **somente no backend**.

---

## 8. Tratamento de Falhas (tolerância)

| Falha | Estratégia |
|---|---|
| OpenAQ indisponível | Retorna última medição do histórico + aviso |
| Gemini indisponível | Exibe interpretação local baseada em faixas do IQAr |
| Sem dados na região | Busca a estação válida mais próxima |
| Falha de rede no mobile | Cache local da última consulta |
| Limite de requisições (free tier) | Fila/cache de respostas por região |

---

## 9. Segurança

- Comunicação por **HTTPS**;
- **Autenticação JWT** entre mobile e backend;
- **Chaves de API** (Gemini/OpenAQ) apenas no servidor, nunca no cliente;
- **Hash de senhas** (bcrypt);
- **Variáveis de ambiente** (`.env`) para segredos;
- **Privacidade da localização:** o app arredonda latitude e longitude para 2 casas
  decimais (cerca de 1 km) antes de enviá-las ao backend. A estação é buscada num
  raio de 25 km, então o resultado não muda, e o histórico (`medicoes`) não guarda a
  posição exata do usuário. O nome do lugar exibido na tela é calculado no próprio
  aparelho.

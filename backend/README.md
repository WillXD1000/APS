# 🐍 Backend — AirIA

API REST do assistente inteligente de qualidade do ar, construída com **FastAPI** + **PostgreSQL**.

> **Etapas concluídas:**
> - ✅ **Etapa 1:** base do backend com autenticação (cadastro/login via JWT) e banco de dados.
> - ✅ **Etapa 2:** integração com a **OpenAQ** (consulta de qualidade do ar + cálculo do IQAr + histórico).
> - ✅ **Etapa 3:** integração com o **Gemini** (interpretação por IA, recomendação personalizada e chatbot ambiental).
> - ✅ **Etapa 5:** alertas por perfil de saúde, relatório por dia e troca do perfil de saúde.

---

## 📋 Pré-requisitos

- **Python 3.11+**
- **PostgreSQL 14+** rodando (local ou via Docker)
- Acesso à internet (para instalar dependências)

---

## 🚀 Como rodar

### 1. Criar e ativar um ambiente virtual

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e ajuste principalmente:
- `DATABASE_URL` → com o usuário, senha e nome do seu banco PostgreSQL;
- `JWT_SECRET` → um segredo forte (gere com o comando abaixo);
- `OPENAQ_API_KEY` → **(Etapa 2)** chave gratuita da OpenAQ. Crie uma conta em
  https://explore.openaq.org e gere sua chave na área de conta/API.
- `GEMINI_API_KEY` → **(Etapa 3)** chave gratuita do Gemini. Gere em
  https://aistudio.google.com (botão "Get API key"). Sem ela, o app continua
  funcionando com interpretações locais (fallback), mas o chatbot fica limitado.
- `GEMINI_MODEL` → modelo do Gemini (padrão `gemini-3.5-flash-lite`). Opcional.

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Criar o banco de dados no PostgreSQL

```bash
# Exemplo criando o banco "airia"
createdb airia
# ou via psql:
# psql -U postgres -c "CREATE DATABASE airia;"
```

> As **tabelas** são criadas automaticamente na primeira inicialização da API.

### 5. Subir o servidor

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em: **http://localhost:8000**

---

## 📚 Documentação interativa

Com o servidor rodando, acesse:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔌 Endpoints

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| `GET` | `/` | Health check | ❌ |
| `POST` | `/auth/register` | Cadastra um usuário | ❌ |
| `POST` | `/auth/login` | Login → retorna token JWT | ❌ |
| `GET` | `/auth/me` | Dados do usuário logado | ✅ (Bearer) |
| `GET` | `/air-quality?lat=&lon=` | Qualidade do ar + IQAr + interpretação da IA | ✅ (Bearer) |
| `GET` | `/history?limite=` | Histórico de medições do usuário | ✅ (Bearer) |
| `POST` | `/chat` | Chatbot ambiental (pergunta → resposta da IA) | ✅ (Bearer) |
| `GET` | `/chat/history?limite=` | Histórico de conversas do usuário | ✅ (Bearer) |
| `PUT` | `/auth/me/perfil` | Altera o perfil de saúde do usuário | ✅ (Bearer) |
| `GET` | `/alerts?limite=` | Alertas do usuário, mais recentes primeiro | ✅ (Bearer) |
| `GET` | `/report?dias=` | Relatório por dia: índice médio, máximo e total (1 a 31 dias) | ✅ (Bearer) |

### Exemplo: cadastro

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria","email":"maria@email.com","senha":"123456","perfil_saude":"asmatico"}'
```

### Exemplo: login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"maria@email.com","senha":"123456"}'
```

A resposta traz o `access_token`. Use-o nas rotas protegidas:

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

### Exemplo: consultar qualidade do ar (São Paulo)

```bash
curl "http://localhost:8000/air-quality?lat=-23.55&lon=-46.63" \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

Resposta (exemplo):

```json
{
  "latitude": -23.55,
  "longitude": -46.63,
  "cidade": "São Paulo",
  "estacao": "Pinheiros",
  "poluentes": { "pm25": 18.0, "pm10": 32.0, "o3": 55.0, "no2": null, "co": null },
  "indice_geral": 41,
  "categoria": "Moderada",
  "poluente_critico": "o3",
  "coletado_em": "2026-01-01T12:00:00Z"
}
```

### Exemplo: histórico

```bash
curl "http://localhost:8000/history?limite=10" \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

### Exemplo: chatbot ambiental

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SEU_TOKEN>" \
  -d '{"pergunta":"Posso levar meu filho ao parque hoje?"}'
```

Resposta (exemplo):

```json
{
  "pergunta": "Posso levar meu filho ao parque hoje?",
  "resposta": "Com a qualidade do ar atual classificada como Boa na sua região, é um ótimo dia para atividades ao ar livre com a criança..."
}
```

### Alertas

A cada consulta em `/air-quality`, o backend avalia se o ar exige um alerta para o
perfil de saúde do usuário:

| Perfil | Alerta a partir de |
|---|---|
| `asmatico`, `idoso`, `crianca` | Moderada |
| `geral`, `atleta` | Ruim |

O nível é `perigo` para Muito Ruim e Péssima, e `atencao` nos demais casos. A resposta
de `/air-quality` traz o campo `alerta` (`null` quando não há alerta):

```json
"alerta": {
  "nivel": "atencao",
  "mensagem": "Qualidade do ar moderada em Diadema. Como seu perfil é sensível à poluição, evite esforço físico prolongado ao ar livre.",
  "novo": true
}
```

`novo: true` indica que o alerta acabou de ser gravado em `/alerts`. Para não repetir o
mesmo aviso, um alerta do mesmo nível só é gravado de novo depois de 3 horas.

### Exemplo: alterar o perfil de saúde

```bash
curl -X PUT http://localhost:8000/auth/me/perfil \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SEU_TOKEN>" \
  -d '{"perfil_saude":"asmatico"}'
```

### Exemplo: relatório dos últimos 7 dias

```bash
curl "http://localhost:8000/report?dias=7" \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

Cada item de `itens` traz `data`, `total`, `indice_medio`, `indice_maximo` e
`categoria`. Dias sem consulta aparecem com `total: 0`. As consultas são agrupadas
pelo horário de Brasília (UTC−3).

> ⚠️ **Importante:**
> - O endpoint `/air-quality` precisa da `OPENAQ_API_KEY` no `.env`. Sem ela (ou chave
>   inválida), retorna `502` com mensagem explicativa. Nem toda coordenada tem estação
>   num raio de 25 km — nesse caso também é `502` com explicação.
> - A `interpretacao` e a `recomendacao` do `/air-quality` usam o **Gemini**. Se a
>   `GEMINI_API_KEY` não estiver configurada ou a IA falhar, o sistema usa textos
>   locais (fallback) — ou seja, **não quebra**.
> - O `/chat` depende mais fortemente do Gemini: sem a chave, retorna uma mensagem
>   avisando que o assistente não está configurado.

### Cota gratuita do Gemini

A cota gratuita é **por modelo e por projeto**, contada por dia. No `gemini-2.5-flash`,
por exemplo, o limite medido foi de 20 requisições por dia. Por isso:

- **Cache:** a interpretação de cada combinação de local, categoria e perfil é
  reaproveitada por 30 minutos. Consultas repetidas na tela Início não gastam cota.
  O cache fica na memória do processo e é zerado quando o backend reinicia.
- **Erros visíveis:** quando o Gemini falha, o terminal do backend mostra uma linha
  `Falha ao chamar o Gemini (modelo=..., motivo=...)`. O chat explica o motivo:
  limite atingido (429), modelo indisponível (404) ou chave inválida (400/401/403).
- **Se a cota acabar:** espere o dia virar, troque o `GEMINI_MODEL` no `.env` por outro
  modelo da sua chave (cada um tem cota própria) ou gere uma chave em outro projeto do
  AI Studio. Para listar os modelos da sua chave:

```bash
python -c "from app.core.config import settings; from google import genai; c = genai.Client(api_key=settings.gemini_api_key); print([m.name for m in c.models.list() if 'flash' in m.name])"
```

---

## 🗂️ Estrutura do projeto

```
backend/
├── app/
│   ├── main.py              # ponto de entrada (FastAPI)
│   ├── core/                # config, banco e segurança
│   ├── models/              # tabelas (SQLAlchemy)
│   ├── schemas/             # validação (Pydantic)
│   ├── repositories/        # acesso ao banco
│   ├── services/            # regras de negócio
│   └── api/                 # rotas e dependências
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🏛️ Arquitetura em camadas

```
Requisição HTTP
      │
      ▼
  api/routes  ← recebe a requisição, trata erros HTTP
      │
      ▼
  services    ← regras de negócio (ex.: autenticação)
      │
      ▼
 repositories ← acesso ao banco (CRUD)
      │
      ▼
   models     ← tabelas no PostgreSQL
```

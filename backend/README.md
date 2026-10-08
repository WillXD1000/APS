# 🐍 Backend — AirIA

API REST do assistente inteligente de qualidade do ar, construída com **FastAPI** + **PostgreSQL**.

> **Etapas concluídas:**
> - ✅ **Etapa 1:** base do backend com autenticação (cadastro/login via JWT) e banco de dados.
> - ✅ **Etapa 2:** integração com a **OpenAQ** (consulta de qualidade do ar + cálculo do IQAr + histórico).
> - ✅ **Etapa 3:** integração com o **Gemini** (interpretação por IA, recomendação personalizada e chatbot ambiental).

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

> ⚠️ **Importante:**
> - O endpoint `/air-quality` precisa da `OPENAQ_API_KEY` no `.env`. Sem ela (ou chave
>   inválida), retorna `502` com mensagem explicativa. Nem toda coordenada tem estação
>   num raio de 25 km — nesse caso também é `502` com explicação.
> - A `interpretacao` e a `recomendacao` do `/air-quality` usam o **Gemini**. Se a
>   `GEMINI_API_KEY` não estiver configurada ou a IA falhar, o sistema usa textos
>   locais (fallback) — ou seja, **não quebra**.
> - O `/chat` depende mais fortemente do Gemini: sem a chave, retorna uma mensagem
>   avisando que o assistente não está configurado.

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

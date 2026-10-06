# 🐍 Backend — AirIA

API REST do assistente inteligente de qualidade do ar, construída com **FastAPI** + **PostgreSQL**.

> **Etapa 1 (atual):** base do backend com autenticação (cadastro/login via JWT) e banco de dados.
> As integrações com **OpenAQ** (Etapa 2) e **Gemini** (Etapa 3) virão nas próximas etapas.

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
- `JWT_SECRET` → um segredo forte (gere com o comando abaixo).

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

## 🔌 Endpoints desta etapa

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| `GET` | `/` | Health check | ❌ |
| `POST` | `/auth/register` | Cadastra um usuário | ❌ |
| `POST` | `/auth/login` | Login → retorna token JWT | ❌ |
| `GET` | `/auth/me` | Dados do usuário logado | ✅ (Bearer) |

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

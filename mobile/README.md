# 📱 Mobile — AirIA

Aplicativo móvel do AirIA, construído com **React Native (Expo SDK 57)**.

> App com login/cadastro, consulta da qualidade do ar pela **localização do celular**,
> interpretação da IA, alertas por perfil de saúde, chatbot ambiental, histórico com
> gráfico e perfil.

---

## 📋 Pré-requisitos

- **Node.js 22.13+**
- **Expo** (usado via `npx`, não precisa instalar global)
- O **backend rodando** e acessível pela rede (veja `../backend/README.md`)
- Um **celular** com o app **Expo Go** da loja (Android/iOS), que roda o SDK 57, **ou** um emulador

---

## 🚀 Como rodar

### 1. Instalar as dependências

```bash
cd mobile
npm install
```

### 2. Configurar a URL do backend

```bash
cp .env.example .env
```

Edite o `.env` e ajuste a `EXPO_PUBLIC_API_URL`:

- **Celular físico (Expo Go):** use o **IP da sua máquina** na rede local.
  - Descubra com `ipconfig` (Windows) → procure "Endereço IPv4", algo como `192.168.0.10`.
  - Exemplo: `EXPO_PUBLIC_API_URL=http://192.168.0.10:8000`
- **Emulador Android:** `EXPO_PUBLIC_API_URL=http://10.0.2.2:8000`
- ⚠️ **Nunca use `localhost`** no celular/emulador — ele aponta para o próprio aparelho, não para o seu PC.

### 3. Garantir que o backend aceita conexões externas

Suba o backend ouvindo em todas as interfaces (não só localhost):

```bash
# na pasta backend, com o venv ativo:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> O `--host 0.0.0.0` é essencial para o celular alcançar o servidor pela rede.

### 4. Iniciar o app

Em um terminal **separado** do backend (sem o `.venv` do Python ativo):

```bash
npx expo start --clear
```

Vai aparecer um **QR Code** no terminal. Abra o app **Expo Go** no celular
e escaneie o QR Code (o celular e o PC precisam estar na **mesma rede Wi-Fi**).

> 💡 Para adicionar pacotes, use sempre `npx expo install <pacote>` em vez de
> `npm install <pacote>`: ele escolhe a versão compatível com o SDK do projeto.

---

## 📍 Localização

- Na primeira abertura, o app pede permissão de localização. Sem ela, a tela Início
  explica o motivo e mostra um botão para permitir ou para abrir as configurações do
  celular. Ao voltar das configurações, o app tenta de novo sozinho.
- A estação de monitoramento é buscada num raio de **25 km**. Se não houver nenhuma,
  a tela mostra a mensagem do backend.
- **Privacidade:** a latitude e a longitude são arredondadas para **2 casas decimais**
  (cerca de 1 km) antes de irem para o backend, que grava esses valores no histórico.
  O resultado não muda, porque o raio de busca é de 25 km. O nome do lugar
  ("Vila Mariana, São Paulo") é obtido no próprio aparelho.
- **Emulador Android:** a localização padrão é na Califórnia. Para simular outro
  lugar, use os controles do emulador (`...` → **Location**) e informe a latitude e
  a longitude, por exemplo `-23.55` e `-46.63` para São Paulo.

---

## 🧭 Telas

| Aba | Descrição |
|---|---|
| **Início** | Usa a localização do celular e consulta a qualidade do ar automaticamente ao abrir, com interpretação da IA. Botão "Atualizar" ou puxar a tela para baixo refaz a consulta. Mostra um banner de alerta quando o ar exige atenção para o seu perfil, e um popup quando o alerta é novo |
| **Chat** | Chatbot ambiental (pergunte sobre o ar) |
| **Histórico** | Gráfico do índice médio dos últimos 7 dias, alertas recentes e lista das consultas |
| **Perfil** | Dados do usuário, troca do perfil de saúde (com descrição de cada um) e logout |

Antes de logar: telas de **Login** e **Cadastro** (com a escolha do perfil de saúde).

> Os alertas aparecem **dentro do app**. Notificações push com o app fechado não
> funcionam no Expo Go para Android desde o SDK 53: exigiriam um development build.

---

## 🗂️ Estrutura

```
mobile/
├── index.js                # ponto de entrada (registra o App)
├── App.js                  # raiz (providers + navegação)
├── app.json                # config do Expo
├── assets/                 # ícones e favicon
├── src/
│   ├── api/                # chamadas ao backend (axios)
│   ├── components/         # AirQualityCard, AlertBanner, IndexChart,
│   │                       # HealthProfilePicker
│   ├── config/             # perfis de saúde e tema/cores
│   ├── services/           # localização do celular (expo-location)
│   ├── contexts/           # AuthContext (sessão)
│   ├── navigation/         # abas + fluxo de auth
│   └── screens/            # telas
└── .env.example
```

---

## 🔧 Solução de problemas

| Problema | Causa provável | Solução |
|---|---|---|
| "Network Error" | URL errada ou backend fora da rede | Use o IP da máquina; suba o backend com `--host 0.0.0.0` |
| Trava na tela de carregamento | Backend inacessível | Confira se PC e celular estão na mesma Wi-Fi |
| Login falha com 401 | Credenciais erradas | Cadastre-se novamente ou revise e-mail/senha |
| `/air-quality` dá erro | Backend sem `OPENAQ_API_KEY` | Configure a chave no `.env` do backend |
| Respostas da IA genéricas | Backend sem `GEMINI_API_KEY` | Configure a chave do Gemini no backend (opcional) |
| "Project is incompatible with this version of Expo Go" | Expo Go com SDK diferente do projeto (57) | Atualize o Expo Go pela loja |
| Erros de dependência ao iniciar | Pacote com versão incompatível com o SDK | Rode `npx expo install --fix` e depois `npx expo-doctor` |
| `Unable to resolve module expo-location` | Pacote de localização não instalado | Rode `npx expo install expo-location` |
| "Não foi possível obter sua localização" | GPS sem sinal ou demorando mais de 15 s | Toque em Tentar novamente, de preferência perto de uma janela |

---

## 🌐 Fluxo distribuído

```
App (Expo) ──HTTP──> Backend (FastAPI) ──> OpenAQ + Gemini + PostgreSQL
```

O app apenas consome a API; toda a lógica, as chaves e os dados ficam no backend.

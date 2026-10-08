# 4 PLANO DE DESENVOLVIMENTO DA APLICAÇÃO

Este capítulo descreve o que a aplicação deveria fazer, com quais elementos e ferramentas ela foi construída e como o trabalho foi organizado. Ao final, registra as dificuldades encontradas e a forma como os testes foram feitos.

## 4.1 Escopo

O AirIA é composto por um aplicativo móvel e por um servidor de aplicação com banco de dados próprio, que se integra a dois serviços externos: a OpenAQ, para as medições de qualidade do ar, e o Google Gemini, para a geração de textos. O escopo inclui o cadastro e a autenticação de usuários, a consulta da qualidade do ar pela localização do celular, a interpretação por inteligência artificial, os alertas por perfil de saúde, o chat, o histórico com gráfico e a troca do perfil de saúde.

Ficaram fora do escopo as notificações com o aplicativo fechado, que exigiriam uma versão compilada do aplicativo, a publicação nas lojas e a implantação do servidor em nuvem. Durante o desenvolvimento e a apresentação, o servidor roda em um computador da equipe, na mesma rede do celular.

## 4.2 Requisitos funcionais

Os requisitos funcionais descrevem o que o sistema faz. Eles estão listados no Quadro 2.

Quadro 2 – Requisitos funcionais

| Código | Requisito |
|---|---|
| RF01 | Cadastrar usuário com nome, e-mail, senha e perfil de saúde. |
| RF02 | Autenticar o usuário e manter a sessão entre as aberturas do aplicativo. |
| RF03 | Pedir a permissão e obter a localização do celular. |
| RF04 | Consultar as medições da estação de monitoramento mais próxima, em um raio de 25 km. |
| RF05 | Calcular o IQAr, a categoria e o poluente que define o índice. |
| RF06 | Gerar, com IA, uma interpretação do resultado e uma recomendação para o perfil do usuário. |
| RF07 | Emitir alertas conforme o perfil de saúde e manter o histórico de alertas. |
| RF08 | Responder perguntas no chat, usando a última consulta do usuário como contexto. |
| RF09 | Exibir o histórico de consultas. |
| RF10 | Exibir um gráfico com o índice médio de cada um dos últimos sete dias. |
| RF11 | Permitir a troca do perfil de saúde, com a descrição de cada perfil. |
| RF12 | Encerrar a sessão do usuário. |

Fonte: autoria própria.

## 4.3 Requisitos não funcionais

Os requisitos não funcionais descrevem as qualidades que o sistema deve ter. Eles estão no Quadro 3.

Quadro 3 – Requisitos não funcionais

| Código | Requisito |
|---|---|
| RNF01 | Executar em Android e iOS a partir de uma única base de código (React Native com Expo). |
| RNF02 | Guardar senhas apenas como *hash* bcrypt e autenticar as requisições com token JWT válido por 24 horas. |
| RNF03 | Manter as chaves da OpenAQ e do Gemini somente no servidor, em variáveis de ambiente. |
| RNF04 | Enviar ao servidor as coordenadas arredondadas para duas casas decimais (cerca de 1 km). |
| RNF05 | Continuar funcionando quando a IA falhar, com textos locais baseados na categoria do índice. |
| RNF06 | Limitar a espera do GPS a 15 segundos e a espera da OpenAQ a 15 segundos. |
| RNF07 | Reaproveitar por 30 minutos a interpretação da IA para o mesmo local, categoria e perfil. |
| RNF08 | Apresentar textos em português simples e cores padronizadas para cada categoria do IQAr. |
| RNF09 | Usar apenas serviços com acesso gratuito. |
| RNF10 | Organizar o código em camadas e documentar a instalação e o uso. |

Fonte: autoria própria.

## 4.4 Elementos da aplicação

A aplicação é formada por telas no celular e por serviços no servidor. O Quadro 4 relaciona os elementos de cada lado.

Quadro 4 – Elementos da aplicação

| Elemento | Lado | Função |
|---|---|---|
| Telas de entrada e cadastro | Aplicativo | Login e criação de conta, com escolha do perfil de saúde |
| Tela Início | Aplicativo | Localização, qualidade do ar, textos da IA e alerta |
| Tela Chat | Aplicativo | Conversa com o assistente ambiental |
| Tela Histórico | Aplicativo | Gráfico de sete dias, alertas recentes e consultas |
| Tela Perfil | Aplicativo | Dados do usuário, troca do perfil e saída |
| Serviço de autenticação | Servidor | Cadastro, login, emissão e validação do token |
| Serviço de qualidade do ar | Servidor | Orquestra a consulta, o índice, a IA, o alerta e o histórico |
| Serviço OpenAQ | Servidor | Busca estações e medições recentes |
| Serviço IQAr | Servidor | Calcula o índice e a categoria |
| Serviço Gemini | Servidor | Interpretação, recomendação, chat e cache |
| Serviço de alertas | Servidor | Regra por perfil e registro sem repetição |
| Banco de dados | Servidor | Usuários, medições, alertas e conversas |

Fonte: autoria própria.

## 4.5 Ferramentas e tecnologias utilizadas

O Quadro 5 lista as ferramentas usadas, com as versões que constam nos arquivos de dependências do projeto.

Quadro 5 – Ferramentas e tecnologias

| Ferramenta | Versão | Uso no projeto |
|---|---|---|
| Python | 3.13 | Linguagem do servidor |
| FastAPI e Uvicorn | 0.115 e 0.34 | Framework da API e servidor de execução |
| Pydantic | 2.10 | Validação dos dados de entrada e saída |
| SQLAlchemy | 2.0 | Acesso ao banco de dados (ORM) |
| PostgreSQL | 14 ou superior | Banco de dados relacional |
| bcrypt e python-jose | 4.2 e 3.3 | *Hash* de senhas e tokens JWT |
| httpx | 0.28 | Requisições do servidor à OpenAQ |
| google-genai | 1.9 | Cliente da API do Gemini |
| Node.js e npm | 22 | Ambiente de execução e gerenciador de pacotes do aplicativo |
| Expo SDK e Expo CLI | 57 | Plataforma de desenvolvimento do aplicativo |
| React Native e React | 0.86 e 19.2 | Framework e biblioteca de interface |
| React Navigation | 7 | Navegação por pilha e por abas |
| Axios | 1 | Cliente HTTP do aplicativo |
| AsyncStorage | 2.2 | Armazenamento local da sessão |
| expo-location | 57.0 | Localização e permissão |
| Expo Go | SDK 57 | Execução do aplicativo no celular durante o desenvolvimento |
| Swagger UI | gerado pelo FastAPI | Teste manual dos endpoints |
| Google AI Studio | — | Geração da chave e acompanhamento da cota do Gemini |
| OpenAQ Explore | — | Geração da chave da OpenAQ |
| Git e GitHub | — | Controle de versão, revisão por *pull requests* e histórico |
| Kiro | — | Assistente de programação com IA, usado como apoio na escrita e revisão de código |

Fonte: autoria própria.

## 4.6 Metodologia e etapas

O desenvolvimento seguiu um modelo incremental. Cada etapa produziu uma parte que funcionava sozinha e era testada antes de a etapa seguinte começar. Primeiro foi construído o servidor, porque o aplicativo depende dele. Depois veio o aplicativo, e por fim os recursos adicionais.

**Etapa 1 – Base do servidor.** Estrutura em camadas do FastAPI, conexão com o PostgreSQL, criação das tabelas de usuários, medições, alertas e conversas, e autenticação com cadastro, login e token JWT. A validação foi feita pelo Swagger, com cadastro e login de um usuário de teste.

**Etapa 2 – Qualidade do ar.** Integração com a API da OpenAQ, cálculo do IQAr e gravação de cada consulta no histórico. A validação foi a consulta do centro de São Paulo, que retornou a estação de Diadema com os poluentes e a categoria corretos.

**Etapa 3 – Inteligência artificial.** Integração com o Gemini para gerar a interpretação e a recomendação conforme o perfil, criação do chat e textos locais para quando a IA não responde. A validação comparou as respostas da IA e os textos locais com os dados da consulta.

**Etapa 4 – Aplicativo.** Projeto em React Native com Expo, telas de entrada, cadastro, Início, Chat, Histórico e Perfil, sessão persistente e cliente HTTP com token. A validação foi feita no celular, pelo Expo Go, com o servidor rodando no computador da equipe.

**Etapa 5 – Alertas e relatório.** Regra de alerta por perfil de saúde, relatório por dia com gráfico, escolha do perfil com descrição e correção do teclado no Android.

**Refinamentos finais.** Troca da escolha manual de cidade pela localização do celular, com arredondamento das coordenadas, e melhorias na integração com o Gemini: modelo configurável, registro do motivo das falhas e cache das respostas.

## 4.7 Cronograma

O Quadro 6 resume a sequência das etapas, as entregas de cada uma e como foram validadas.

Quadro 6 – Cronograma das etapas

| Ordem | Etapa | Entrega | Validação |
|---|---|---|---|
| 1 | Proposta e arquitetura | Documento de proposta, arquitetura e plano | Revisão pela equipe |
| 2 | Base do servidor | API com cadastro, login e banco de dados | Swagger |
| 3 | Qualidade do ar | Endpoint de consulta, IQAr e histórico | Consulta real em São Paulo |
| 4 | Inteligência artificial | Interpretação, recomendação e chat | Respostas reais da IA e textos locais |
| 5 | Aplicativo | Telas, navegação e sessão | Expo Go no celular |
| 6 | Alertas e relatório | Alertas, gráfico, perfil de saúde | Celular e testes isolados da lógica |
| 7 | Refinamentos | Localização, cache e erros da IA | Celular e testes isolados da lógica |
| 8 | Documentação | Este trabalho e a apresentação | Revisão pela equipe |

Fonte: autoria própria.

## 4.8 Organização do trabalho e do código

O trabalho foi feito pela equipe em conjunto. O código fica em um repositório Git hospedado no GitHub, dividido em três pastas: `backend` (servidor), `mobile` (aplicativo) e `docs` (documentação). Cada etapa foi desenvolvida em uma ramificação própria, como `feat/etapa2-openaq` ou `fix/gemini-erros-cache`, e incorporada à ramificação principal por meio de um *pull request*. Isso deixou registrado o que mudou em cada etapa e permitiu revisar as mudanças antes de juntá-las ao restante.

Os arquivos de configuração com senhas e chaves (`.env`) não são enviados ao repositório. Em seu lugar, o repositório contém modelos (`.env.example`) com a descrição de cada variável.

## 4.9 Dificuldades encontradas e soluções

Várias decisões do projeto surgiram de problemas reais encontrados durante o desenvolvimento. O Quadro 7 registra os principais.

Quadro 7 – Dificuldades encontradas e soluções adotadas

| Dificuldade | Causa | Solução |
|---|---|---|
| A instalação das dependências do servidor falhava. | O Python 3.14 ainda não tinha pacotes pré-compilados de algumas bibliotecas, que tentavam ser compiladas na máquina. | Uso do Python 3.13. |
| O cadastro retornava erro 500. | A biblioteca passlib, sem manutenção, era incompatível com a versão atual do bcrypt. | Uso direto da biblioteca bcrypt. |
| O botão de autorização do Swagger não obtinha o token. | O Swagger envia um formulário OAuth2, e o login recebia apenas JSON. | Nova rota `/auth/token`, no formato OAuth2, mantendo o login em JSON para o aplicativo. |
| A estação próxima aparecia sem medições. | A OpenAQ identifica cada medição pelo sensor, e o nome do poluente fica na lista de sensores da estação. | Cruzamento das medições com os sensores e busca em até dez estações próximas. |
| A busca de estações retornava erro 422. | O parâmetro de ordenação por distância não é aceito. | Remoção do parâmetro, porque a busca por coordenadas já ordena pela proximidade. |
| O aplicativo não abria no Expo Go, com erros de compatibilidade e de empacotamento. | Versões de bibliotecas escritas manualmente, incompatíveis com o SDK do Expo Go instalado. | Novo projeto criado pelo modelo oficial do Expo (SDK 57), com o código do aplicativo copiado para ele, e instalação de pacotes sempre por `npx expo install`. |
| O teclado cobria o campo de texto do chat no Android. | Com a exibição de ponta a ponta, a janela não encolhe quando o teclado aparece. | `KeyboardAvoidingView` com ajuste de espaço também no Android. |
| O chat respondia sempre que havia instabilidade na IA. | A cota gratuita diária do modelo usado (20 requisições) tinha acabado, e o erro real não era registrado. | Registro do motivo da falha, mensagens específicas, troca do modelo para `gemini-3.5-flash-lite` e cache de 30 minutos. |
| Notificações não chegavam pelo Expo Go. | O Expo Go para Android não recebe notificações remotas desde o SDK 53. | Alertas exibidos dentro do aplicativo. |
| A localização precisa seria gravada no histórico. | O servidor grava as coordenadas recebidas em cada consulta. | Arredondamento das coordenadas no aplicativo antes do envio. |

Fonte: autoria própria.

## 4.10 Testes

Os testes foram feitos em três níveis.

**Testes manuais do servidor.** Cada endpoint foi testado pelo Swagger, com dados válidos e inválidos: cadastro, login, consulta autenticada, consulta sem token, histórico, chat, alertas, relatório e troca de perfil.

**Testes manuais do aplicativo.** Cada fluxo foi executado no celular com o Expo Go: cadastro, login, permissão de localização concedida e negada, consulta, alerta, chat, histórico e troca de perfil.

**Testes isolados da lógica.** As regras que não dependem de serviços externos foram testadas com casos conhecidos:

- cálculo do IQAr: ar limpo resultando em Boa, PM2,5 de 40 µg/m³ em Moderada, PM2,5 de 60 µg/m³ em Ruim e ausência de poluentes sem índice;
- regra de alerta: onze combinações de categoria e perfil, incluindo perfis sensíveis com ar Moderado;
- relatório por dia: agrupamento pelo horário de Brasília, dias sem consulta e consultas fora do período;
- integração com o Gemini, com um cliente simulado: classificação dos erros, mensagem do chat para cada motivo e funcionamento do cache;
- arredondamento das coordenadas enviadas pelo aplicativo.

Como exemplo de resultado, a consulta no centro de São Paulo retornou a estação de Diadema, com PM10 de 21 µg/m³ e ozônio de 42 µg/m³. O PM10 está na faixa Boa (0 a 50 µg/m³, índice de 0 a 40). Por interpolação, 21/50 × 40 ≈ 17, valor igual ao índice calculado pelo sistema.

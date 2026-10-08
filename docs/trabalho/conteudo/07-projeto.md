# 5 PROJETO DO PROGRAMA

Este capítulo descreve a estrutura do AirIA: os nós do sistema, os módulos de cada parte, o modelo de dados, a interface entre o aplicativo e o servidor e as regras de negócio.

## 5.1 Arquitetura geral

O AirIA segue uma arquitetura cliente-servidor em camadas, com cinco nós que se comunicam pela rede (Figura 1). O aplicativo se comunica somente com o servidor de aplicação, por HTTP. O servidor, por sua vez, se comunica com o banco de dados e com os dois serviços externos.

[[FIGURA: Figura 1 – Arquitetura distribuída do AirIA | Inserir o arquivo docs/trabalho/diagramas/arquitetura.svg]]

O aplicativo cuida da interface, da localização e da sessão do usuário. O servidor concentra as regras de negócio, a segurança e a integração com os demais nós. O banco de dados guarda usuários, medições, alertas e conversas. A OpenAQ fornece as estações e as medições recentes, e o Gemini gera os textos e as respostas do chat.

## 5.2 Módulos do servidor

O servidor é organizado em camadas, e cada camada só conhece a camada imediatamente abaixo dela. Uma requisição entra pela camada de rotas, que chama a camada de serviços. Os serviços aplicam as regras e usam a camada de repositórios para ler e gravar no banco. O Quadro 8 descreve cada pasta do servidor.

Quadro 8 – Camadas do servidor (`backend/app`)

| Pasta | Responsabilidade |
|---|---|
| `api/routes` | Recebe as requisições HTTP e converte os erros em respostas |
| `api/deps.py` | Identifica o usuário a partir do token |
| `services` | Regras de negócio: autenticação, consulta, OpenAQ, IQAr, Gemini e alertas |
| `repositories` | Leitura e gravação no banco de dados |
| `models` | Tabelas do banco, como classes do SQLAlchemy |
| `schemas` | Formato e validação dos dados de entrada e saída |
| `core` | Configuração, conexão com o banco e segurança |

Fonte: autoria própria.

## 5.3 Módulos do aplicativo

O aplicativo segue uma divisão semelhante: as telas cuidam da apresentação, e o acesso ao servidor e aos recursos do aparelho fica em módulos separados. O Quadro 9 descreve a estrutura.

Quadro 9 – Estrutura do aplicativo (`mobile/src`)

| Pasta | Responsabilidade |
|---|---|
| `screens` | Telas de entrada, cadastro, Início, Chat, Histórico e Perfil |
| `components` | Card do resultado, faixa de alerta, gráfico e seletor de perfil |
| `api` | Chamadas ao servidor, com o token incluído automaticamente |
| `services` | Localização do aparelho |
| `contexts` | Sessão do usuário, compartilhada entre as telas |
| `navigation` | Navegação por pilha e por abas |
| `config` | Perfis de saúde e cores das categorias |

Fonte: autoria própria.

## 5.4 Modelo de dados

O banco de dados tem quatro tabelas, mostradas na Figura 2. A tabela de usuários se relaciona com as demais na proporção de um para muitos: cada usuário pode ter várias medições, vários alertas e várias conversas.

[[FIGURA: Figura 2 – Modelo de dados | Inserir o arquivo docs/trabalho/diagramas/modelo-dados.svg]]

A tabela `usuarios` guarda as contas, com o e-mail único, o *hash* da senha e o perfil de saúde. A tabela `medicoes` guarda cada consulta, com as coordenadas arredondadas, os poluentes, o índice e a categoria. As tabelas `alertas` e `conversas` guardam, respectivamente, os alertas emitidos e as perguntas e respostas do chat.

## 5.5 Interface entre o aplicativo e o servidor

O servidor expõe os endpoints do Quadro 10. Todos, exceto o cadastro, o login e a verificação de funcionamento, exigem o token JWT no cabeçalho `Authorization`.

Quadro 10 – Endpoints da API

| Método | Endereço | Função |
|---|---|---|
| GET | `/` | Verifica se o servidor está no ar |
| POST | `/auth/register` | Cadastra um usuário |
| POST | `/auth/login` | Faz o login e devolve o token (usado pelo aplicativo) |
| POST | `/auth/token` | Faz o login no formato OAuth2 (usado pelo Swagger) |
| GET | `/auth/me` | Devolve os dados do usuário conectado |
| PUT | `/auth/me/perfil` | Altera o perfil de saúde |
| GET | `/air-quality` | Consulta a qualidade do ar por latitude e longitude |
| GET | `/history` | Lista as consultas do usuário |
| GET | `/report` | Resume as consultas por dia |
| GET | `/alerts` | Lista os alertas do usuário |
| POST | `/chat` | Envia uma pergunta ao assistente |
| GET | `/chat/history` | Lista as conversas do usuário |

Fonte: autoria própria.

## 5.6 Fluxo de uma consulta

A Figura 3 mostra a sequência de uma consulta, que é o fluxo principal do sistema.

[[FIGURA: Figura 3 – Fluxo de uma consulta de qualidade do ar | Inserir o arquivo docs/trabalho/diagramas/fluxo-consulta.svg]]

O aplicativo lê a posição do celular, arredonda as coordenadas e as envia em `GET /air-quality`, com o token. O servidor valida o token, busca até dez estações da OpenAQ em um raio de 25 km e usa a primeira que tiver medições dos poluentes monitorados. Em seguida, calcula o IQAr, obtém do Gemini a interpretação e a recomendação (ou as reaproveita do cache), grava a medição e avalia o alerta. Por fim, devolve um único JSON com os poluentes, o índice, a categoria, os textos e o alerta, e o aplicativo mostra o resultado.

## 5.7 Regras de negócio

**Cálculo do IQAr.** Para cada poluente, o índice é obtido por interpolação linear dentro da faixa de concentração em que o valor se encontra. O índice geral é o maior entre os poluentes medidos, e o poluente correspondente é informado como crítico. As faixas adotadas seguem as da CETESB (CETESB, 2026b) e estão no Quadro 11.

Quadro 11 – Faixas de concentração usadas no cálculo do IQAr (µg/m³)

| Categoria (índice) | PM2,5 (24 h) | PM10 (24 h) | O3 (8 h) | NO2 (1 h) |
|---|---|---|---|---|
| Boa (0 a 40) | 0 a 25 | 0 a 50 | 0 a 100 | 0 a 200 |
| Moderada (41 a 80) | 25 a 50 | 50 a 100 | 100 a 130 | 200 a 240 |
| Ruim (81 a 120) | 50 a 75 | 100 a 150 | 130 a 160 | 240 a 320 |
| Muito Ruim (121 a 200) | 75 a 125 | 150 a 250 | 160 a 200 | 320 a 1130 |
| Péssima (acima de 200) | acima de 125 | acima de 250 | acima de 200 | acima de 1130 |

Fonte: autoria própria, com base em CETESB (2026b).

**Alertas.** Os perfis asmático, idoso e criança recebem alerta a partir da categoria Moderada, e os perfis geral e atleta a partir da categoria Ruim. O nível do alerta é perigo nas categorias Muito Ruim e Péssima e atenção nas demais. Para não repetir o mesmo aviso a cada consulta, um alerta do mesmo nível só é gravado novamente depois de três horas. A resposta da consulta indica se o alerta é novo, e o aplicativo usa essa informação para decidir se mostra a janela de aviso ou apenas a faixa colorida na tela.

**Cache da IA.** A interpretação gerada para uma combinação de local, categoria e perfil é reaproveitada por 30 minutos. Respostas com falha não são guardadas, para que a IA seja chamada novamente na consulta seguinte.

**Relatório.** As consultas dos últimos dias são agrupadas por data no horário de Brasília. Para cada dia, o sistema calcula o índice médio, o índice máximo e o número de consultas. Dias sem consulta aparecem com total zero, para que o gráfico mostre sempre os sete dias.

## 5.8 Segurança e privacidade

As senhas são gravadas apenas como *hash* bcrypt, os tokens JWT valem por 24 horas e as chaves da OpenAQ e do Gemini ficam somente no servidor. Para preservar a privacidade, o aplicativo arredonda a latitude e a longitude para duas casas decimais (cerca de 1 km) antes de enviá-las. Como as estações são buscadas em um raio de 25 km, o resultado não muda, e o histórico não guarda a posição exata do usuário. O nome do lugar exibido na tela vem da geocodificação do sistema operacional do celular, e a posição precisa não é enviada ao servidor.

## 5.9 Tolerância a falhas

O Quadro 12 mostra como o sistema reage a cada tipo de falha.

Quadro 12 – Tratamento de falhas

| Falha | Comportamento |
|---|---|
| Gemini sem resposta ou sem cota | Textos locais na consulta; o chat informa o motivo |
| OpenAQ lenta ou indisponível | Erro 502 com explicação após 15 segundos |
| Nenhuma estação com dados em 25 km | Erro 502 com explicação |
| Localização negada ou bloqueada | Explicação e botão para permitir ou abrir as configurações |
| GPS sem resposta em 15 segundos | Uso da última posição de até uma hora |
| Sem conexão com o servidor | Mensagem para verificar a rede |
| Token expirado ou inválido | Erro 401 |

Fonte: autoria própria.

## 5.10 Limitações conhecidas

- O cálculo supõe concentrações em µg/m³, mas algumas estações informam gases em ppm. No CO, as faixas da CETESB, definidas em ppm, foram adotadas como 9.000 a 15.000 µg/m³, quando 1 ppm equivale a cerca de 1,15 mg/m³ a 25 °C. Verificar a unidade de cada sensor fica como melhoria futura.
- O índice usa a medição mais recente de cada sensor, e não as médias de 24 ou 8 horas da definição oficial. É, portanto, uma estimativa do momento.
- O cache da IA fica na memória do servidor: é perdido ao reiniciar e não é compartilhado entre cópias do servidor.
- Os alertas só aparecem com o aplicativo aberto (seção 3.5), e regiões sem estação a até 25 km não recebem resultado.

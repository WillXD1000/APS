# 3 FUNDAMENTOS DAS TECNOLOGIAS PARA DISPOSITIVOS MÓVEIS ESCOLHIDAS

Este capítulo apresenta os conceitos gerais das tecnologias usadas no aplicativo AirIA. A seção 3.1 discute as abordagens de desenvolvimento para celulares. As seções 3.2 a 3.5 tratam das tecnologias do aplicativo. As seções 3.6 e 3.7 cobrem a comunicação com o servidor e as tecnologias do lado do servidor, e a seção 3.8 relaciona tudo aos conceitos de sistemas distribuídos.

## 3.1 Abordagens de desenvolvimento para dispositivos móveis

Há três formas principais de construir um aplicativo para celular. No desenvolvimento nativo, o aplicativo é escrito na linguagem oficial de cada sistema operacional, como Kotlin ou Java no Android e Swift no iOS. Essa abordagem oferece o melhor acesso aos recursos do aparelho, mas exige manter dois códigos diferentes. Nos aplicativos web e híbridos, a interface é feita com HTML, CSS e JavaScript e exibida dentro de um navegador ou de um componente de navegador embutido. O código é único, mas a aparência e o desempenho nem sempre se igualam aos de um aplicativo nativo.

A terceira abordagem é o desenvolvimento multiplataforma com componentes nativos. O código é escrito uma vez, em uma linguagem comum, e o framework o traduz para os componentes de interface reais de cada sistema. O AirIA usa essa abordagem por meio do React Native. Com uma única base de código em JavaScript, o aplicativo pode ser executado em Android e iOS e usa os botões, listas e campos de texto nativos de cada plataforma.

## 3.2 React Native

O React Native é um framework de código aberto criado pelo Facebook, hoje Meta, e lançado publicamente em 2015. Ele leva para o celular o modelo de programação da biblioteca React, usada em aplicações web (REACT NATIVE, 2026). A interface é descrita por componentes, que são funções JavaScript que recebem dados e devolvem a estrutura da tela. Essa estrutura é escrita em JSX, uma extensão do JavaScript que permite misturar código e marcação. No React Native, em vez de elementos HTML como `div` e `p`, usam-se componentes como `View`, `Text`, `TextInput`, `ScrollView` e `FlatList`, que são convertidos nos elementos nativos correspondentes.

O comportamento dos componentes é controlado por estado. Quando o estado muda, por exemplo quando chega a resposta do servidor, o React redesenha apenas as partes da tela afetadas. O AirIA usa os hooks principais do React para isso:

- `useState`, para guardar dados da tela, como o resultado da consulta e as mensagens de erro;
- `useEffect`, para executar ações em momentos específicos, como consultar a qualidade do ar assim que a tela abre;
- `useCallback` e `useRef`, para manter funções estáveis entre redesenhos e impedir que duas consultas rodem ao mesmo tempo;
- `useContext`, para compartilhar entre todas as telas os dados do usuário que está conectado.

A versão usada no projeto é o React Native 0.86, com o React 19.2. Nas versões recentes, o React Native usa a chamada nova arquitetura, em que a comunicação entre o JavaScript e o código nativo é feita de forma mais direta e eficiente do que no modelo anterior, baseado em mensagens serializadas.

## 3.3 Expo

O Expo é uma plataforma construída sobre o React Native que simplifica a criação, a execução e a publicação de aplicativos (EXPO, 2026a). Ela oferece três elementos usados neste trabalho:

- o **Expo SDK**, um conjunto de bibliotecas que dão acesso a recursos do aparelho, como localização, ícones e fontes, já testadas em conjunto;
- o **Expo CLI**, ferramenta de linha de comando que inicia o servidor de desenvolvimento (`npx expo start`) e gera um código QR para abrir o aplicativo no celular;
- o **Expo Go**, aplicativo disponível nas lojas que executa o projeto em desenvolvimento sem que seja necessário compilar um pacote Android ou iOS.

Cada versão do Expo SDK é associada a uma versão específica do React Native e das bibliotecas nativas. O projeto usa o SDK 57, lançado em junho de 2026 com o React Native 0.86 (EXPO, 2026b). O Expo Go instalado pela loja executa apenas projetos da versão de SDK mais recente. Por isso, as dependências do projeto devem ser instaladas com o comando `npx expo install`, que escolhe automaticamente as versões compatíveis com o SDK. Essa regra teve importância prática no desenvolvimento, como mostra o capítulo 4.

## 3.4 Bibliotecas usadas no aplicativo

**React Navigation.** É a biblioteca de navegação entre telas (REACT NAVIGATION, 2026). O AirIA combina dois tipos de navegação. Antes do login, uma pilha (*stack*) alterna entre as telas de entrada e de cadastro. Depois do login, uma barra de abas na parte inferior dá acesso às telas Início, Chat, Histórico e Perfil.

**AsyncStorage.** É um armazenamento local do tipo chave-valor, persistente entre as aberturas do aplicativo. O AirIA o usa para guardar o token de autenticação e os dados do usuário. Assim, quem já entrou não precisa digitar a senha a cada uso.

**Axios.** É uma biblioteca de requisições HTTP. O aplicativo cria um único cliente configurado com o endereço do servidor e com um *interceptor*, função executada antes de cada requisição, que acrescenta o token de autenticação ao cabeçalho (AXIOS, 2026).

**expo-location.** É a biblioteca do Expo que dá acesso à localização do aparelho (EXPO, 2026c). Ela permite verificar e pedir a permissão de localização, ler a posição atual, aproveitar a última posição conhecida e obter o nome do lugar a partir das coordenadas, operação chamada de geocodificação reversa.

**@expo/vector-icons.** É um conjunto de ícones vetoriais usado na barra de abas e nos cartões de escolha do perfil de saúde.

## 3.5 Recursos do dispositivo e particularidades do Android

**Permissões em tempo de execução.** Desde o Android 6.0, o acesso a dados sensíveis, como a localização, precisa ser autorizado pelo usuário enquanto o aplicativo está em uso, e não apenas na instalação. O usuário pode negar o pedido ou bloquear novos pedidos. O aplicativo precisa tratar os três casos: permissão concedida, negada e bloqueada. No último caso, a única saída é levar o usuário às configurações do aparelho.

**Localização.** O celular combina várias fontes para estimar a posição, como GPS, redes Wi-Fi e antenas de telefonia. Uma leitura precisa pode levar alguns segundos, principalmente em ambientes fechados. Por isso, é comum aproveitar a última posição conhecida, quando ela é recente, e limitar o tempo de espera da leitura atual.

**Exibição de ponta a ponta (*edge-to-edge*).** Nas versões recentes do Android, e por padrão no Expo desde o SDK 53, o aplicativo desenha a tela inteira, inclusive atrás das barras do sistema. Uma consequência é que a janela não encolhe quando o teclado aparece. É o próprio aplicativo que precisa abrir espaço para que o campo de texto não fique escondido, o que no React Native é feito com o componente `KeyboardAvoidingView`.

**Notificações.** O Expo Go para Android não recebe notificações *push* remotas desde o SDK 53. Esse recurso exige uma versão compilada do aplicativo (EXPO, 2026d). Por esse motivo, os alertas do AirIA são exibidos dentro do aplicativo.

## 3.6 Comunicação entre o aplicativo e o servidor

**Modelo cliente-servidor.** No modelo cliente-servidor, o cliente faz pedidos e o servidor executa o serviço e devolve uma resposta (COULOURIS et al., 2013). No AirIA, o aplicativo é o cliente e o servidor de aplicação concentra as regras do sistema.

**HTTP e REST.** A comunicação usa o protocolo HTTP no estilo arquitetural REST, descrito por Fielding (2000). Nesse estilo, cada recurso tem um endereço, como `/air-quality` ou `/history`, e as operações são expressas pelos métodos do HTTP: `GET` para consultar, `POST` para criar e `PUT` para alterar. Cada requisição carrega todas as informações necessárias para ser atendida, sem depender de uma sessão guardada no servidor.

**JSON.** Os dados trafegam no formato JSON, um formato de texto legível que representa objetos e listas. Ele é usado de forma nativa pelo JavaScript do aplicativo e é facilmente convertido em objetos pelo Python do servidor.

**JWT.** A autenticação usa o JSON Web Token (JWT), padrão definido na RFC 7519 (JONES; BRADLEY; SAKIMURA, 2015). Depois do login, o servidor devolve um token assinado que contém o identificador do usuário e a data de expiração. O aplicativo envia esse token no cabeçalho `Authorization` de cada requisição. Como a assinatura é verificada pelo servidor a cada pedido, não é preciso guardar sessões, o que combina com o estilo REST.

## 3.7 Tecnologias do servidor e serviços externos

Embora este capítulo trate das tecnologias móveis, o aplicativo depende de um servidor e de serviços externos. Eles são apresentados aqui de forma resumida.

**Python e FastAPI.** O servidor é escrito em Python com o FastAPI, um framework para construção de APIs (FASTAPI, 2026). O FastAPI usa as anotações de tipo do Python para validar automaticamente os dados de entrada, por meio da biblioteca Pydantic, e gera uma documentação interativa da API, o Swagger, acessível pelo navegador. O servidor é executado pelo Uvicorn, que atende várias requisições ao mesmo tempo.

**PostgreSQL e SQLAlchemy.** Os dados ficam no PostgreSQL, um sistema gerenciador de banco de dados relacional de código aberto (POSTGRESQL GLOBAL DEVELOPMENT GROUP, 2026). O acesso é feito pelo SQLAlchemy, biblioteca de mapeamento objeto-relacional (ORM) que representa as tabelas como classes Python (SQLALCHEMY, 2026). As senhas são guardadas apenas na forma de *hash*, calculado pelo algoritmo bcrypt.

**OpenAQ.** A OpenAQ é uma plataforma aberta que reúne medições de qualidade do ar de estações de vários países e as disponibiliza por uma API REST (OPENAQ, 2026). Cada local de monitoramento possui sensores, e cada sensor mede um parâmetro, como PM2,5 ou ozônio. O acesso exige uma chave gratuita.

**Google Gemini.** O Gemini é uma família de modelos de linguagem de grande escala (LLM) do Google, acessível por uma API (GOOGLE, 2026a). Um modelo de linguagem recebe um texto de instrução, chamado *prompt*, e gera um texto de resposta. O AirIA usa o modelo `gemini-3.5-flash-lite`, da categoria gratuita. Nessa categoria, o uso é limitado por uma cota diária de requisições, contada separadamente para cada modelo e para cada projeto (GOOGLE, 2026b).

## 3.8 Conceitos de sistemas distribuídos aplicados

Coulouris et al. (2013) apontam desafios que todo sistema distribuído precisa enfrentar. O Quadro 1 mostra como cada um aparece no AirIA.

Quadro 1 – Desafios de sistemas distribuídos no AirIA

| Desafio | Como aparece no AirIA |
|---|---|
| Heterogeneidade | Nós em linguagens e plataformas diferentes: JavaScript no celular, Python no servidor, SQL no banco e serviços externos de terceiros. |
| Abertura | Comunicação por padrões abertos (HTTP, REST, JSON, JWT), que permitem trocar qualquer nó sem alterar os outros. |
| Segurança | Senhas com *hash* bcrypt, autenticação por JWT e chaves dos serviços externos guardadas somente no servidor. |
| Escalabilidade | Servidor sem sessão, o que permite executar várias cópias dele, e cache das respostas da IA para reduzir chamadas externas. |
| Tratamento de falhas | Textos locais quando o Gemini falha, mensagens explicativas quando a OpenAQ não responde e tempo-limite na leitura do GPS. |
| Concorrência | O servidor atende várias requisições ao mesmo tempo, e o cache compartilhado é protegido por uma trava. |
| Transparência | O aplicativo faz uma única requisição e não sabe de onde vêm os dados nem quais serviços foram chamados. |

Fonte: autoria própria, com base em Coulouris et al. (2013).

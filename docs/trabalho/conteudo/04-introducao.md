# 2 INTRODUÇÃO

A qualidade do ar nas cidades é um tema de saúde pública. Segundo as diretrizes de qualidade do ar publicadas pela Organização Mundial da Saúde em 2021, a exposição à poluição atmosférica está associada a cerca de sete milhões de mortes prematuras por ano no mundo, principalmente por doenças respiratórias e cardiovasculares (WORLD HEALTH ORGANIZATION, 2021). Os poluentes de maior impacto são o material particulado fino (PM2,5) e inalável (PM10), o ozônio (O3), o dióxido de nitrogênio (NO2) e o monóxido de carbono (CO), gerados em grande parte pelo tráfego de veículos e pela atividade industrial.

No Brasil, os padrões de qualidade do ar são definidos pela Resolução CONAMA nº 491, de 2018, que estabelece limites de concentração para esses poluentes e orienta a divulgação dos dados à população (BRASIL, 2018). No estado de São Paulo, a CETESB opera uma rede de estações automáticas e divulga diariamente o Índice de Qualidade do Ar (IQAr). O índice resume as medições em um único número, associado a uma categoria: Boa, Moderada, Ruim, Muito Ruim ou Péssima (CETESB, 2026a, 2026b). O governo federal também disponibiliza o aplicativo MonitorAr, que reúne dados de estações oficiais do país (BRASIL, 2025).

Mesmo com essas fontes, permanece uma distância entre o dado e a decisão do dia a dia. O índice informa a categoria, mas não diz o que ela significa para cada pessoa. Um ar Moderado pode não exigir nenhum cuidado de um adulto saudável e, ao mesmo tempo, ser motivo de atenção para uma pessoa asmática. Além disso, a consulta costuma exigir que o usuário saiba qual estação fica perto dele e como interpretar os valores de cada poluente.

## 2.1 A proposta do AirIA

O AirIA é um aplicativo para celular que procura reduzir essa distância. Ao ser aberto, ele lê a localização do aparelho, encontra a estação de monitoramento mais próxima em um raio de 25 km e calcula o IQAr a partir das medições mais recentes. Em seguida, um modelo de linguagem (Google Gemini) recebe os valores, a categoria e o perfil de saúde do usuário e devolve duas frases em português: uma explicando como está o ar e outra com uma recomendação prática.

O aplicativo oferece também um chat, no qual o usuário faz perguntas como "posso correr ao ar livre hoje?" e recebe uma resposta que leva em conta a sua última consulta. Quando o ar exige atenção para o perfil escolhido, um alerta aparece na tela. Todas as consultas ficam registradas e podem ser vistas em um gráfico dos últimos sete dias.

Os perfis de saúde disponíveis são geral, asmático, idoso, atleta e criança. Eles influenciam tanto o texto gerado pela inteligência artificial quanto o momento em que o alerta é emitido. Os perfis considerados sensíveis (asmático, idoso e criança) são alertados a partir da categoria Moderada. Os demais são alertados a partir da categoria Ruim.

## 2.2 O AirIA como sistema distribuído

Tanenbaum e Van Steen (2007) definem um sistema distribuído como um conjunto de computadores independentes que se apresenta aos usuários como um sistema único e coerente. O AirIA segue esse modelo. Para quem usa o aplicativo, há apenas uma tela que mostra a qualidade do ar. Por trás dela, porém, cinco nós independentes cooperam pela rede:

- o aplicativo móvel, que roda no celular do usuário;
- o servidor de aplicação, desenvolvido em Python com o framework FastAPI;
- o servidor de banco de dados PostgreSQL;
- a plataforma OpenAQ, que fornece as medições de qualidade do ar;
- a API do Google Gemini, que fornece o modelo de linguagem.

O aplicativo conversa apenas com o servidor do AirIA. É o servidor que consulta a OpenAQ, calcula o índice, chama o Gemini, aplica a regra de alertas e grava o histórico. Essa separação esconde do aplicativo a origem dos dados, protege as chaves de acesso aos serviços externos, que ficam somente no servidor, e permite que cada parte seja substituída ou escalada sem afetar as demais. O sistema também foi construído para continuar funcionando quando um serviço externo falha: se o Gemini não responder, o servidor usa textos locais baseados na categoria do índice, e o usuário continua recebendo uma orientação.

## 2.3 Organização deste trabalho

O capítulo 3 apresenta os fundamentos das tecnologias móveis escolhidas e, de forma resumida, as tecnologias do servidor com as quais o aplicativo se comunica. O capítulo 4 descreve o plano de desenvolvimento, com requisitos, ferramentas, etapas e dificuldades encontradas. O capítulo 5 detalha o projeto do programa: arquitetura, módulos, modelo de dados e regras de negócio. O capítulo 6 traz os trechos de código mais importantes, e o capítulo 7 mostra o programa em funcionamento. Ao final estão as referências bibliográficas.

# 1 OBJETIVO E MOTIVAÇÃO DO TRABALHO

## 1.1 Objetivo geral

Desenvolver uma aplicação distribuída para dispositivos móveis, chamada AirIA, que informa a qualidade do ar no local onde o usuário está e transforma os indicadores técnicos de poluição em explicações e recomendações em linguagem simples, personalizadas pelo perfil de saúde de cada pessoa, com o apoio de inteligência artificial generativa.

## 1.2 Objetivos específicos

- Obter a localização do celular e consultar, a partir dela, as medições da estação de monitoramento mais próxima em uma base pública de dados de qualidade do ar.
- Calcular o Índice de Qualidade do Ar (IQAr) e a sua categoria (Boa, Moderada, Ruim, Muito Ruim ou Péssima) a partir das concentrações de poluentes.
- Integrar um modelo de linguagem para interpretar o resultado, gerar uma recomendação prática para o perfil do usuário e responder perguntas em um chat.
- Emitir alertas quando a qualidade do ar exigir atenção, considerando que pessoas asmáticas, idosas e crianças são mais sensíveis à poluição.
- Guardar o histórico de consultas em um banco de dados e apresentá-lo em um gráfico dos últimos dias.
- Organizar a solução em nós independentes (aplicativo, servidor, banco de dados e serviços externos) que se comunicam pela rede, aplicando conceitos de sistemas distribuídos.

## 1.3 Motivação

A poluição do ar é um dos problemas ambientais urbanos que mais afetam a saúde da população. Os dados existem: órgãos como a CETESB mantêm redes de estações de monitoramento, e plataformas abertas reúnem essas medições. O problema é a forma como eles chegam ao cidadão. Um valor como "PM10 = 21 µg/m³" não diz, para a maioria das pessoas, se é seguro levar uma criança ao parque ou sair para correr.

O grupo escolheu esse tema por reunir três assuntos estudados no curso em um problema real. O primeiro é o desenvolvimento para dispositivos móveis, já que o celular é o meio mais direto de levar uma informação do lugar onde a pessoa está. O segundo são os sistemas distribuídos, porque a aplicação depende de vários computadores independentes trabalhando juntos. O terceiro é a inteligência artificial, que hoje permite converter dados técnicos em uma conversa acessível.

Também pesou a possibilidade de apresentar um sistema que funciona com dados reais, e não com valores simulados. Durante o desenvolvimento, a consulta feita no centro de São Paulo retornou a estação de Diadema, com PM10 de 21 µg/m³ e ozônio de 42 µg/m³, o que resultou em índice 17 e categoria Boa. A partir desse resultado, o aplicativo explicou em português que o ar estava bom e que era possível praticar atividades ao ar livre. Essa passagem do número para a orientação prática é o que o trabalho busca demonstrar.

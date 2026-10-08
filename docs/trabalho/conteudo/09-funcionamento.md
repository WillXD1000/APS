# 7 APRESENTAÇÃO DO PROGRAMA EM FUNCIONAMENTO

Este capítulo mostra o AirIA em execução, com todas as funcionalidades pedidas e as extras. O servidor roda em um computador, junto com o banco de dados PostgreSQL. Na apresentação em computador, o aplicativo é executado no emulador Android ou no celular com a tela espelhada no computador. Em ambos os casos, ele se conecta ao servidor pela rede local. As figuras foram capturadas nessa execução.

## 7.1 Servidor e documentação da API

Com o servidor em execução, a documentação interativa gerada pelo FastAPI fica disponível no navegador. Ela lista todos os endpoints e permite testá-los.

[[FIGURA: Figura 4 – Documentação interativa da API (Swagger) | Capturar a página http://localhost:8000/docs com a lista de endpoints]]

## 7.2 Cadastro e escolha do perfil de saúde

No cadastro, o usuário informa nome, e-mail e senha e escolhe o perfil de saúde. Cada perfil aparece em um cartão com ícone e descrição, explicando quando os alertas são emitidos.

[[FIGURA: Figura 5 – Tela de cadastro com a escolha do perfil de saúde | Capturar a tela de cadastro com os campos preenchidos e um perfil selecionado]]

## 7.3 Login

Depois do cadastro, o usuário entra com e-mail e senha. A sessão fica salva no aparelho, e nas aberturas seguintes o aplicativo vai direto para a tela Início.

[[FIGURA: Figura 6 – Tela de login | Capturar a tela de login]]

## 7.4 Permissão de localização

Na primeira abertura da tela Início, o sistema operacional pede a permissão de localização. Se o usuário negar, a tela explica o motivo e oferece o botão para permitir. Se a permissão estiver bloqueada, o botão leva às configurações do aparelho.

[[FIGURA: Figura 7 – Pedido de permissão de localização | Capturar a janela do sistema pedindo a permissão de localização]]

[[FIGURA: Figura 8 – Tela Início com a permissão negada | Negar a permissão e capturar a mensagem com o botão Permitir localização]]

## 7.5 Consulta da qualidade do ar

Com a permissão concedida, o aplicativo lê a posição e consulta o servidor automaticamente. A tela mostra o lugar onde o usuário está, a estação mais próxima, o índice, a categoria com a cor correspondente, a interpretação e a recomendação geradas pela IA e os poluentes medidos. O botão Atualizar, ou o gesto de puxar a tela para baixo, refaz a consulta.

[[FIGURA: Figura 9 – Tela Início com o resultado da consulta | Capturar a tela Início com o card completo, incluindo os textos da IA]]

## 7.6 Alerta por perfil de saúde

Quando a qualidade do ar exige atenção para o perfil do usuário, aparece uma faixa de alerta acima do resultado. Se o alerta for novo, o aplicativo também exibe uma janela de aviso.

[[FIGURA: Figura 10 – Alerta na tela Início | Com o perfil Asmático, capturar a janela de aviso e a faixa de alerta. Se o ar estiver Bom, usar no emulador as coordenadas de uma região com ar Moderado ou pior]]

## 7.7 Chat ambiental

No chat, o usuário faz perguntas em linguagem natural. A resposta considera a última consulta do usuário. O campo de texto acompanha o teclado, e a conversa rola até a última mensagem.

[[FIGURA: Figura 11 – Chat ambiental | Capturar uma pergunta como "Posso correr ao ar livre hoje?" e a resposta]]

## 7.8 Histórico e gráfico

A tela Histórico mostra o índice médio de cada um dos últimos sete dias em um gráfico de barras, colorido conforme a categoria, seguido dos alertas recentes e da lista de consultas.

[[FIGURA: Figura 12 – Tela Histórico com o gráfico dos últimos sete dias | Capturar a tela Histórico depois de algumas consultas]]

## 7.9 Perfil do usuário

A tela Perfil mostra os dados do usuário e permite trocar o perfil de saúde. A troca passa a valer para as próximas recomendações e alertas.

[[FIGURA: Figura 13 – Tela Perfil com a troca do perfil de saúde | Capturar a tela Perfil com um perfil diferente selecionado e o botão Salvar perfil]]

## 7.10 Funcionalidades pedidas e extras

O Quadro 13 relaciona as funcionalidades com as figuras deste capítulo. As funcionalidades marcadas como extras vão além do requisito básico de uma aplicação distribuída para dispositivos móveis com informações ambientais urbanas.

Quadro 13 – Funcionalidades demonstradas

| Funcionalidade | Tipo | Figura |
|---|---|---|
| Cadastro, login e sessão | Básica | 5 e 6 |
| Consulta da qualidade do ar pela localização | Básica | 7 e 9 |
| Cálculo do IQAr e da categoria | Básica | 9 |
| Histórico de consultas | Básica | 12 |
| Interpretação e recomendação por IA | Extra | 9 |
| Chat ambiental com IA | Extra | 11 |
| Alertas por perfil de saúde | Extra | 10 |
| Gráfico dos últimos sete dias | Extra | 12 |
| Escolha e troca do perfil de saúde | Extra | 5 e 13 |
| Tratamento de erros e textos locais quando a IA falha | Extra | 8 |
| Documentação interativa da API | Extra | 4 |

Fonte: autoria própria.

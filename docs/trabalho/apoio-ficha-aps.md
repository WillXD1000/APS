# Apoio para a ficha de Atividades Práticas Supervisionadas

A ficha oficial da APS deve ser preenchida pela equipe, em ordem cronológica, conforme a orientação da professora. Esta lista reúne as atividades registradas no repositório, por data, no horário de Brasília. Ela serve de ponto de partida.

Duas observações:

- O repositório só registra o que virou código ou documento. Pesquisa, reuniões, estudo das tecnologias, testes no celular, escrita do trabalho e preparação da apresentação também são atividades da APS e devem entrar na ficha com as datas reais.
- **As horas não estão aqui de propósito.** Preencham a ficha com as horas que a equipe de fato dedicou a cada atividade.

| Data | Atividade registrada no repositório |
|---|---|
| 06/10/2026 | Proposta do projeto, arquitetura do sistema distribuído e plano de desenvolvimento (`docs/`) |
| 06/10/2026 | Etapa 1: servidor FastAPI em camadas, banco PostgreSQL e autenticação com JWT |
| 06/10/2026 | Correção da autenticação: troca da biblioteca passlib pelo bcrypt |
| 06/10/2026 | Etapa 2: integração com a OpenAQ e cálculo do IQAr |
| 06/10/2026 | Correções da integração: login no formato OAuth2 para o Swagger, leitura dos sensores e parâmetro de ordenação da OpenAQ |
| 06/10/2026 | Etapa 3: integração com o Gemini (interpretação, recomendação e chat) |
| 07/10/2026 | Etapa 4: aplicativo em React Native com Expo (telas, navegação e sessão) |
| 07/10/2026 | Ajustes de compatibilidade do Expo e recriação do aplicativo pelo modelo oficial do SDK 57 |
| 07/10/2026 | Etapa 5: alertas por perfil de saúde, relatório com gráfico, escolha do perfil e correção do teclado |
| 07/10/2026 | Localização do celular na tela Início, com arredondamento das coordenadas |
| 07/10/2026 | Integração com o Gemini: troca do modelo, registro do motivo das falhas e cache |
| 07/10/2026 | Trabalho escrito (`docs/trabalho/`) |

Para ver o histórico completo, com horários, rode na pasta do repositório:

```
git log --reverse --date=format-local:"%d/%m/%Y %H:%M" --pretty="%ad  %s"
```

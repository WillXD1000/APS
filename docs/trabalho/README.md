# Trabalho escrito da APS

O texto de cada seção fica em `conteudo/`, e o script `gerar_docx.py` monta o arquivo `APS-AirIA.docx` já formatado. A versão final é exportada para PDF pelo Word.

## Estrutura

| Arquivo | Seção do documento da APS |
|---|---|
| `conteudo/01-capa.md` | 1. Capa (dados em `Chave: valor`) |
| (gerado) | 2. Índice (sumário automático) |
| `conteudo/03-objetivo.md` | 3. Objetivo e motivação |
| `conteudo/04-introducao.md` | 4. Introdução |
| `conteudo/05-fundamentos.md` | 5. Fundamentos das tecnologias móveis |
| `conteudo/06-plano.md` | 6. Plano de desenvolvimento |
| `conteudo/07-projeto.md` | 7. Projeto do programa |
| `conteudo/08-codigo.md` | 8. Relatório com as linhas de código |
| `conteudo/09-funcionamento.md` | 9. Programa em funcionamento |
| `conteudo/10-bibliografia.md` | 10. Bibliografia |
| `diagramas/*.svg` | Figuras 1 a 3 (arquitetura, modelo de dados e fluxo da consulta) |
| `apoio-ficha-aps.md` | Atividades por data, para ajudar a preencher a ficha da APS |

Formatação aplicada pelo gerador: A4, Arial 12, espaçamento 1,5 em todo o texto, margens esquerda e direita de 2,5 cm, superior de 3 cm e inferior de 2 cm, parágrafos justificados com recuo de 1,25 cm, cada capítulo em página nova e número da página no canto superior direito a partir do primeiro capítulo.

## Gerar o .docx

Depois de mudar qualquer arquivo de `conteudo/`, gere o documento de novo (Python 3.9 ou superior, sem instalar nada):

```
cd docs/trabalho
python gerar_docx.py --estimar
```

O script também confere se os trechos do capítulo de código continuam iguais aos arquivos do repositório e avisa se algum mudou. A estimativa de páginas é aproximada: a contagem que vale é a do Word.

## Finalizar no Word

1. Abra o `APS-AirIA.docx`. O Word vai perguntar se deseja atualizar os campos: responda **Sim**. Isso monta o sumário e os números das páginas.
2. **Figuras 1 a 3:** em cada caixa tracejada do capítulo 5, apague o texto "[Inserir aqui: ...]" e use **Inserir > Imagens** com o arquivo `.svg` indicado (pasta `diagramas`). Ajuste a largura para 16 cm.
3. **Figuras 4 a 13:** tire as capturas de tela indicadas no capítulo 7 e insira cada uma na caixa correspondente.
4. Depois de inserir as imagens, atualize o sumário: clique com o botão direito sobre ele > **Atualizar campo** > **Atualizar o índice inteiro**.
5. Exporte: **Arquivo > Salvar como > PDF**.

Para mostrar o aplicativo no computador, há duas opções:
- emulador Android do Android Studio, com o Expo Go instalado no emulador;
- celular com a tela espelhada no computador, por exemplo com o `scrcpy`.

Se editar o texto direto no Word, lembre que o `.docx` é substituído quando o gerador roda de novo. Para mudanças de texto, prefira editar os arquivos de `conteudo/`. Insira as imagens no Word só na versão final.

## Conferência antes de imprimir

| Seção | Limite do documento |
|---|---|
| Objetivo e motivação | 1 a 2 páginas |
| Introdução | 2 a 4 páginas |
| Fundamentos | 4 a 8 páginas |
| Plano de desenvolvimento | 5 a 15 páginas |
| Projeto do programa | 3 a 8 páginas |
| Linhas de código | até 10 páginas |

Confira também:
- capa com curso, tema e alunos com RA;
- todas as figuras inseridas, sem nenhuma caixa "[Inserir aqui: ...]";
- sumário atualizado depois de inserir as imagens;
- grupo de 3 alunos aprovado pela coordenação auxiliar (o documento pede 4);
- ficha de Atividades Práticas Supervisionadas preenchida (ver `apoio-ficha-aps.md`);
- impressão em A4, encadernada em espiral com capa transparente.

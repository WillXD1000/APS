#!/usr/bin/env python3
"""Gera o trabalho escrito da APS (APS-AirIA.docx) a partir de conteudo/*.md.

Usa somente a biblioteca padrão do Python, então roda em qualquer máquina com
Python 3.9 ou superior:

    python gerar_docx.py            # gera o .docx
    python gerar_docx.py --estimar  # gera e mostra uma estimativa de páginas

Formatação aplicada (regras do documento da APS e ABNT):
    - papel A4; Arial 12; espaçamento 1,5 em todo o texto;
    - margens esquerda e direita de 2,5 cm; superior 3 cm e inferior 2 cm (ABNT);
    - parágrafos justificados com recuo de 1,25 cm na primeira linha;
    - cada capítulo começa em página nova;
    - número da página no canto superior direito, a partir do primeiro capítulo
      (a contagem inclui a capa e o sumário, que não exibem o número);
    - sumário automático (o Word pede para atualizar os campos ao abrir).

Marcações aceitas nos arquivos .md:
    # Título de capítulo   ## Seção   ### Subseção
    parágrafos, listas com "- " ou "1. ", tabelas com "|", blocos de código com ```,
    **negrito**, *itálico*, `código` (impresso em Arial, como o restante),
    legendas que começam com "Quadro N –", "Figura N –" ou "Código N –",
    linhas que começam com "Fonte:",
    [[FIGURA: Figura N – Legenda | instrução]] para o espaço de uma figura.
"""

from __future__ import annotations

import datetime as _dt
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

BASE = Path(__file__).resolve().parent
RAIZ = BASE.parent.parent
CONTEUDO = BASE / "conteudo"
SAIDA = BASE / "APS-AirIA.docx"

CAPA = "01-capa.md"
CAPITULOS = [
    "03-objetivo.md",
    "04-introducao.md",
    "05-fundamentos.md",
    "06-plano.md",
    "07-projeto.md",
    "08-codigo.md",
    "09-funcionamento.md",
    "10-bibliografia.md",
]
BIBLIOGRAFIA = "10-bibliografia.md"

# Limites de páginas definidos pelo documento da APS (mínimo, máximo).
LIMITES = {
    "03-objetivo.md": (1, 2),
    "04-introducao.md": (2, 4),
    "05-fundamentos.md": (4, 8),
    "06-plano.md": (5, 15),
    "07-projeto.md": (3, 8),
    "08-codigo.md": (0, 10),
}

# Medidas em twips (1 cm = 567 twips).
LARGURA_PAGINA, ALTURA_PAGINA = 11906, 16838
MARGEM_SUP, MARGEM_INF, MARGEM_ESQ, MARGEM_DIR = 1701, 1134, 1417, 1417
LARGURA_TEXTO = LARGURA_PAGINA - MARGEM_ESQ - MARGEM_DIR  # 9072 (16 cm)
RECUO_PRIMEIRA_LINHA = 709  # 1,25 cm
LINHA_1_5 = 360  # espaçamento 1,5

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

LEGENDA_RE = re.compile(r"^(Quadro|Figura|Tabela|Código)\s+\d+\s+[–-]\s+")
FIGURA_RE = re.compile(r"^\[\[FIGURA:\s*(.+?)\s*\|\s*(.+?)\s*\]\]$")
INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\s][^*]*?\*)")


# --------------------------------------------------------------------------- #
# Construção de XML
# --------------------------------------------------------------------------- #
def _t(texto: str) -> str:
    return f'<w:t xml:space="preserve">{escape(texto)}</w:t>'


def runs(texto: str, negrito: bool = False, italico: bool = False) -> str:
    """Converte texto com **negrito**, *itálico* e `código` em runs do Word."""
    saida = []
    for parte in INLINE_RE.split(texto):
        if not parte:
            continue
        b, i, conteudo = negrito, italico, parte
        if parte.startswith("**") and parte.endswith("**") and len(parte) > 4:
            # O negrito pode conter itálico: trata o conteúdo de novo.
            saida.append(runs(parte[2:-2], negrito=True, italico=italico))
            continue
        elif parte.startswith("`") and parte.endswith("`") and len(parte) > 2:
            conteudo = parte[1:-1]
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            i, conteudo = True, parte[1:-1]
        rpr = ("<w:b/>" if b else "") + ("<w:i/>" if i else "")
        saida.append(f"<w:r>{f'<w:rPr>{rpr}</w:rPr>' if rpr else ''}{_t(conteudo)}</w:r>")
    return "".join(saida)


def paragrafo(conteudo_runs: str, estilo: str | None = None, ppr_extra: str = "") -> str:
    ppr = (f'<w:pStyle w:val="{estilo}"/>' if estilo else "") + ppr_extra
    return f"<w:p>{f'<w:pPr>{ppr}</w:pPr>' if ppr else ''}{conteudo_runs}</w:p>"


def quebra_de_pagina() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def campo(instrucao: str, texto_provisorio: str) -> str:
    return (
        '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> {instrucao} </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f"<w:r>{_t(texto_provisorio)}</w:r>"
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    )


def tabela(linhas: list[list[str]]) -> str:
    """Tabela com bordas (formato de quadro) e cabeçalho repetido em cada página."""
    ncol = max(len(l) for l in linhas)
    linhas = [l + [""] * (ncol - len(l)) for l in linhas]
    pesos = [max(6, max(len(l[c]) for l in linhas)) for c in range(ncol)]
    pesos = [min(p, 60) for p in pesos]
    total = sum(pesos)
    larguras = [max(1100, int(LARGURA_TEXTO * p / total)) for p in pesos]
    ajuste = LARGURA_TEXTO - sum(larguras)
    larguras[larguras.index(max(larguras))] += ajuste

    borda = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    bordas = "".join(borda.format(b) for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    xml = [
        "<w:tbl><w:tblPr>"
        f'<w:tblW w:w="{LARGURA_TEXTO}" w:type="dxa"/>'
        f"<w:tblBorders>{bordas}</w:tblBorders>"
        '<w:tblLayout w:type="fixed"/>'
        '<w:tblCellMar><w:left w:w="85" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
        "</w:tblPr><w:tblGrid>"
        + "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras)
        + "</w:tblGrid>"
    ]
    for n, linha in enumerate(linhas):
        cabecalho = n == 0
        xml.append("<w:tr>" + ('<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if cabecalho else '<w:trPr><w:cantSplit/></w:trPr>'))
        for c, celula in enumerate(linha):
            sombra = '<w:shd w:val="clear" w:color="auto" w:fill="E4E7EC"/>' if cabecalho else ""
            xml.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{larguras[c]}" w:type="dxa"/>{sombra}</w:tcPr>'
                + paragrafo(runs(celula.strip(), negrito=cabecalho), "TabelaTexto")
                + "</w:tc>"
            )
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


# --------------------------------------------------------------------------- #
# Leitura do Markdown
# --------------------------------------------------------------------------- #
def converter(md: str, referencias: bool = False, primeiro_capitulo: bool = False) -> str:
    """Converte o subconjunto de Markdown usado no trabalho em XML do Word."""
    linhas = md.splitlines()
    xml: list[str] = []
    buffer: list[str] = []
    estilo_texto = "Referencia" if referencias else None
    capitulo_aberto = False

    def descarregar():
        if buffer:
            texto = " ".join(s.strip() for s in buffer)
            if LEGENDA_RE.match(texto):
                xml.append(paragrafo(runs(texto), "Legenda"))
            elif texto.startswith("Fonte:"):
                xml.append(paragrafo(runs(texto), "Fonte"))
            else:
                xml.append(paragrafo(runs(texto), estilo_texto))
            buffer.clear()

    i = 0
    while i < len(linhas):
        linha = linhas[i]
        bruta = linha.rstrip()

        if bruta.startswith("```"):
            descarregar()
            i += 1
            while i < len(linhas) and not linhas[i].rstrip().startswith("```"):
                xml.append(paragrafo(f"<w:r>{_t(linhas[i].rstrip())}</w:r>", "Codigo"))
                i += 1
            i += 1
            continue

        cabecalho = re.match(r"^(#{1,3})\s+(.+)$", bruta)
        if cabecalho:
            descarregar()
            nivel = len(cabecalho.group(1))
            extra = ""
            if nivel == 1 and primeiro_capitulo and not capitulo_aberto:
                extra = '<w:pageBreakBefore w:val="0"/>'
            capitulo_aberto = capitulo_aberto or nivel == 1
            xml.append(paragrafo(runs(cabecalho.group(2)), f"Heading{nivel}", extra))
            i += 1
            continue

        if bruta.startswith("|"):
            descarregar()
            tab = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                celulas = [c.strip() for c in linhas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celulas if c):
                    tab.append(celulas)
                i += 1
            xml.append(tabela(tab))
            continue

        figura = FIGURA_RE.match(bruta.strip())
        if figura:
            descarregar()
            xml.append(paragrafo(runs(figura.group(1)), "Legenda"))
            xml.append(paragrafo(runs(f"[Inserir aqui: {figura.group(2)}]"), "EspacoFigura"))
            xml.append(paragrafo(runs("Fonte: autoria própria."), "Fonte"))
            i += 1
            continue

        item = re.match(r"^\s*-\s+(.+)$", bruta)
        numerado = re.match(r"^\s*(\d+)\.\s+(.+)$", bruta)
        if item or numerado:
            descarregar()
            marcador = "•" if item else f"{numerado.group(1)}."
            texto = item.group(1) if item else numerado.group(2)
            i += 1
            # Junta linhas de continuação do mesmo item.
            while i < len(linhas) and linhas[i].startswith("  ") and linhas[i].strip() and not re.match(r"^\s*(-|\d+\.)\s", linhas[i]):
                texto += " " + linhas[i].strip()
                i += 1
            xml.append(paragrafo(f"<w:r>{_t(marcador)}</w:r><w:r><w:tab/></w:r>" + runs(texto), "ListaItem"))
            continue

        if not bruta.strip():
            descarregar()
        else:
            buffer.append(bruta)
        i += 1

    descarregar()
    return "".join(xml)


def ler_capa() -> dict[str, list[str]]:
    dados: dict[str, list[str]] = {}
    chaves = {"Instituição", "Curso", "Período", "Atividade", "Título", "Subtítulo",
              "Aluno", "Professora", "Cidade", "Ano"}
    for linha in (CONTEUDO / CAPA).read_text(encoding="utf-8").splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            if chave.strip() in chaves:
                dados.setdefault(chave.strip(), []).append(valor.strip())
    return dados


def montar_capa(d: dict[str, list[str]]) -> str:
    def linha(texto, negrito=False, antes=0):
        extra = f'<w:spacing w:before="{antes}"/>' if antes else ""
        return paragrafo(runs(texto, negrito=negrito), "Capa", extra)

    um = lambda k: (d.get(k) or [""])[0]
    xml = [
        linha(um("Instituição"), True),
        linha(um("Curso"), True),
        linha(um("Período")),
    ]
    for n, aluno in enumerate(d.get("Aluno", [])):
        xml.append(linha(aluno, antes=1700 if n == 0 else 0))
    xml += [
        linha(um("Título"), True, antes=2300),
        linha(um("Subtítulo")),
        linha(um("Atividade"), antes=900),
        linha(f"Professora: {um('Professora')}"),
        linha(um("Cidade"), antes=2600),
        linha(um("Ano")),
    ]
    return "".join(xml)


# --------------------------------------------------------------------------- #
# Partes fixas do pacote .docx
# --------------------------------------------------------------------------- #
def estilos() -> str:
    def estilo(id_, nome, ppr="", rpr="", base="Normal", tipo="paragraph", extra=""):
        base_xml = f'<w:basedOn w:val="{base}"/>' if base else ""
        return (
            f'<w:style w:type="{tipo}" w:styleId="{id_}"><w:name w:val="{nome}"/>{base_xml}{extra}'
            f"<w:qFormat/>{f'<w:pPr>{ppr}</w:pPr>' if ppr else ''}{f'<w:rPr>{rpr}</w:rPr>' if rpr else ''}</w:style>"
        )

    sem_recuo = '<w:ind w:firstLine="0"/>'
    tab_sumario = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{LARGURA_TEXTO}"/></w:tabs>'
    return (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><w:styles {NS}>"
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR" w:eastAsia="pt-BR" w:bidi="ar-SA"/>'
        "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>"
        f'<w:spacing w:after="0" w:line="{LINHA_1_5}" w:lineRule="auto"/>'
        "</w:pPr></w:pPrDefault></w:docDefaults>"
        + estilo("Normal", "Normal", f'<w:ind w:firstLine="{RECUO_PRIMEIRA_LINHA}"/><w:jc w:val="both"/>', base=None,
                 extra="")
        .replace('<w:style w:type="paragraph" w:styleId="Normal">', '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">')
        + estilo("Heading1", "heading 1",
                 f'<w:keepNext/><w:pageBreakBefore/><w:spacing w:after="{LINHA_1_5}"/>{sem_recuo}<w:jc w:val="left"/><w:outlineLvl w:val="0"/>',
                 "<w:b/>", extra='<w:next w:val="Normal"/>')
        + estilo("Heading2", "heading 2",
                 f'<w:keepNext/><w:spacing w:before="{LINHA_1_5}" w:after="120"/>{sem_recuo}<w:jc w:val="left"/><w:outlineLvl w:val="1"/>',
                 "<w:b/>", extra='<w:next w:val="Normal"/>')
        + estilo("Heading3", "heading 3",
                 f'<w:keepNext/><w:spacing w:before="240" w:after="120"/>{sem_recuo}<w:jc w:val="left"/><w:outlineLvl w:val="2"/>',
                 "<w:b/><w:i/>", extra='<w:next w:val="Normal"/>')
        + estilo("TOC1", "toc 1", f'{tab_sumario}<w:ind w:left="0" w:firstLine="0"/><w:jc w:val="left"/>', "<w:b/>")
        + estilo("TOC2", "toc 2", f'{tab_sumario}<w:ind w:left="284" w:firstLine="0"/><w:jc w:val="left"/>')
        + estilo("TOC3", "toc 3", f'{tab_sumario}<w:ind w:left="567" w:firstLine="0"/><w:jc w:val="left"/>')
        + estilo("SumarioTitulo", "Título do sumário", f'<w:spacing w:after="{LINHA_1_5}"/>{sem_recuo}<w:jc w:val="center"/>', "<w:b/>")
        + estilo("Capa", "Capa", f'{sem_recuo}<w:jc w:val="center"/>')
        + estilo("Legenda", "Legenda", f'<w:keepNext/><w:spacing w:before="240"/>{sem_recuo}<w:jc w:val="center"/>')
        + estilo("Fonte", "Fonte da figura", f'<w:spacing w:after="240"/>{sem_recuo}<w:jc w:val="center"/>')
        + estilo("EspacoFigura", "Espaço para figura",
                 '<w:keepNext/><w:pBdr><w:top w:val="dashed" w:sz="6" w:space="8" w:color="98A2B3"/>'
                 '<w:left w:val="dashed" w:sz="6" w:space="8" w:color="98A2B3"/>'
                 '<w:bottom w:val="dashed" w:sz="6" w:space="8" w:color="98A2B3"/>'
                 '<w:right w:val="dashed" w:sz="6" w:space="8" w:color="98A2B3"/></w:pBdr>'
                 f'<w:spacing w:before="1200" w:after="1200"/>{sem_recuo}<w:jc w:val="center"/>',
                 '<w:i/><w:color w:val="667085"/>')
        + estilo("Codigo", "Código-fonte",
                 f'<w:shd w:val="clear" w:color="auto" w:fill="F2F4F7"/>{sem_recuo}<w:jc w:val="left"/>')
        + estilo("ListaItem", "Item de lista",
                 f'<w:tabs><w:tab w:val="left" w:pos="{RECUO_PRIMEIRA_LINHA}"/></w:tabs>'
                 f'<w:ind w:left="{RECUO_PRIMEIRA_LINHA}" w:hanging="357"/><w:jc w:val="both"/>')
        + estilo("TabelaTexto", "Texto de tabela", f'{sem_recuo}<w:jc w:val="left"/>')
        + estilo("Referencia", "Referência", f'<w:spacing w:after="240"/>{sem_recuo}<w:jc w:val="left"/>')
        + estilo("Cabecalho", "header", f'<w:spacing w:line="240" w:lineRule="auto"/>{sem_recuo}<w:jc w:val="right"/>')
        + "</w:styles>"
    )


def secao(cabecalho: bool, quebra: bool) -> str:
    ref = '<w:headerReference w:type="default" r:id="rIdCabecalho"/>' if cabecalho else ""
    tipo = '<w:type w:val="nextPage"/>' if quebra else ""
    return (
        f"<w:sectPr>{ref}{tipo}<w:pgSz w:w=\"{LARGURA_PAGINA}\" w:h=\"{ALTURA_PAGINA}\"/>"
        f'<w:pgMar w:top="{MARGEM_SUP}" w:right="{MARGEM_DIR}" w:bottom="{MARGEM_INF}" '
        f'w:left="{MARGEM_ESQ}" w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>'
    )


def cabecalho_xml() -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr {NS}>'
        + paragrafo(campo("PAGE", "1"), "Cabecalho")
        + "</w:hdr>"
    )


def pacote(corpo: str, titulo: str, autores: str) -> dict[str, str]:
    agora = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>"
        ),
        "word/_rels/document.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rIdEstilos" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rIdConfig" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
            '<Relationship Id="rIdCabecalho" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
            "</Relationships>"
        ),
        "word/document.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NS}><w:body>{corpo}</w:body></w:document>',
        "word/styles.xml": estilos(),
        "word/settings.xml": (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings {NS}>'
            '<w:defaultTabStop w:val="709"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/>'
            '<w:updateFields w:val="true"/>'
            '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
            "</w:settings>"
        ),
        "word/header1.xml": cabecalho_xml(),
        "docProps/core.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{escape(titulo)}</dc:title><dc:creator>{escape(autores)}</dc:creator>"
            f'<dc:language>pt-BR</dc:language><dcterms:created xsi:type="dcterms:W3CDTF">{agora}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{agora}</dcterms:modified>'
            "</cp:coreProperties>"
        ),
        "docProps/app.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
            "<Application>gerar_docx.py</Application></Properties>"
        ),
    }


# --------------------------------------------------------------------------- #
# Conferências
# --------------------------------------------------------------------------- #
def conferir_codigo() -> list[str]:
    """Compara os trechos do capítulo de código com os arquivos do repositório."""
    texto = (CONTEUDO / "08-codigo.md").read_text(encoding="utf-8")
    padrao = re.compile(
        r"```\w*\n(.*?)\n```\s*\n\s*Fonte: autoria própria \(arquivo `([^`]+)`, linhas (\d+) a (\d+)\)", re.S
    )
    avisos = []
    for codigo, arquivo, ini, fim in padrao.findall(texto):
        caminho = RAIZ / arquivo
        if not caminho.exists():
            avisos.append(f"arquivo não encontrado: {arquivo}")
            continue
        real = "\n".join(caminho.read_text(encoding="utf-8").splitlines()[int(ini) - 1:int(fim)])
        if real != codigo:
            avisos.append(f"trecho diferente do código atual: {arquivo}, linhas {ini} a {fim}")
    return avisos


def estimar_paginas(md: str) -> float:
    """Estimativa grosseira: cerca de 68 caracteres por linha e 33 linhas por página."""
    por_linha, por_pagina = 68, 33
    linhas = 0.0
    em_codigo = False
    tabela_atual: list[list[str]] = []

    def linhas_da_tabela(tab: list[list[str]]) -> float:
        # Mesmas proporções de coluna usadas em tabela().
        ncol = max(len(l) for l in tab)
        tab = [l + [""] * (ncol - len(l)) for l in tab]
        pesos = [min(60, max(6, max(len(l[c]) for l in tab))) for c in range(ncol)]
        total = sum(pesos)
        larguras = [max(4, int(por_linha * p / total) - 2) for p in pesos]
        return sum(max(-(-len(l[c]) // larguras[c]) or 1 for c in range(ncol)) for l in tab) + 1

    for bruta in md.splitlines() + [""]:
        s = bruta.rstrip()
        if tabela_atual and not s.startswith("|"):
            linhas += linhas_da_tabela(tabela_atual)
            tabela_atual = []
        if s.startswith("```"):
            em_codigo = not em_codigo
            continue
        if em_codigo:
            linhas += max(1, -(-len(s) // por_linha))
        elif not s.strip():
            continue
        elif s.startswith("# "):
            linhas += 2
        elif s.startswith("#"):
            linhas += 2
        elif s.startswith("|"):
            if not re.fullmatch(r"\|[\s:|-]+\|", s.strip()):
                tabela_atual.append([c.strip() for c in s.strip().strip("|").split("|")])
            continue
        elif FIGURA_RE.match(s.strip()):
            linhas += 12
        else:
            linhas += max(1, -(-(len(s) + 6) // por_linha))
    return linhas / por_pagina


# --------------------------------------------------------------------------- #
def main() -> None:
    capa = ler_capa()
    corpo = [montar_capa(capa), quebra_de_pagina()]
    corpo.append(paragrafo(runs("SUMÁRIO"), "SumarioTitulo"))
    corpo.append(paragrafo(campo('TOC \\o "1-2" \\h \\z \\u',
                                 'Clique com o botão direito aqui e escolha "Atualizar campo" para montar o sumário.')))
    # Fim da seção 1 (capa e sumário, sem número de página aparente).
    corpo.append(f"<w:p><w:pPr>{secao(cabecalho=False, quebra=True)}</w:pPr></w:p>")

    for n, nome in enumerate(CAPITULOS):
        md = (CONTEUDO / nome).read_text(encoding="utf-8")
        corpo.append(converter(md, referencias=(nome == BIBLIOGRAFIA), primeiro_capitulo=(n == 0)))
    corpo.append(secao(cabecalho=True, quebra=False))

    titulo = (capa.get("Título") or ["Trabalho"])[0]
    autores = "; ".join(capa.get("Aluno", []))
    with zipfile.ZipFile(SAIDA, "w", zipfile.ZIP_DEFLATED) as z:
        for caminho, conteudo in pacote("".join(corpo), titulo, autores).items():
            z.writestr(caminho, conteudo)
    print(f"Gerado: {SAIDA}")

    avisos = conferir_codigo()
    for aviso in avisos:
        print(f"AVISO: {aviso}")
    if not avisos:
        print("Trechos de código conferidos: iguais aos arquivos do repositório.")

    if "--estimar" in sys.argv:
        print("\nEstimativa de páginas (confira no Word):")
        for nome in CAPITULOS:
            paginas = estimar_paginas((CONTEUDO / nome).read_text(encoding="utf-8"))
            minimo, maximo = LIMITES.get(nome, (None, None))
            faixa = f"limite {minimo} a {maximo}" if maximo else "sem limite"
            alerta = ""
            if maximo and (paginas < minimo or paginas > maximo):
                alerta = "  <-- fora do limite"
            print(f"  {nome:22s} ~{paginas:4.1f} págs. ({faixa}){alerta}")


if __name__ == "__main__":
    main()

"""Genera un borrador .docx de la tesis a partir de thesis/ (FORMATO_TESIS.md).

Uso (desde la raíz del repo):
    python scripts/build_docx.py              # usa/crea scripts/plantilla/referencia.docx
    python scripts/build_docx.py --plantilla  # regenera la plantilla antes de compilar

Requiere: pandoc (>= 3) y LibreOffice (para convertir las figuras SVG a PNG).
Solo usa la biblioteca estándar de Python. No modifica ningún archivo de thesis/:
los .md se copian, se normalizan y se convierten en un directorio temporal.
Salida: build/KaabLab_Tesis_<VERSION>.docx
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

VERSION = "v1.0"

RAIZ = Path(__file__).resolve().parent.parent
THESIS = RAIZ / "thesis"
PRELIM = THESIS / "preliminares"
PLANTILLA = RAIZ / "scripts" / "plantilla" / "referencia.docx"
SALIDA = RAIZ / "build" / f"KaabLab_Tesis_{VERSION}.docx"

CAPITULOS = [
    "capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md",
    "capitulo-2-materiales-y-metodos/capitulo-2.md",
    "capitulo-3-resultados-y-discusiones/capitulo-3.md",
    "capitulo-4-recomendaciones/capitulo-4.md",
    "capitulo-5-conclusiones/capitulo-5.md",
]

# Documentos firmados (01–03 y 06): en el .docx solo se reserva su página.
DOCUMENTOS_OFICIALES = {
    "01-carta-liberacion-tesis.md": "Carta de liberación de tesis (CPI-FO-05-06)",
    "02-oficio-autorizacion-comite.md": "Oficio de autorización del comité tutorial/claustro doctoral",
    "03-carta-reconocimiento-directores.md": "Carta de reconocimiento del director(a) y codirector(a) de tesis",
    "06-oficio-antiplagio.md": "Oficio de liberación de análisis anti-plagio",
}

# Medidas (twips: 1 cm = 567; medios puntos para tamaños de fuente)
MARGEN = 1418           # 2.5 cm
SANGRIA_FRANCESA = 851  # 1.5 cm
ANCHO_MAX_CM, ALTO_MAX_CM = 16.0, 18.0  # área útil carta con márgenes de 2.5 cm: 16.6 × 22.9 cm

SALTO_PAGINA = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'
CAMPO_TOC = (
    '```{=openxml}\n'
    '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:t>[Actualizar el índice en Word: clic derecho → Actualizar campo]</w:t></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>\n'
    '```'
)


def buscar_soffice():
    for c in ("soffice", "libreoffice"):
        if shutil.which(c):
            return shutil.which(c)
    for c in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if os.path.exists(c):
            return c
    return None


# ---------------------------------------------------------------- plantilla

ARIAL = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
ESPACIADO_CUERPO = '<w:spacing w:before="240" w:after="0" w:line="360" w:lineRule="auto"/>'


def _estilo(style_id, nombre, ppr="", rpr="", base="Normal", siguiente=None, tipo="paragraph", extra=""):
    sig = f'<w:next w:val="{siguiente}"/>' if siguiente else ""
    b = f'<w:basedOn w:val="{base}"/>' if base else ""
    return (f'<w:style w:type="{tipo}" w:customStyle="1" w:styleId="{style_id}">'
            f'<w:name w:val="{nombre}"/>{b}{sig}{extra}<w:qFormat/>'
            f'<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


ESTILOS = [
    _estilo("Normal", "Normal", ESPACIADO_CUERPO, ARIAL + '<w:sz w:val="22"/><w:szCs w:val="22"/>', base=None),
    _estilo("BodyText", "Body Text", ESPACIADO_CUERPO),
    _estilo("FirstParagraph", "First Paragraph", "", "", base="BodyText", siguiente="BodyText"),
    _estilo("Compact", "Compact", ESPACIADO_CUERPO),
    # Título de capítulo: Arial 12, MAYÚSCULAS, negritas, izquierda, en página nueva
    _estilo("Heading1", "heading 1",
            '<w:keepNext/><w:keepLines/><w:pageBreakBefore/><w:spacing w:before="240" w:after="240" w:line="360" w:lineRule="auto"/><w:jc w:val="left"/><w:outlineLvl w:val="0"/>',
            ARIAL + '<w:b/><w:bCs/><w:caps/><w:sz w:val="24"/><w:szCs w:val="24"/>', siguiente="BodyText"),
    # Subtítulo nivel 1: Arial 11, MAYÚSCULAS, negritas
    _estilo("Heading2", "heading 2",
            '<w:keepNext/><w:keepLines/>' + ESPACIADO_CUERPO + '<w:outlineLvl w:val="1"/>',
            ARIAL + '<w:b/><w:bCs/><w:caps/><w:sz w:val="22"/><w:szCs w:val="22"/>', siguiente="BodyText"),
    # Niveles siguientes: Arial 11, mayúsculas y minúsculas, negritas
    _estilo("Heading3", "heading 3",
            '<w:keepNext/><w:keepLines/>' + ESPACIADO_CUERPO + '<w:outlineLvl w:val="2"/>',
            ARIAL + '<w:b/><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/>', siguiente="BodyText"),
    _estilo("Heading4", "heading 4",
            '<w:keepNext/><w:keepLines/>' + ESPACIADO_CUERPO + '<w:outlineLvl w:val="3"/>',
            ARIAL + '<w:b/><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/>', siguiente="BodyText"),
    # Leyendas "Tabla X.Y" / "Figura X.Y": Arial 10
    _estilo("Leyenda", "Leyenda", '<w:keepNext/>' + ESPACIADO_CUERPO,
            '<w:sz w:val="20"/><w:szCs w:val="20"/>', siguiente="BodyText"),
    _estilo("TextoTabla", "Texto de tabla", '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>',
            '<w:sz w:val="20"/><w:szCs w:val="20"/>'),
    _estilo("Bibliography", "Bibliography",
            ESPACIADO_CUERPO + f'<w:ind w:left="{SANGRIA_FRANCESA}" w:hanging="{SANGRIA_FRANCESA}"/>', ""),
    _estilo("ImageCaption", "Image Caption", '<w:jc w:val="center"/>', '<w:sz w:val="20"/><w:szCs w:val="20"/>'),
    _estilo("CaptionedFigure", "Captioned Figure", '<w:keepNext/><w:jc w:val="center"/>', ""),
    _estilo("Figure", "Figure", '<w:jc w:val="center"/>', ""),
]

PIE_PAGINA = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/><w:jc w:val="right"/></w:pPr>'
    f'<w:r><w:rPr>{ARIAL}<w:sz w:val="22"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
    f'<w:r><w:rPr>{ARIAL}<w:sz w:val="22"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    f'<w:r><w:rPr>{ARIAL}<w:sz w:val="22"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
    f'<w:r><w:rPr>{ARIAL}<w:sz w:val="22"/></w:rPr><w:t>1</w:t></w:r>'
    f'<w:r><w:rPr>{ARIAL}<w:sz w:val="22"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
    '</w:p></w:ftr>'
)

SECTPR_PLANTILLA = (
    '<w:sectPr><w:footerReference w:type="default" r:id="rIdPiePagina"/>'
    '<w:footnotePr><w:numRestart w:val="eachSect"/></w:footnotePr>'
    '<w:pgSz w:w="12240" w:h="15840"/>'
    f'<w:pgMar w:top="{MARGEN}" w:right="{MARGEN}" w:bottom="{MARGEN}" w:left="{MARGEN}" '
    'w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>'
)


def crear_plantilla(destino: Path):
    """Parte de la plantilla por defecto de pandoc y aplica FORMATO_TESIS.md."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "default.docx"
        subprocess.run(["pandoc", "-o", str(base), "--print-default-data-file", "reference.docx"], check=True)
        with zipfile.ZipFile(base) as zin:
            partes = {n: zin.read(n) for n in zin.namelist()}

    estilos = partes["word/styles.xml"].decode("utf-8")
    estilos = re.sub(
        r"<w:docDefaults>.*?</w:docDefaults>",
        "<w:docDefaults><w:rPrDefault><w:rPr>" + ARIAL +
        '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="es-MX" w:eastAsia="es-MX" w:bidi="ar-SA"/>'
        "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>" + ESPACIADO_CUERPO +
        "</w:pPr></w:pPrDefault></w:docDefaults>",
        estilos, flags=re.S)
    for e in ESTILOS:
        sid = re.search(r'w:styleId="([^"]+)"', e).group(1)
        estilos = re.sub(rf'<w:style [^>]*w:styleId="{sid}"[^>]*>.*?</w:style>', "", estilos, flags=re.S)
        estilos = estilos.replace("</w:styles>", e + "</w:styles>")
    partes["word/styles.xml"] = estilos.encode("utf-8")

    doc = partes["word/document.xml"].decode("utf-8")
    doc = re.sub(r"<w:sectPr>.*?</w:sectPr>", SECTPR_PLANTILLA, doc, flags=re.S)
    partes["word/document.xml"] = doc.encode("utf-8")

    rels = partes["word/_rels/document.xml.rels"].decode("utf-8")
    rels = rels.replace("</Relationships>",
                        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
                        'Id="rIdPiePagina" Target="footer1.xml" /></Relationships>')
    partes["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    ct = partes["[Content_Types].xml"].decode("utf-8")
    ct = ct.replace("</Types>",
                    '<Override PartName="/word/footer1.xml" '
                    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" /></Types>')
    partes["[Content_Types].xml"] = ct.encode("utf-8")
    partes["word/footer1.xml"] = PIE_PAGINA.encode("utf-8")

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, d in partes.items():
            zout.writestr(n, d)
    print(f"Plantilla creada: {destino.relative_to(RAIZ)}")


# ---------------------------------------------------------------- markdown

def normalizar_md(texto: str) -> str:
    """Limpieza solo de la copia temporal (los .md originales no se tocan)."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)  # comentarios HTML fuera del docx
    # Negritas partidas heredadas de la conversión desde Word: "**Capa ****IoT****" → "**Capa IoT"
    texto = texto.replace("****", "")
    # "**Tabla 1.3 **Texto" no cierra la negrita en Markdown: → "**Tabla 1.3** Texto"
    abre = r"(?<![*\w])\*\*(?=\S)([^*\n]*?[^\s*])[ \t]+\*\*"
    texto = re.sub(abre + r"(?=\S)", r"**\1** ", texto)
    texto = re.sub(abre, r"**\1**", texto)
    return anchos_tablas(texto)


def anchos_tablas(texto: str) -> str:
    """Ajusta los guiones del separador de cada tabla al contenido de sus columnas.

    Pandoc reparte el ancho de las columnas según el número de guiones del separador;
    con separadores uniformes ("| --- | --- |") todas las columnas quedan iguales.
    """
    lineas = texto.split("\n")
    sep = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
    for i, linea in enumerate(lineas):
        if i == 0 or not sep.match(linea) or not lineas[i - 1].lstrip().startswith("|"):
            continue
        fin = i + 1
        while fin < len(lineas) and lineas[fin].lstrip().startswith("|"):
            fin += 1
        filas = [lineas[i - 1]] + lineas[i + 1:fin]
        celdas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
        alineas = [c.strip() for c in linea.strip().strip("|").split("|")]
        nuevas = []
        for j, a in enumerate(alineas):
            largo = max((len(re.sub(r"[*_`]", "", f[j])) for f in celdas if j < len(f)), default=3)
            n = min(max(largo, 4), 60)
            nuevas.append((":" if a.startswith(":") else "") + "-" * n + (":" if a.endswith(":") else ""))
        lineas[i] = "| " + " | ".join(nuevas) + " |"
    return "\n".join(lineas)


def convertir_figuras(md: str, dir_md: Path, dir_png: Path, soffice: str) -> str:
    """Sustituye cada imagen SVG por una copia PNG temporal con tamaño dentro de márgenes."""
    def reemplazo(m):
        alt, ruta = m.group(1), m.group(2)
        if not ruta.lower().endswith(".svg"):
            return m.group(0)
        svg = (dir_md / ruta).resolve()
        cab = svg.read_text(encoding="utf-8")[:2000]
        vb = re.search(r'viewBox="\s*[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', cab)
        w, h = (float(vb.group(1)), float(vb.group(2))) if vb else (1000.0, 1000.0)
        escala = 2400 / w
        filtro = ('png:draw_png_Export:{"PixelWidth":{"type":"long","value":"%d"},'
                  '"PixelHeight":{"type":"long","value":"%d"}}' % (round(w * escala), round(h * escala)))
        subprocess.run([soffice, "--headless", "--convert-to", filtro, "--outdir", str(dir_png), str(svg)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        png = dir_png / (svg.stem + ".png")
        if not png.exists():
            sys.exit(f"No se pudo convertir {svg}")
        ancho = min(ANCHO_MAX_CM, ALTO_MAX_CM * w / h)
        return f"![{alt}]({png.name}){{width={ancho:.2f}cm}}"
    return re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", reemplazo, md)


def ensamblar(dir_png: Path, soffice: str) -> str:
    bloques = []
    for f in sorted(PRELIM.glob("*.md")):
        nombre = f.name
        if nombre in DOCUMENTOS_OFICIALES:
            bloques.append(SALTO_PAGINA)
            bloques.append(f"\\[Insertar escaneo oficial: {DOCUMENTOS_OFICIALES[nombre]}\\]")
            continue
        texto = normalizar_md(f.read_text(encoding="utf-8"))
        if nombre.startswith("08-"):
            titulo = re.search(r"^# .*$", texto, flags=re.M).group(0)
            texto = f"{titulo}\n\n{CAMPO_TOC}"
        elif nombre.startswith("07-") and not re.sub(r"^# .*$", "", texto, flags=re.M).strip():
            titulo = re.search(r"^# .*$", texto, flags=re.M).group(0)
            texto = f"{titulo}\n\n\\[Pendiente\\]"
        bloques.append(texto)
    for c in CAPITULOS:
        ruta = THESIS / c
        texto = normalizar_md(ruta.read_text(encoding="utf-8"))
        bloques.append(convertir_figuras(texto, ruta.parent, dir_png, soffice))
    bloques.append(bibliografia())
    return "\n\n".join(b.strip() for b in bloques) + "\n"


def bibliografia() -> str:
    """Solo el encabezado y las entradas de referencias.md, sin notas de trabajo.

    Se omiten la nota inicial ("Formato APA…"), el subtítulo y la introducción de la
    sección "Referencias ya citadas…" y las remisiones ("Ver entrada arriba"); las
    entradas de esa sección se integran a la lista en orden alfabético y cronológico.
    """
    texto = normalizar_md((THESIS / "referencias.md").read_text(encoding="utf-8"))
    titulo = re.search(r"^# .*$", texto, flags=re.M).group(0)
    entradas = []
    for bloque in re.split(r"\n\s*\n", texto):
        for linea in re.split(r"\n(?=- )", bloque.strip()):
            linea = re.sub(r"^- ", "", linea.strip())
            linea = re.sub(r"\s*\n\s*", " ", linea)
            if (not linea or linea.startswith("#") or linea.startswith("Formato APA")
                    or linea.startswith("Las siguientes referencias") or "Ver entrada arriba" in linea
                    or not re.search(r"\(\d{4}[a-z]?\)", linea)):
                continue
            entradas.append(linea)

    def clave(e):
        autores = e.split("(", 1)[0]
        apellido = autores.split(",", 1)[0].casefold()
        anio = re.search(r"\((\d{4}[a-z]?)\)", e).group(1)
        return (apellido, "&" in autores or "et al" in autores, anio, e.casefold())
    return titulo + "\n\n" + "\n\n".join(sorted(entradas, key=clave))


# ---------------------------------------------------------------- postproceso

def _texto(p: str) -> str:
    return "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p))


def postprocesar(docx: Path):
    with zipfile.ZipFile(docx) as zin:
        partes = {n: zin.read(n) for n in zin.namelist()}
    doc = partes["word/document.xml"].decode("utf-8")

    # 1) Texto dentro de tablas: estilo TextoTabla (Arial 10, interlineado sencillo)
    doc = re.sub(r"<w:tbl>.*?</w:tbl>",
                 lambda m: m.group(0).replace('<w:pStyle w:val="Compact" />', '<w:pStyle w:val="TextoTabla" />'),
                 doc, flags=re.S)

    parrafos = list(re.finditer(r"<w:p>(?:(?!</w:p>).)*?</w:p>|<w:p [^>]*>(?:(?!</w:p>).)*?</w:p>", doc, flags=re.S))
    zona = "preliminar"
    cambios = []
    for m in parrafos:
        p = m.group(0)
        txt = _texto(p).strip()
        nuevo = p
        if '<w:pStyle w:val="Heading1" />' in p:
            if txt.upper().startswith("CAPÍTULO"):
                zona = "cuerpo"
            elif zona == "cuerpo" and txt.lower().startswith("referencias"):
                zona = "bibliografia"
            if zona == "preliminar":  # RESUMEN, ABSTRACT, INTRODUCCIÓN, etc.: centrados
                extra = '<w:jc w:val="center" />'
                if txt.upper() in ("INTRODUCCIÓN", "ÍNDICE"):  # inician sección (ver paso 2)
                    extra = '<w:pageBreakBefore w:val="0" />' + extra
                nuevo = nuevo.replace('<w:pStyle w:val="Heading1" />', '<w:pStyle w:val="Heading1" />' + extra, 1)
        elif re.match(r"^(Tabla|Figura) \d+\.\d+", txt) and "<w:b />" in p and '<w:pStyle w:val="TextoTabla" />' not in p:
            nuevo = re.sub(r'<w:pStyle w:val="(BodyText|FirstParagraph)" />', '<w:pStyle w:val="Leyenda" />', nuevo, count=1)
        elif "<w:drawing>" in p:  # figura: mantenerla en la misma página que su leyenda
            nuevo = re.sub(r'(<w:pStyle w:val="[^"]+" />)', r'\1<w:keepNext />', nuevo, count=1)
        elif zona == "bibliografia":
            nuevo = re.sub(r'<w:pStyle w:val="(BodyText|FirstParagraph)" />', '<w:pStyle w:val="Bibliography" />', nuevo, count=1)
        if nuevo != p:
            cambios.append((m.start(), m.end(), nuevo))
    for ini, fin, nuevo in reversed(cambios):
        doc = doc[:ini] + nuevo + doc[fin:]

    # 2) Secciones de numeración: portada…agradecimientos sin número; ÍNDICE…ABSTRACT en
    #    romanos desde i; INTRODUCCIÓN en adelante en arábigos desde 1
    sect = re.search(r"<w:sectPr>.*?</w:sectPr>(?=\s*</w:body>)", doc, flags=re.S)
    if not sect:
        sys.exit("No se encontró sectPr final en el documento")
    base = sect.group(0)
    sin_numero = re.sub(r"<w:footerReference [^>]*/>", "", base)
    romano = re.sub(r"(<w:pgMar [^>]*/>)", r'\1<w:pgNumType w:fmt="lowerRoman" w:start="1" />', base)
    arabigo = re.sub(r"(<w:pgMar [^>]*/>)", r'\1<w:pgNumType w:fmt="decimal" w:start="1" />', base)
    doc = doc[:sect.start()] + arabigo + doc[sect.end():]
    for encabezado, sect_anterior in (("INTRODUCCIÓN", romano), ("ÍNDICE", sin_numero)):
        ubic = next((m for m in re.finditer(r"<w:p>(?:(?!</w:p>).)*?</w:p>", doc, flags=re.S)
                     if '<w:pStyle w:val="Heading1" />' in m.group(0)
                     and _texto(m.group(0)).strip().upper() == encabezado), None)
        if not ubic:
            sys.exit(f"No se encontró el encabezado {encabezado}")
        doc = doc[:ubic.start()] + f"<w:p><w:pPr>{sect_anterior}</w:pPr></w:p>" + doc[ubic.start():]
    partes["word/document.xml"] = doc.encode("utf-8")

    # 3) Pedir a Word que actualice campos (índice) al abrir
    ajustes = partes["word/settings.xml"].decode("utf-8")
    if "updateFields" not in ajustes:
        ajustes = re.sub(r"(<w:settings[^>]*>)", r'\1<w:updateFields w:val="true" />', ajustes, count=1)
    partes["word/settings.xml"] = ajustes.encode("utf-8")

    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, d in partes.items():
            zout.writestr(n, d)
    tmp.replace(docx)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plantilla", action="store_true", help="regenerar la plantilla de referencia")
    args = ap.parse_args()

    if not shutil.which("pandoc"):
        sys.exit("pandoc no está en el PATH")
    soffice = buscar_soffice()
    if not soffice:
        sys.exit("No se encontró LibreOffice (soffice), necesario para convertir las figuras SVG")
    if args.plantilla or not PLANTILLA.exists():
        crear_plantilla(PLANTILLA)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kaablab_docx_") as tmp:
        tmp = Path(tmp)
        md = tmp / "tesis.md"
        md.write_text(ensamblar(tmp, soffice), encoding="utf-8")
        subprocess.run(["pandoc", str(md), "-f", "markdown-implicit_figures", "-t", "docx",
                        "--reference-doc", str(PLANTILLA), "--resource-path", str(tmp),
                        "-M", "lang=es-MX", "-o", str(SALIDA)], check=True)
    postprocesar(SALIDA)
    print(f"Borrador generado: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

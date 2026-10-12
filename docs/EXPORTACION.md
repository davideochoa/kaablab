# Exportación de la tesis a .docx

Comando de referencia para generar el documento final con Pandoc, una vez
completados los pasos de separación de preliminares y formato de
`thesis/`. Los preliminares viven en `thesis/preliminares/`, separados en
archivos numerados (00–13 según las 14 secciones oficiales del formato
ITESCAM/TecNM).

Borrador con formato FORMATO_TESIS.md: `python scripts/build_docx.py` → `build/KaabLab_Tesis_borrador.docx` (requiere pandoc y LibreOffice).

```bash
pandoc thesis/preliminares/00-portada.md thesis/preliminares/06-agradecimientos.md \
  thesis/preliminares/07-indice.md thesis/preliminares/08-abreviaturas.md \
  thesis/preliminares/09-indice-figuras.md thesis/preliminares/10-indice-tablas.md \
  thesis/preliminares/11-resumen.md thesis/preliminares/12-abstract.md thesis/preliminares/13-introduccion.md \
  thesis/capitulo-1*/*.md thesis/capitulo-2*/*.md thesis/capitulo-3*/*.md \
  thesis/capitulo-4*/*.md thesis/capitulo-5*/*.md \
  thesis/referencias.md \
  --toc --toc-depth=3 \
  -o tesis_final.docx
```

## Notas

- Los documentos oficiales firmados (`thesis/preliminares/01-carta-liberacion-tesis.md`
  a `thesis/preliminares/05-oficio-antiplagio.md`) **no** se incluyen en este
  comando — son placeholders para oficios y cartas institucionales. Se
  insertan manualmente en Word como PDF/imagen escaneada después de la
  conversión, en su posición correspondiente dentro del orden de
  preliminares (entre `00-portada.md` y `06-agradecimientos.md`).
- `07-indice.md`, `09-indice-figuras.md` y `10-indice-tablas.md` ya
  contienen el listado real de capítulos/secciones y de leyendas de
  Figura/Tabla, mantenido a mano en sincronía con los 5 capítulos (no se
  generan automáticamente). El número de página de cada entrada de
  `09-indice-figuras.md` y `10-indice-tablas.md` queda como
  `[pendiente]` hasta la paginación final en Word. Pandoc además genera
  su propio índice general con `--toc` a partir de los headings
  Markdown reales (`#`, `##`, `###`); conviene revisar en el .docx
  final si se conserva solo uno de los dos índices generales (el de
  `--toc` o el texto manual de `07-indice.md`) para evitar duplicarlo.
- La ruta de los preliminares (`thesis/preliminares/...`) corrige una
  omisión de una versión anterior del comando de referencia, que
  suponía los archivos directamente bajo `thesis/`.

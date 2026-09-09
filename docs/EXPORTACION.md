# Exportación de la tesis a .docx

Comando de referencia para generar el documento final con Pandoc, una vez
completados los pasos de separación de preliminares y formato de
`thesis/`. Los preliminares viven en `thesis/preliminares/`, separados en
archivos numerados (00–13 según las 13 secciones oficiales del formato
ITESCAM/TecNM, más `14-otros-preliminares.md` para contenido que no
encaja en esas 13 secciones — ver nota al final).

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
- `thesis/preliminares/14-otros-preliminares.md` (Dedicatoria) tampoco se
  incluye — no forma parte de las 13 secciones oficiales del formato
  ITESCAM/TecNM. Su inclusión y ubicación en el documento final quedan
  pendientes de confirmación con la asesora.
- `07-indice.md`, `09-indice-figuras.md` y `10-indice-tablas.md` solo
  contienen el encabezado de sección — el contenido de cada índice se
  genera automáticamente al exportar con `--toc` (para el índice general)
  o al compilar el documento final en Word (para figuras y tablas), a
  partir de los headings Markdown reales (`#`, `##`, `###`) presentes en
  cada capítulo y en las leyendas de Figura/Tabla.
- La ruta de los preliminares (`thesis/preliminares/...`) corrige una
  omisión de una versión anterior del comando de referencia, que
  suponía los archivos directamente bajo `thesis/`.

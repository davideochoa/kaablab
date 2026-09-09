# Revisión de preliminares, headings y nomenclatura binomial

Reporte de la separación de `thesis/preliminares/preliminares.md`, la
conversión de títulos a headings Markdown reales y la corrección de
nomenclatura binomial en todo `thesis/`, ejecutada según el formato
"Elaboración de Tesis" de ITESCAM/TecNM. No se hizo commit ni push.

## 1. Archivos de preliminares creados

Se crearon 15 archivos en `thesis/preliminares/` y se eliminó
`preliminares.md`.

| Archivo | Líneas | Tipo |
|---|---|---|
| `00-portada.md` | 27 | Contenido real (portada, movida verbatim; título con markup `**` malformado corregido) |
| `01-carta-liberacion-tesis.md` | 7 | Placeholder (documento oficial pendiente) |
| `02-oficio-autorizacion-comite.md` | 7 | Placeholder (documento oficial pendiente) |
| `03-carta-reconocimiento-directores.md` | 7 | Placeholder (documento oficial pendiente) |
| `04-declaracion-propiedad-intelectual.md` | 7 | Placeholder (documento oficial pendiente) |
| `05-oficio-antiplagio.md` | 7 | Placeholder (documento oficial pendiente) |
| `06-agradecimientos.md` | 5 | Placeholder (heading real + nota de becas/productos) |
| `07-indice.md` | 2 | Solo heading — contenido auto-generado por Pandoc `--toc` |
| `08-abreviaturas.md` | 4 | Placeholder (sección opcional) |
| `09-indice-figuras.md` | 5 | Placeholder (heading real, auto-generado al compilar) |
| `10-indice-tablas.md` | 5 | Placeholder (heading real, auto-generado al compilar) |
| `11-resumen.md` | 9 | Contenido real, movido verbatim, con cursiva agregada a binomios |
| `12-abstract.md` | 7 | Contenido real, movido verbatim, con cursiva agregada a binomios |
| `13-introduccion.md` | 3 | Contenido real, movido verbatim, con cursiva agregada a binomios |
| `14-otros-preliminares.md` | 3 | Placeholder (Dedicatoria — ver punto 7) |

El contenido descartado (no movido a ningún archivo) fue el índice
manual de `ÍNDICE` (líneas 67–207 del original, entradas con número de
página) y las listas manuales de `ÍNDICE DE FIGURAS` e `ÍNDICE DE
TABLAS` (líneas 211–233), porque las instrucciones especifican que
esos tres archivos solo necesitan el heading real — Pandoc `--toc` y
la compilación final de Word regeneran ese contenido automáticamente.

## 2. Headings convertidos de negrita/texto plano a Markdown real

| Archivo | Headings creados | Desglose |
|---|---|---|
| `capitulo-1.md` | 14 | 1× `#`, 9× `##` (1.1–1.9), 4× `###` (1.1.5, 1.5.1, 1.5.2, 1.6.1) |
| `capitulo-2.md` | 5 | 1× `#`, 4× `##` (2.1–2.4) |
| `capitulo-3.md` | 30 | 1× `#`, 10× `##` (3.1–3.10), 19× `###` (3.2.1–3.2.4, 3.3.1–3.3.3, 3.4.1–3.4.5, 3.8.1–3.8.3, 3.9.1–3.9.4) |
| `capitulo-4.md` | 9 | 1× `#`, 3× `##` (4.1–4.3), 5× `###` (4.1.1–4.1.5) |
| `capitulo-5.md` | 3 | 1× `#`, 2× `##` (5.1–5.2) |
| Preliminares (06, 07, 08, 09, 10, 11, 12, 13, 14) | 9 | 1× `#` por archivo |

**Total: 70 headings reales creados** (61 en capítulos + 9 en
preliminares). Todos los títulos previos eran texto en negrita
(`**texto**`) o texto plano sin marcado (`RESUMEN`, `CAPÍTULO 1. ...`,
`1.1 Antecedentes`, etc.) — no existía ni un solo heading Markdown
real (`#`) en ningún archivo de `thesis/` antes de esta revisión.

`00-portada.md` se dejó deliberadamente sin headings (decisión
confirmada): es una página de título, no una entrada del índice
automático.

Leyendas de Tabla/Figura (`**Tabla 3.1 **...`, `**Figura 3.1 **...`) y
los lead-in en negrita de listas (`- **H1a. **`, `- **OE1. **`,
`- **Zenodo****: **`, etc.) se dejaron sin cambios — no son títulos de
sección/subsección, quedan fuera del alcance del Paso 3.

## 3. Correcciones de nomenclatura binomial

Regla aplicada: `Genus species` completo → cursiva; abreviatura
`G. species` válida en cursiva solo si el nombre completo ya apareció
antes en el mismo archivo; si la abreviatura aparece primero, se
corrigió la primera ocurrencia al nombre completo en cursiva.

| Archivo | Ocurrencias con cursiva agregada | Tipo C (expansión de abreviatura-primero) |
|---|---|---|
| `thesis/preliminares/00-portada.md` | 0 (título en mayúsculas, sin cursiva por regla F — solo se limpió el markup `**` malformado) | — |
| `thesis/preliminares/11-resumen.md` | 6 (*Melipona beecheii* ×2, *M. beecheii* ×2, *Apis mellifera*, *Varroa destructor*) | Ninguna — orden ya correcto |
| `thesis/preliminares/12-abstract.md` | 4 (*Melipona beecheii* ×2, *M. beecheii* ×1, *Varroa destructor* ×1) | Ninguna — orden ya correcto |
| `thesis/preliminares/13-introduccion.md` | 3 (*Melipona beecheii*, *Apis mellifera*, *M. beecheii*) | Ninguna — orden ya correcto |
| `capitulo-1.md` | 23 (*M. beecheii* ×18, *Melipona beecheii* ×4 ya-completas, *Apis mellifera* ×3) | **Sí** — línea 11, primera "M. beecheii" del archivo → `*Melipona beecheii*`; línea 13, "M. eburnea" (única ocurrencia) → `*Melipona eburnea*` |
| `capitulo-2.md` | 5 (*Melipona beecheii* ×1 en heading, *M. beecheii* ×3, *Apis mellifera* ×1) | Ninguna — orden ya correcto (forma completa en el heading 2.1, línea 3) |
| `capitulo-3.md` | 9 (*M. beecheii* ×7, *Melipona beecheii* ×1, *Apis mellifera* ×1) | **Sí** — línea 35, primera "M. beecheii" del archivo → `*Melipona beecheii*` |
| `capitulo-4.md` | 13 (*M. beecheii* ×10, *Melipona beecheii* ×1, *Apis mellifera* ×2) | **Sí** — línea 33 (leyenda Tabla 4.1), primera "M. beecheii" del archivo → `*Melipona beecheii*` |
| `capitulo-5.md` | 5 (*Melipona beecheii* ×1, *M. beecheii* ×3, *Varroa destructor* ×1 — corregido de sin-cursiva a cursiva) | Ninguna — orden ya correcto (forma completa en línea 5) |
| `thesis/referencias.md` | 8 (*Apis mellifera* ×1, *Melipona beecheii* ×2, *M. beecheii* ×4, *Melipona eburnea* ×1) | **Sí** — línea 25, primera "M. beecheii" del archivo → `*Melipona beecheii*`; línea 37, "M. eburnea" (única ocurrencia) → `*Melipona eburnea*` |

Notas de tipo D (resolución incidental de markup de negrita partido al
tocar directamente el binomio, sin afectar leyendas de Tabla/Figura en
otros lugares):
- `capitulo-3.md` línea 203: celda de encabezado de tabla
  `**Ref. Apis ****mellifera**` (no es una leyenda de Tabla/Figura,
  es un encabezado de columna) → fusionada a
  `**Ref. *Apis mellifera***`.
- `capitulo-4.md` línea 69: `**Primer dataset multimodal de M.
  ****beecheii****. **` → `**Primer dataset multimodal de *M.
  beecheii*. **`.

Menciones de género solo (`género Melipona`, `Melipona sp.`, `Varroa`
sin epíteto) no se modificaron — no son binomios completos. Menciones
ya en cursiva preexistentes (`*Varroa destructor*` y `*Varroa*` en
`capitulo-4.md` línea 35) se conservaron sin cambios.

`thesis/referencias.md` no estaba en el alcance original de la
exploración pero cae dentro de "TODOS los archivos .md dentro de
thesis/" del Paso 4 — se revisó y corrigió también.

## 4. Discrepancia de numeración de capítulos (solo reportada, sin cambios)

El formato oficial ITESCAM/TecNM especifica **numeración romana
(I–IV) y 4 capítulos**: I. Antecedentes/justificación/hipótesis/
objetivos, II. Materiales y Métodos, III. Resultados y Discusiones,
IV. Conclusiones. El repo actual usa **numeración arábiga (1–5) y 5
capítulos** (Propósito y Organización se trata como capítulo separado
del resto). No se modificó — requiere confirmación explícita de la
Dra. Marlene Méndez Moreno (directora) antes de cualquier
renumeración, ya que afecta referencias cruzadas en todo el documento
(p. ej. "sección 1.1.5", "Tabla 4.1", "Capítulo 3").

Adicionalmente, dentro de `capitulo-1.md`, la subsección `1.1.5` (línea
9) aparece sin que existan `1.1.1`–`1.1.4` en ningún lugar del archivo
— un salto de numeración que tampoco se corrigió (mismo criterio:
requiere confirmación del asesor, no se renumera por iniciativa
propia).

## 5. Hallazgos del Paso 6 (formato general)

- **Orden cronológico de citas APA multi-fuente**: revisados los 5
  capítulos y `referencias.md` — no se encontró ninguna cita con
  múltiples fuentes separadas por punto y coma. Todas las citas en el
  cuerpo del texto son de una sola fuente (`(Moo-Valle et al., 2000)`,
  `(Suárez Carvajal, 2025)`, `(dos Santos et al., 2025)`,
  `(Uthoff et al., 2023)`, `(Chin-Canché et al., 2026)` ×2, etc.). No
  se agregó ningún marcador `<!-- REVISAR ORDEN CRONOLÓGICO DE CITAS -->`.
- **Numeración "Figura X.Y" / "Tabla X.Y"**: las leyendas existentes
  (`Tabla 3.1`, `Figura 3.1`, `Tabla 4.1`, etc.) ya siguen el formato
  sin punto después del número de capítulo — conforme, sin cambios
  necesarios.

## 6. `docs/EXPORTACION.md`

Creado en `docs/EXPORTACION.md` (raíz del repo) con el comando Pandoc
de referencia, actualizado para apuntar a `thesis/preliminares/` (el
comando original de las instrucciones omitía ese subdirectorio). Nota
explícita de que los documentos 01–05 se insertan manualmente como
PDF/escaneo y de que `14-otros-preliminares.md` no forma parte del
comando de exportación.

## 7. Contenido de `14-otros-preliminares.md`

La única sección de `preliminares.md` que no encajó en las 13
secciones oficiales fue **"Dedicatoria"** (línea 43 del original): una
línea de título sin contenido, ubicada entre el placeholder de
"Análisis anti-plagio" (05) y "Agradecimientos" (06). Se movió a
`14-otros-preliminares.md` con heading `# Dedicatoria` y un placeholder
`<!-- PENDIENTE: agregar dedicatoria -->` (no existe texto de
placeholder oficial para esta sección en las instrucciones originales,
por no ser una de las 13 secciones — este texto se infirió siguiendo
el mismo patrón que 06-agradecimientos.md).

Este archivo **no se incluyó** en el comando Pandoc de
`docs/EXPORTACION.md`, ya que no forma parte de las 13 secciones
oficiales; su inclusión y posición en el documento final quedan
pendientes de confirmación con la asesora.

## Notas adicionales

- El comando Pandoc verbatim de las instrucciones originales usaba
  rutas `thesis/00-portada.md`, etc., sin el subdirectorio
  `preliminares/`. Se corrigió en `docs/EXPORTACION.md` para reflejar
  la ubicación real de los archivos (`thesis/preliminares/...`).
- El nombre de archivo de salida del comando (`tesis_final.docx`) se
  mantuvo tal cual se especificó en las instrucciones originales.

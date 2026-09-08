# Revisión de tesis KaabLab — septiembre 2026

Revisión aplicada localmente sobre `CLAUDE.md` y `thesis/`. **No se realizó commit ni push.**

## 1. Resumen ejecutivo

Se corrigió la tesis para reflejar tres decisiones de diseño confirmadas por el asesor que no estaban (o estaban incorrectamente) reflejadas en el texto:

1. **El módulo de visión computacional (OV2640 + YOLOv8 + CNN) se retira** como componente activo del sistema KaabLab, porque *Varroa destructor* —el objetivo original de ese módulo en el artículo de referencia— no parasita a *M. beecheii*. Se conserva únicamente como contexto histórico del artículo de referencia (Chin-Canché et al., 2026), explícitamente marcado como no transferible.
2. **Los roles de humedad/temperatura se corrigen**: SHT31 pasa a ser el sensor interno primario (antes ambiguo/externo); DHT22 pasa a ser el sensor externo secundario (antes tratado como redundante interno). Esto obligó a reescribir el mecanismo de fusión sensorial: ya no es un promedio ponderado de dos lecturas del mismo punto, sino una comparación diagnóstica interno–externo (M. beecheii es termoconformadora, con desfase térmico de 5–6 h).
3. **El rol del INMP441 se corrige**: pasa de "comportamiento defensivo" a "nivel acústico y vitalidad general de la colonia". El comportamiento defensivo en meliponinos se expresa por vibración de sustrato (MPU6050), no por sonido aéreo.

Además se agregó un **sensor IR doble haz** de conteo de tráfico en piquera (ausente del documento original) y una **sección de brechas bibliográficas** (Capítulo 1) que documenta explícitamente qué no existe publicado para *M. beecheii* en los cuatro parámetros que mide el sistema.

Se corrigió toda la numeración de capítulos de romana a arábiga (afecta encabezados de los 5 capítulos y el índice de preliminares) y el rango declarado del INMP441 (de "50–10,000 Hz" a "60 Hz–15 kHz").

## 2. Archivos modificados

| Archivo | Cambios principales |
|---|---|
| `CLAUDE.md` | Reemplazado íntegramente: alumno/asesor, stack de sensores, decisiones de diseño confirmadas, umbrales provisionales, pendientes técnicos e institucionales. |
| `thesis/capitulo-1-proposito-y-organizacion/capitulo-1.md` | Encabezado a arábigo. Nueva sección **1.1.5** (brechas bibliográficas, 4 gaps). Hipótesis H1/H1a sin métricas de visión; **H1c eliminada** (CNN/YOLOv8), renumeradas H1c–H1e. OE1 y OE2 reescritos (dataset sin imágenes, roles de sensores corregidos); **OE5 eliminada** (visión), renumerada OE5←OE6. Alcances (1.7) sin módulo de visión, dataset sin conteo de imágenes. Estrategia experimental (1.8) sin "modelos de visión". Cronograma (fila 9) e presupuesto (Tabla 1.2) actualizados: sensor IR agregado, visión removida, aritmética recalculada. |
| `thesis/capitulo-2-marco-teorico/capitulo-2.md` | Solo encabezado a arábigo. Sin más cambios (no mencionaba visión ni INMP441 con rol incorrecto). |
| `thesis/capitulo-3-metodologia/capitulo-3.md` | Reescritura sustancial. Tabla 3.2 con columna de rol y rango INMP441 corregido. Sección 3.2.1 reescrita (roles interno/externo, autocalibración SHT31 vs. degradación DHT22). Sección 3.2.2 con rol INMP441/MPU6050 corregido. **Nueva 3.2.3** (sensor IR). Fusión sensorial renumerada a 3.2.4, mecanismo rediseñado (contraste interno-externo en vez de promedio). Tabla de pines (3.3.1) sin OV2640, con IR; nota de conflicto GPIO14 agregada. Disposición física (3.3.2) con SHT31 interno / DHT22 externo. Flujo de datos (3.3.3) sin imágenes/YOLO. Preprocesamiento (3.4.5) sin fusión promediada. Arquitectura del sistema (3.5) de 5 capas a 4, sin capa de visión. **Nueva sección 3.6** (interferencia de hardware). Pipeline IA (3.7, antes 3.6) sin ruta de visión. 3.7.4 (CNN/YOLOv8) **eliminada**; subsecciones renumeradas 3.8.1–3.8.3. Protocolo de dataset (3.9, antes 3.8): 3.9.2 reemplaza recolección de imágenes por recolección de conteo IR. Métricas (3.10, antes 3.9): sin mAP/FPS, con precisión de conteo IR y contraste térmico. |
| `thesis/capitulo-4-resultados-y-discusiones/capitulo-4.md` | Encabezado a arábigo. Tabla 4.1: filas CNN/YOLOv8/VarroaDataset retiradas de la tabla activa, movidas a nota histórica explícita; fila de sensor IR agregada; fila de arquitectura sensorial corregida. Sección 4.1.4: bullets de DHT22/propóleos reescritos para reflejar roles interno/externo. Sección 4.1.5: descripción del vector de características corregida. Sección 4.2: dataset sin imágenes, con conteo IR; nueva viñeta de "caracterización de brechas bibliográficas". Discusión (4.3): estimación de "60% reutilizable" corregida a ~40% tras excluir visión, referencia a H1f actualizada a H1e. |
| `thesis/capitulo-5-conclusiones-y-recomendaciones/capitulo-5.md` | Reescrito. Encabezado a arábigo. Conclusiones incluyen ahora la lista explícita de las 5 contribuciones originales (dataset, arquitectura sensorial, preprocesamiento, gaps bibliográficos, sistema validado en campo). Arquitectura sensorial con roles e IR agregados. Recomendaciones: divergencia SHT31/DHT22 reformulada como indicador de propóleos en el sensor interno; nueva recomendación sobre el conflicto GPIO14. |
| `thesis/preliminares/preliminares.md` | Índice: 5 encabezados de capítulo a arábigo, entrada 1.1.5 agregada, bloque completo del Capítulo 3 renumerado (3.2.1–3.2.4, 3.6 nueva, 3.7–3.10 corridos). Índice de tablas: caption de Tabla 3.2 actualizado. RESUMEN, ABSTRACT y palabras clave/keywords reescritos: sin visión computacional/YOLOv8 como componente activo (se menciona solo como excluido), roles de sensores corregidos, IR y vibración agregados a palabras clave. |
| `thesis/referencias.md` | **Archivo nuevo** (no existía; `thesis/referencias.bib` existe pero está vacío y quedó fuera de alcance — ver pendientes). Contiene las 8 referencias solicitadas en formato APA, todas marcadas `<!-- PENDIENTE -->` porque no pude verificar sus datos bibliográficos completos, más una lista de referencias ya citadas en el cuerpo del texto que no formaban parte del alcance de esta revisión. |
| `docs/REVISION_2026-09.md` | Este archivo. |

## 3. Secciones nuevas con contenido provisional (marcadas `<!-- REVISAR CON ASESOR -->`)

- **Capítulo 1, sección 1.1.5** (brechas bibliográficas): dos marcadores — (a) confirmar si existe alguna fuente de frecuencia específica de M. beecheii; (b) revisar el libro de José Quezada para rangos de temperatura específicos.
- **Capítulo 3, sección 3.2.1**: marcador para confirmar los umbrales de temperatura/HR provisionales de `CLAUDE.md`.
- **Capítulo 3, sección 3.2.3** (sensor IR): marcador para confirmar la separación exacta entre haces y el protocolo de montaje en la caja racional.
- **Capítulo 3, sección 3.6** (interferencia de hardware, sección completa nueva): marcador para confirmar el protocolo de aclimatación y si se requiere registro de comportamiento antes/después de instalación.

Todo el contenido de estas secciones fue generado a partir del contexto disponible en `CLAUDE.md` y las instrucciones de revisión; **no reemplaza la validación del asesor**.

## 4. Referencias faltantes o incompletas en `referencias.md`

Las 8 referencias solicitadas están registradas pero **ninguna tiene datos bibliográficos completos verificados** (título exacto, revista/editorial, DOI): Chin-Canché et al. (2026) [complemento de datos], dos Santos et al. (2025), Hrncir et al. (2000, 2006, 2008), Macías-Macías et al. (2011), Moo-Valle et al. (2000), Muniz (año desconocido), Suárez Carvajal (2025). Adicionalmente, las referencias ya citadas en el cuerpo del texto (Bennett 1831, Cauich Kumul et al. 2015, Lóriga Peña et al. 2015, Ramírez-Miranda et al. 2023, Uthoff et al. 2023, Villanueva-Gutiérrez et al. 2014, y los datasets Schurischuster & Kampel 2020 / Yang 2022) se listaron por completitud pero tampoco fueron verificadas en esta revisión.

## 5. Pendientes técnicos sin resolver

- Conflicto GPIO14 (compartido entre SDA del bus I²C — SHT31/MPU6050 — y SCK del bus I²S del INMP441). Documentado en `CLAUDE.md`, en la Tabla 3.3 del Capítulo 3, y como recomendación en el Capítulo 5.
- Umbrales de temperatura/HR provisionales pendientes de confirmación con el asesor (listados en `CLAUDE.md`, referenciados desde la sección 1.1.5b y 3.2.1).
- Libro de José Quezada sobre temperatura en M. beecheii pendiente de revisión (Capítulo 1, sección 1.1.5b).
- Conversión de `referencias.md` a formato `.bib` BibTeX. **Nota:** el repositorio ya contiene `thesis/referencias.bib`, pero está vacío; no se modificó en esta revisión porque el prompt de origen asume `referencias.md` como archivo de trabajo. Se recomienda decidir cuál de los dos archivos es la fuente canónica antes de la siguiente revisión.
- Separación exacta entre haces del sensor IR y protocolo de montaje en la caja racional, pendiente de validación física.
- Protocolo de aclimatación (2–4 semanas) y necesidad de registro de comportamiento antes/después de la instalación de hardware, pendiente de confirmación con el asesor.
- Las 8 referencias nuevas (y las ya citadas listadas en `referencias.md`) requieren completar datos bibliográficos verificados antes de compilar la bibliografía final.

## 6. Pendientes institucionales

- Confirmar la política de propiedad intelectual de ITESCAM (Dirección de Vinculación/Investigación) antes de definir licencia o acuerdo formal con el equipo de mecatrónica colaborador.
- Formalizar cualquier acuerdo de colaboración conforme a la legislación mexicana aplicable.

## 7. Notas sobre decisiones tomadas sin confirmación explícita del prompt

- El prompt de origen refería `thesis/referencias.md`; el repositorio real tiene `thesis/referencias.bib` (vacío). Se creó `referencias.md` como archivo nuevo, sin tocar `referencias.bib`, dejando la reconciliación como pendiente (sección 5).
- La renumeración de hipótesis (H1c eliminada, H1d–H1f → H1c–H1e) y objetivos (OE5 eliminado, OE6 → OE5) no estaba explícitamente solicitada, pero se aplicó para evitar huecos de numeración tras retirar el módulo de visión.
- La renumeración completa de las subsecciones del Capítulo 3 (3.2.1–3.2.4, nueva 3.6, corrimiento de 3.6–3.9 a 3.7–3.10) se hizo por la misma razón; se actualizó el índice de preliminares en consecuencia.
- El presupuesto y cronograma del Capítulo 1 se recalcularon aritméticamente (sensor IR ~$40 MXN agregado, fila de visión reemplazada) — los montos exactos deben validarse con cotizaciones reales.
- La estimación "60% de componentes reutilizables" del Capítulo 4/5 se corrigió a "~40%" tras retirar del cálculo los componentes de visión; es una estimación aproximada basada en el conteo de filas de la Tabla 4.1, no un cálculo formal ponderado.
- **Resuelto (2026-09, sesión de seguimiento):** se detectó que `CLAUDE.md` nombraba un asesor distinto (Dr. Felipe Ángel Álvarez Salgado) al comité tutorial real de la portada de `preliminares.md` (Director: Dra. Marlene Méndez Moreno · Codirector: Dr. Rogelio Alfredo Flores Haas · Asesor interno: Dr. Daniel Bolivar Moreno · Asesor externo: Dr. Henry Jesus Loeza Concha). El usuario confirmó que `preliminares.md` es la fuente correcta; se corrigió `CLAUDE.md` para reflejar el comité tutorial real. `preliminares.md` no se modificó (ya era correcto).

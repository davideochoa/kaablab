# Reestructuración de capítulos de la tesis — 2026-09-17

Registro de la reestructuración solicitada: fusión de los antiguos
Capítulos 1 (Propósito y organización) y 2 (Marco teórico) en un solo
Capítulo I; renumeración de Metodología (antiguo Cap. 3) a Capítulo II;
renumeración de Resultados (antiguo Cap. 4) a Capítulo III; y división
del antiguo Capítulo 5 (Conclusiones y recomendaciones) en Capítulo IV
(Recomendaciones) y Capítulo V (Conclusiones), según
`thesis/docs/FORMATO_TESIS.md` (numeración romana de capítulos).

No se hizo commit ni push — todos los cambios quedan en el working tree
para revisión.

## 1. Archivos creados

- `thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md`
  (fusión de los antiguos capitulo-1.md + capitulo-2.md)
- `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`
  (renumeración del antiguo capitulo-3.md)
- `thesis/capitulo-3-resultados-y-discusiones/capitulo-3.md`
  (renumeración del antiguo capitulo-4.md)
- `thesis/capitulo-4-recomendaciones/capitulo-4.md`
  (mitad "Recomendaciones" del antiguo capitulo-5.md)
- `thesis/capitulo-5-conclusiones/capitulo-5.md`
  (mitad "Conclusiones" del antiguo capitulo-5.md)
- `docs/REESTRUCTURACION_2026-09.md` (este archivo)

## 2. Archivos/carpetas eliminados

- `thesis/capitulo-1-proposito-y-organizacion/` (contenido fusionado al nuevo Capítulo I)
- `thesis/capitulo-2-marco-teorico/` (contenido fusionado al nuevo Capítulo I)
- `thesis/capitulo-3-metodologia/` (renombrado/renumerado a Capítulo II)
- `thesis/capitulo-4-resultados-y-discusiones/` (renombrado/renumerado a Capítulo III)
- `thesis/capitulo-5-conclusiones-y-recomendaciones/` (dividido en Capítulos IV y V)

## 3. Archivos modificados (referencias cruzadas actualizadas)

- `thesis/preliminares/07-indice.md` — reescrito completo con la nueva
  estructura de 5 capítulos (numeración romana en títulos, 1.1.1–1.1.5
  nuevos en Capítulo I, 2.1–2.10 en Capítulo II, 3.1–3.3 en Capítulo III,
  4.1 en Capítulo IV, 5.1 en Capítulo V).
- `CLAUDE.md` — árbol de "Estructura del repo" actualizado a las 5
  carpetas nuevas; referencia `thesis/capitulo-3.md, Tabla 3.3` →
  `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md, Tabla 2.3`;
  "Establecer rangos... en Capítulo 3" → "...en el Capítulo II".
- `README.md` (raíz) — árbol de `## Estructura del repositorio`
  actualizado a las 5 carpetas nuevas.
- `software/sensor-trafico/README.md` — 5 referencias a
  `capitulo-3-metodologia/capitulo-3.md` → `capitulo-2-materiales-y-metodos/capitulo-2.md`;
  sección 3.9.2→2.9.2; sección 3.2.3→2.2.3 (×3); Tabla 3.3→2.3.
- `software/sensor-trafico/ir_doble_haz_conteo.ino` — 1 referencia,
  sección 3.9.2→2.9.2, ruta actualizada.
- `software/sensor-trafico/concepto_deteccion.svg` — texto
  `capitulo-3.md §3.9.2` → `capitulo-2.md §2.9.2`.
- `software/sensor-audio/README.md` — 3 referencias: ruta actualizada
  (×3), sección 3.2.2→2.2.2, Tabla 3.3→2.3. (Las referencias internas
  "sección 2.1/2.2/2.3" de ese mismo README, a sus propias secciones 0–5,
  **no se tocaron** — son autorreferencias del documento, no citas a la
  tesis.)
- `software/sensor-audio/inmp441_i2s_capture.ino` — 1 referencia, ruta y
  Tabla 3.3→2.3 actualizadas.
- `software/sensor-temperatura-humedad-precision/README.md` — 4
  referencias: ruta actualizada (×4), sección 3.4.5→2.4.5,
  sección 3.2.1→2.2.1, sección 3.2.4→2.2.4, secciones 3.2.1/3.4.5→2.2.1/2.4.5.
- `software/sensor-temperatura-humedad-precision/sht31_lectura.ino` — 2
  referencias, ruta y secciones (3.2.4→2.2.4; 3.2.1/3.4.5→2.2.1/2.4.5)
  actualizadas.
- `software/sensor-temperatura-humedad-basico/README.md` — 3
  referencias: ruta actualizada (×3), sección 3.4.5→2.4.5,
  sección 3.2.1→2.2.1, secciones 3.2.1/3.2.4/3.4.5→2.2.1/2.2.4/2.4.5.
- `software/sensor-temperatura-humedad-basico/dht22_lectura.ino` — 1
  referencia, ruta y secciones 3.2.1/3.4.5→2.2.1/2.4.5 actualizadas.

Dentro de los capítulos fusionados/renumerados también se resolvieron
referencias cruzadas internas: "sección 3.2.1" (contraste SHT31/DHT22,
citada dos veces en el antiguo Cap. 4) → "sección 2.2.1"; "el Capítulo 3"
(preprocesamiento, citado en el antiguo Cap. 4 sección 4.1.5) →
"el Capítulo II"; "(Sección 4.2)" (autorreferencia del antiguo Cap. 4) →
"(sección 3.2)"; "Tabla 4.1" (citada en Discusión del antiguo Cap. 4 y
en Conclusiones del antiguo Cap. 5) → "Tabla 3.1"; "sección 3.6"
(aclimatación, citada en Recomendaciones) → "sección 2.6"; "sección 3.2.1"
(propóleos, citada en Recomendaciones) → "sección 2.2.1". Las
referencias a "sección 1.1.5" y sus incisos (a–e) se dejaron sin cambio
de número, tal como se indicó.

## 4. Mapa completo de renumeración aplicado

### 4.1 Capítulos

| Antes | Después |
| --- | --- |
| Capítulo 1. Propósito y organización | Fusionado en Capítulo I |
| Capítulo 2. Estado del arte o marco teórico | Fusionado en Capítulo I |
| Capítulo 3. Metodología (Materiales y Métodos) | Capítulo II. Materiales y Métodos |
| Capítulo 4. Resultados y Discusiones | Capítulo III. Resultados y Discusiones |
| Capítulo 5 § 5.2 Recomendaciones | Capítulo IV. Recomendaciones |
| Capítulo 5 § 5.1 Conclusiones | Capítulo V. Conclusiones |

### 4.2 Capítulo I (fusión 1+2)

| Contenido | Antes | Después |
| --- | --- | --- |
| Antecedentes (párrafos Chin-Canché) | 1.1 | 1.1 (sin cambio) |
| Meliponicultura maya y *M. beecheii* (texto narrativo) | 2.1 | 1.1.1 |
| Limitaciones del artículo de referencia | 2.2 | 1.1.2 |
| Hallazgos metodológicos clave | 2.3 | 1.1.3 |
| Amenazas bióticas | 2.4 | 1.1.4 |
| Brechas bibliográficas (a–e) | 1.1.5 | 1.1.5 (sin cambio de número) |
| Tabla "Parámetros documentados vs. no documentados" | Tabla 2.1 | Tabla 1.1 |
| Tabla "Registros previos... manuales vs. automatizado" + párrafo de síntesis | Tabla 2.2 | Tabla 1.2 |
| Planteamiento, pregunta, hipótesis, objetivos, justificación, alcances, estrategia | 1.2–1.8 | 1.2–1.8 (sin cambio) |
| Planeación: recursos, cronograma y presupuesto | 1.9 | 1.9 (sin cambio) |
| Tabla cronograma | Tabla 1.1 | Tabla 1.3 |
| Tabla presupuesto | Tabla 1.2 | Tabla 1.4 |

### 4.3 Capítulo II (antiguo Capítulo 3 completo)

Todas las secciones 3.X → 2.X, subsecciones 3.X.Y → 2.X.Y, Tablas
3.X → 2.X, Figuras 3.X → 2.X, uno a uno y sin excepciones:
3.1→2.1, 3.2→2.2, 3.2.1→2.2.1, 3.2.2→2.2.2, 3.2.3→2.2.3, 3.2.4→2.2.4,
3.3→2.3, 3.3.1→2.3.1, 3.3.2→2.3.2, 3.3.3→2.3.3, 3.4→2.4, 3.4.1→2.4.1,
3.4.2→2.4.2, 3.4.3→2.4.3, 3.4.4→2.4.4, 3.4.5→2.4.5, 3.5→2.5, 3.6→2.6,
3.7→2.7, 3.8→2.8, 3.8.1→2.8.1, 3.8.2→2.8.2, 3.8.3→2.8.3, 3.9→2.9,
3.9.1→2.9.1, 3.9.2→2.9.2, 3.9.3→2.9.3, 3.9.4→2.9.4, 3.10→2.10;
Tabla 3.1→2.1, Tabla 3.2→2.2, Tabla 3.3→2.3, Tabla 3.4→2.4;
Figura 3.1→2.1, Figura 3.2→2.2, Figura 3.3→2.3, Figura 3.4→2.4.
La referencia interna "sección 1.1.5b" no cambió de número.

### 4.4 Capítulo III (antiguo Capítulo 4 completo)

4.1→3.1, 4.1.1→3.1.1, 4.1.2→3.1.2, 4.1.3→3.1.3, 4.1.4→3.1.4,
4.1.5→3.1.5, 4.2→3.2, 4.3→3.3; Tabla 4.1→3.1. Referencias cruzadas al
antiguo Cap. 3 dentro de este capítulo (sección 3.2.1 ×2, "el Capítulo
3") se remapearon a Capítulo II (sección 2.2.1 ×2, "el Capítulo II") —
mapeo distinto del 4.x→3.x local, verificado para no confundir ambos
capítulos de origen. La referencia a "sección 1.1.5" no cambió.

### 4.5 Capítulos IV y V (división del antiguo Capítulo 5)

- Antigua sección 5.2 (Recomendaciones) → Capítulo IV, sección 4.1.
  Referencias internas: sección 3.6→2.6, sección 3.2.1→2.2.1.
- Antigua sección 5.1 (Conclusiones) → Capítulo V, sección 5.1 (mismo
  número, ahora única sección del capítulo). Referencia interna:
  Tabla 4.1→3.1. La referencia a "sección 1.1.5" no cambió.
- La recomendación sobre el conflicto de GPIO14 ya había sido eliminada
  en una tarea previa a esta reestructuración (el conflicto se
  verificó resuelto en la Tabla 3.3 del entonces Capítulo 3, ahora
  Tabla 2.3 del Capítulo II) — no forma parte de esta reestructuración,
  se menciona aquí solo para que el conteo de recomendaciones (4, no 5)
  no se lea como un error de esta fase.

## 5. Referencias cruzadas que NO se modificaron, con justificación

- `docs/REVISION_2026-09.md` — bitácora histórica de una revisión
  anterior, fechada. Contiene múltiples menciones a "Capítulo 1",
  "Capítulo 3", "Capítulo 4/5", "Tabla 3.2", "Tabla 4.1", rutas
  `capitulo-2-marco-teorico/capitulo-2.md` y
  `capitulo-5-conclusiones-y-recomendaciones/capitulo-5.md`, todas con
  la numeración vigente en la fecha de esa bitácora. Se dejó intacta
  porque es un registro histórico de auditoría (mismo criterio aplicado
  ya en tareas anteriores de esta sesión a este mismo archivo: no se
  reescribe la historia). **Quien la lea después de esta
  reestructuración debe interpretar sus referencias de capítulo/sección
  con la numeración anterior a este cambio.**
- `thesis/docs/REVISION_PRELIMINARES_Y_FORMATO.md` — documento de
  auditoría de formato de una revisión anterior. Menciona "CAPÍTULO
  1. ...", "sección 1.1.5", "Tabla 4.1", "Capítulo 3" como ejemplos
  ilustrativos dentro de un reporte de hallazgos ya cerrado, no como
  cross-references vivas. Se dejó intacto por la misma razón que el
  anterior.

Ambos documentos son bitácoras de auditoría, no documentación viva del
estado actual de la tesis; no se tocaron en ninguna fase de esta
reestructuración.

## 6. Hallazgos NO corregidos por quedar fuera del alcance de esta tarea (para revisión manual)

Estos son problemas de contenido reales, detectados durante la
verificación de referencias cruzadas, pero que **no son** referencias
de número de sección/tabla/figura/capítulo (el alcance explícito de
esta tarea), por lo que no se modificaron:

- `thesis/preliminares/11-resumen.md`, línea 7: el RESUMEN todavía dice
  "caracteriza explícitamente **cuatro** brechas bibliográficas de la
  especie en sus parámetros de medición (sección 1.1.5)". Esto es
  inconsistente con el resto de la tesis, que desde una tarea anterior
  a esta reestructuración ya documenta **cinco** brechas (se agregó
  humedad relativa intranidal como quinta brecha). La referencia a
  "sección 1.1.5" en sí es correcta y no cambió de número; el conteo
  "cuatro" es el error preexistente. Recomendado corregir a "cinco" en
  una próxima tarea.
- `software/sensor-temperatura-humedad-basico/README.md`, líneas
  158–163: sigue hablando de un "desfase esperado por la separación
  interior/exterior" para el diagnóstico de deriva del DHT22 —
  formulación anterior al cambio (de una tarea previa a esta
  reestructuración) que reemplazó el concepto de "desfase fijo de 5–6
  h" por el de "patrón día/noche de termoconformidad" en
  `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md` y en los demás
  capítulos. No es una referencia de número de sección — es contenido
  desactualizado — por lo que se deja para revisión manual.

## 7. Verificación aplicada

- Se confirmó, mediante `grep` recursivo sobre todo el repositorio, que
  no quedan rutas `capitulo-1-proposito-y-organizacion`,
  `capitulo-2-marco-teorico`, `capitulo-3-metodologia`,
  `capitulo-4-resultados-y-discusiones` ni
  `capitulo-5-conclusiones-y-recomendaciones` fuera de la bitácora
  histórica `docs/REVISION_2026-09.md`.
- Se confirmó, mediante `grep`, que no quedan referencias sueltas
  "Capítulo 3", "Capítulo 4", "Capítulo 5" (arábigo) ni "Tabla 3.x" /
  "Tabla 4.x" / "sección 3.x" / "sección 4.x" fuera de las dos
  bitácoras históricas señaladas en la sección 5.
- Se verificó línea por línea que ningún encabezado quedara partido en
  dos líneas de forma que el `sed` de renumeración lo pasara por alto
  (se encontró y corrigió manualmente un caso:
  `software/sensor-audio/README.md`, "sección\n3.2.2" → "sección\n2.2.2").
- Se comparó el listado completo de encabezados (`grep "^#"`) de los 5
  capítulos nuevos contra la estructura reescrita de
  `thesis/preliminares/07-indice.md`: coinciden exactamente.
- Se verificó que `docs/EXPORTACION.md` no requiere cambios: el comando
  de Pandoc usa globs por prefijo (`thesis/capitulo-1*/*.md`, etc.), que
  siguen resolviendo correctamente contra los 5 nombres de carpeta
  nuevos.
- No se tocó `thesis/preliminares/09-indice-figuras.md` ni
  `10-indice-tablas.md` (se generan automáticamente al exportar) ni
  `thesis/preliminares/13-introduccion.md` (sin referencias numeradas).
- No se modificaron `thesis/referencias.md` ni `thesis/referencias.bib`
  (sin referencias de capítulo/sección/tabla).

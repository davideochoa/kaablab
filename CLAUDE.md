# KaabLab — contexto del proyecto

## Descripción

KaabLab es un proyecto de tesis de maestría en Inteligencia Artificial (ITESCAM). Desarrolla un sistema IoT/IA de monitoreo no invasivo para colmenas de *Melipona beecheii* (abeja maya xunan kab), basado en el pipeline de Chin-Canché et al. (2026), validado originalmente en *Apis mellifera* y adaptado aquí a una especie sin aguijón con dinámica de colonia distinta.

## Stack de sensores

- **DHT22 + SHT31** — temperatura y humedad, con redundancia entre ambos sensores.
- **INMP441** — micrófono I2S, sonido aéreo / estado acústico general de la colonia.
- **MPU6050** — IMU, vibración estructural y comportamiento defensivo.
- **IR dual-beam** — conteo de tráfico en la piquera (entradas/salidas).
- **ESP32** — adquisición y control en el nodo de la colmena.
- **Raspberry Pi 4** — procesamiento local / agregación.

## Estructura de carpetas

- `firmware/` — firmware por sensor (`inmp441/`, `mpu6050/`, `ir_counter/`) y firmware principal de integración (`esp32_main/`). Licencia por definir.
- `software/kaablab/` — pipeline Python: preprocesamiento, extracción de características, modelo XGBoost, estudios de ablación. Licencia por definir.
- `thesis/` — texto de la tesis en Markdown, capítulos I–V según el índice oficial, cada uno en su propia carpeta (`capitulo-1-proposito-y-organizacion/` … `capitulo-5-conclusiones-y-recomendaciones/`), más `preliminares/`, `figuras/` y `referencias.bib`. Licencia por definir, sujeto además al reglamento de titulación de ITESCAM/TecNM.
- `data/raw/` — datos crudos, no versionados (ver `.gitignore`). `data/samples/` — muestras pequeñas de referencia, sí versionadas.
- `docs/` — bitácora de diseño y notas de asesor.

## Estado legal

Proyecto desarrollado en colaboración con estudiantes de licenciatura en mecatrónica de la misma institución (ITESCAM). La titularidad de la propiedad intelectual está pendiente de confirmación institucional antes de definir licencias o acuerdos de colaboración formales. Cualquier acuerdo entre colaboradores se rige por la legislación mexicana. Ver [`LICENSE-PENDIENTE.md`](./LICENSE-PENDIENTE.md).

## Convenciones

- Comentarios de código en español o inglés según corresponda al módulo (p. ej. firmware en inglés si sigue convenciones de librerías Arduino/ESP-IDF; pipeline Python en español si es código propio del proyecto).
- Commits en español, formato imperativo corto (p. ej. "Agrega extracción de características MFCC", no "Agregando…" ni "Added…").

## Advertencias

- **No modificar directamente el `.docx` de la tesis institucional.** El contenido en `thesis/*.md` es la fuente de trabajo versionada; la exportación a Word se hace aparte, fuera de este repositorio.

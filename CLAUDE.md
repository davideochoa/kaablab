# KaabLab — Contexto del Proyecto para Claude Code

## Descripción
Tesis de Maestría en Inteligencia Artificial, ITESCAM (Instituto Tecnológico
Superior de Calkiní en el Estado de Campeche, TecNM).

**Alumno:** L.I. David Enrique Ochoa Díaz
**Director:** Dra. Marlene Méndez Moreno
**Codirector:** Dr. Rogelio Alfredo Flores Haas
**Asesor interno:** Dr. Daniel Bolivar Moreno
**Asesor externo:** Dr. Henry Jesus Loeza Concha
**Laboratorio:** Ambientes Inteligentes · ITESCAM

Sistema AIoT de monitoreo no invasivo de colmenas de Melipona beecheii
(xunan kab, abeja maya), adaptando el pipeline de Chin-Canché et al. (2026)
validado originalmente en Apis mellifera.

## Stack de sensores confirmado

| Sensor | Fabricante | Rol | Parámetro |
|---|---|---|---|
| SHT31 / FS400-SHT31 | Sensirion (Suiza) | Interno primario, temp+HR | Temperatura + Humedad absoluta |
| DHT22 | Aosong (Taiwán) | Externo secundario | Temperatura + Humedad exterior |
| INMP441 | InvenSense (EUA) | Audio aéreo, piquera interior | Nivel acústico / vitalidad colonia |
| MPU6050 / GY-521 | TDK InvenSense | Vibración estructural | Comportamiento defensivo (sustrato) |
| IR doble haz | LED 940nm + fototransistor | Conteo tráfico piquera | Entradas / salidas de forrajeras |
| ESP32-CAM | Espressif | Edge device | Coordinación y almacenamiento |
| Raspberry Pi 4 4GB | Raspberry Pi Foundation | Inferencia IA (Sem. 3) | Clasificación en campo |

## Decisiones de diseño confirmadas

- Módulo de visión (OV2640 + YOLOv8 + CNN para detección de intrusos):
  RETIRADO. Varroa destructor no parasita M. beecheii.
- INMP441: captura nivel acústico como proxy de vitalidad y estado general
  de la colonia. NO comportamiento defensivo (los meliponinos expresan
  defensa por vibración de sustrato, no sonido aéreo — dos Santos et al. 2025).
- Rango INMP441: 60 Hz–15 kHz (Suárez Carvajal 2025). NO "50–10,000 Hz".
- MPU6050: sensor primario para comportamiento defensivo vía vibración
  estructural. Montar en contacto directo con la madera de la colmena.
- SHT31 interno: se autocalibraba por encima de ~80–85% HR.
- DHT22 externo: degrada sin recuperación a HR sostenida alta.
- Variable diagnóstica térmica: contraste SHT31(interno) - DHT22(externo),
  no el valor absoluto interno solo (M. beecheii es termoconformadora con
  desfase de 5–6 h — Moo-Valle et al. 2000).
- Sensor IR doble haz: GPIO25 (LED drive), GPIO32 (haz A), GPIO33 (haz B).
  Separación entre haces ~4 mm. Embebido en barreno ~15 mm en pared ≥25 mm.
  Lógica: A→B = entrada, B→A = salida. Modulación IR para rechazo de luz solar.
- Frase "primero del mundo" → "primero documentado para la especie" en todo.
- Conflicto GPIO14 pendiente: asignado como SCK (I²S INMP441) y SDA (I²C)
  simultáneamente — reasignar antes del cableado final.

## Parámetros de medición confirmados por el asesor

Temperatura, humedad y decibeles (nivel acústico de actividad).
Establecer rangos de bajo a alto nivel en Capítulo 3.

Umbrales provisionales de temperatura (confirmar con asesor):
- < 28°C: alerta baja (brood development range, Roubik & Peralta 1983)
- 28–33°C: rango óptimo
- ≥ 34–35°C: alerta temprana (LT50 pupas, Macías-Macías et al. 2011)
- ≥ 38–40°C: crítico (mortalidad de obreras)

Umbrales provisionales de HR (confirmar con asesor):
- < 60% HR: alerta baja
- 60–90% HR: funcional
- > 90% HR: alerta alta

## Pendientes técnicos

- Resolver conflicto GPIO14 antes del cableado final
- Confirmar umbrales temp/HR con asesor antes de finalizar Cap. 3
- Revisar libro de José Quezada sobre temperatura en M. beecheii (Cap. 2)
- Anotar dimensiones cuerpo de abeja y separación de haces en figuras IR
- Convertir referencias.md a formato .bib BibTeX

## Pendientes institucionales

- Confirmar política IP de ITESCAM (Dirección de Vinculación/Investigación)
  antes de definir licencia o acuerdo formal con el equipo de mecatrónica
- Cualquier acuerdo de colaboración debe regirse por ley mexicana

## Estructura del repo

```
kaablab/
├── CLAUDE.md
├── LICENSE-PENDIENTE.md
├── firmware/
│   ├── inmp441/
│   ├── mpu6050/
│   ├── ir_counter/
│   └── esp32_main/
├── software/kaablab/
├── thesis/
│   ├── preliminares/
│   ├── capitulo-1-proposito-y-organizacion/capitulo-1.md
│   ├── capitulo-2-marco-teorico/capitulo-2.md
│   ├── capitulo-3-metodologia/capitulo-3.md
│   ├── capitulo-4-resultados-y-discusiones/capitulo-4.md
│   ├── capitulo-5-conclusiones-y-recomendaciones/capitulo-5.md
│   ├── figuras/ ← SVG únicamente, no PNG
│   └── referencias.md
├── data/
└── docs/
```

## Convenciones

- Commits en español, formato imperativo corto
- Figuras: SVG únicamente, nunca PNG
- NO modificar el .docx institucional directamente
- Los archivos thesis/*.md son la fuente versionada; el .docx se exporta con Pandoc
- NO hacer commit ni push desde sesiones de Claude CLI sin instrucción explícita

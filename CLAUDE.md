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
| ESP32 DevKit V1 | Espressif | Edge device | Adquisición, coordinación y almacenamiento |
| Raspberry Pi 4 4GB | Raspberry Pi Foundation | Inferencia IA (Sem. 3) | Clasificación en campo |

## Decisiones de diseño confirmadas

- Módulo de visión (OV2640 + YOLOv8 + CNN para detección de intrusos):
  RETIRADO. Varroa destructor no parasita M. beecheii.
- INMP441: captura nivel acústico como proxy de vitalidad y estado general
  de la colonia. NO comportamiento defensivo (los meliponinos expresan
  defensa por vibración de sustrato, no sonido aéreo — dos Santos et al. 2025).
- Rango INMP441: 60 Hz–15 kHz (Suárez Carvajal 2025). NO "50–10,000 Hz".
  Confirmado y documentado en software/sensor-audio/README.md.
- MPU6050: sensor primario para comportamiento defensivo vía vibración
  estructural. Montar en contacto directo con la madera de la colmena.
- SHT31 interno: se autocalibraba por encima de ~80–85% HR.
- DHT22 externo: degrada sin recuperación a HR sostenida alta.
- Variable diagnóstica térmica: contraste SHT31(interno) - DHT22(externo),
  no el valor absoluto interno solo (M. beecheii es termoconformadora con
  desfase de 5–6 h — Moo-Valle et al. 2000).
- Sensor IR doble haz: arquitectura vigente usa 4 módulos comerciales
  FC-51/KY-033 (2 pares emisor-receptor, uno por haz), NO 2 — cada módulo
  integra emisor+receptor en la misma placa (reflectivo), por lo que no
  puede formar haz directo cruzado con solo 2 unidades. Haz A: receptor
  principal GPIO26, receptor secundario GPIO25 (mismo par, redundancia/
  diagnóstico de banco). Haz B: receptor principal GPIO27, receptor
  secundario GPIO33. Separación entre haces ~4 mm. Embebido en barreno
  ~15 mm en pared ≥25 mm. Lógica: A→B = entrada, B→A = salida. SIN
  mitigación integrada contra luz solar IR — el diseño discreto con
  modulación IR fue descartado; se depende únicamente del blindaje
  mecánico del tubo de madera. Ver software/sensor-trafico/README.md.
- Frase "primero del mundo" → "primero documentado para la especie" en todo.
- Dispositivo edge confirmado: ESP32 DevKit V1 (no ESP32-CAM). Mapeo de
  pines confirmado, sin conflictos: I²C compartido SHT31+MPU6050/6500
  (SDA=GPIO21, SCL=GPIO22); I²S INMP441 (SCK=GPIO14, WS=GPIO15, SD=GPIO32);
  DHT22 1-Wire (DATA=GPIO4); IR doble haz, 4 módulos FC-51/KY-033 (haz A:
  GPIO26 principal + GPIO25 secundario; haz B: GPIO27 principal + GPIO33
  secundario). Ver thesis/capitulo-2-materiales-y-metodos/capitulo-2.md,
  Tabla 2.3. Al ser DevKit V1 (no
  ESP32-CAM/AI-Thinker), no aplican las restricciones de pines reservados
  a cámara/PSRAM de ese módulo — no asumir esa limitación en tareas
  futuras.

## Parámetros de medición confirmados por el asesor

Temperatura, humedad y decibeles (nivel acústico de actividad).
Establecer rangos de bajo a alto nivel en el Capítulo II.

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

- Confirmar umbrales temp/HR con asesor antes de finalizar Cap. 3
- Revisar libro de José Quezada sobre temperatura en M. beecheii (Cap. 2)
- Anotar dimensiones cuerpo de abeja y separación de haces en figuras IR
- Convertir referencias.md a formato .bib BibTeX
- Validación de banco pendiente — contador IR doble haz (FC-51/KY-033):
  la distancia mínima de detección especificada por el módulo (20–300 mm)
  excede el diámetro del tubo de la piquera (~15 mm), y no hay mitigación
  integrada contra falsos positivos por luz solar IR — se depende del
  blindaje mecánico del tubo de madera. Debe probarse en banco antes de
  instalar en campo; no darlo por diseño cerrado.
- Validación de banco pendiente — MPU6500: confirmar que FS_VIB = 1500 Hz
  (periodo ~667 µs, polling I²C a 400 kHz) sea sostenible en hardware real.
  `sensores_capturar_vibracion()` (software/nodo_kaablab/) imprime por
  Serial una ADVERTENCIA con el conteo de muestras que exceden el periodo
  esperado (+10 %); revisarlo en la primera prueba antes de confiar en
  esa tasa para captura de campo. Ver software/sensor-vibracion/README.md,
  sección 2.2.

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
├── software/
│   ├── kaablab/
│   ├── sensor-vibracion/   # doc: config muestreo vibración estructural (README, .ino, SVG)
│   ├── sensor-audio/       # doc: config muestreo audio I²S (README, .ino, SVG)
│   └── sensor-trafico/     # doc: config conteo tráfico IR doble haz (README, .ino, SVG)
├── thesis/
│   ├── preliminares/
│   ├── capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md
│   ├── capitulo-2-materiales-y-metodos/capitulo-2.md
│   ├── capitulo-3-resultados-y-discusiones/capitulo-3.md
│   ├── capitulo-4-recomendaciones/capitulo-4.md
│   ├── capitulo-5-conclusiones/capitulo-5.md
│   ├── figuras/ ← SVG únicamente, no PNG
│   └── referencias.md
├── data/
└── docs/
```

## Documentos de referencia

- Formato oficial de la tesis (ITESCAM): ver thesis/docs/FORMATO_TESIS.md —
  aplicar en la redacción y el ensamblado final del documento.

## Convenciones

- Commits en español, formato imperativo corto
- Figuras: SVG únicamente, nunca PNG
- NO modificar el .docx institucional directamente
- Los archivos thesis/*.md son la fuente versionada; el .docx se exporta con Pandoc
- NO hacer commit ni push desde sesiones de Claude CLI sin instrucción explícita

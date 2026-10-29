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
| MPU6500 / GY-6500 | TDK InvenSense | Vibración estructural | Comportamiento defensivo (sustrato) |
| IR doble haz, 4 × TCRT5000 | Vishay (sensor óptico reflectivo) + comparador LM393 | Conteo tráfico piquera | Entradas / salidas de forrajeras |
| ESP32 DevKit V1 | Espressif | Edge device | Adquisición, coordinación y almacenamiento |
| Raspberry Pi 4 | Raspberry Pi Foundation | Opcional, fuera de la tesis | Soporte alternativo en software/*/raspberry/ |
| DS3231 | Analog Devices (Maxim) | Reloj de tiempo real (RTC), I²C 0x68 | Marca de tiempo de cada ventana |
| microSD | — | Almacenamiento local, SPI | Ciclos de captura (binario + JSON) |

## Decisiones de diseño confirmadas

- Módulo de visión (OV2640 + YOLOv8 + CNN para detección de intrusos):
  RETIRADO. Varroa destructor no parasita M. beecheii.
- INMP441: captura nivel acústico como proxy de vitalidad y estado general
  de la colonia. NO comportamiento defensivo (los meliponinos expresan
  defensa por vibración de sustrato, no sonido aéreo — dos Santos et al. 2025).
- Rango INMP441: 60 Hz–15 kHz (fuente: hoja de datos del INMP441,
  pendiente de citar). NO "50–10,000 Hz". Suárez Carvajal (2025, estudio
  en *Melipona eburnea*, Colombia) queda solo como contexto de bioacústica
  de meliponinos, no como fuente del rango del micrófono. Documentado en
  software/sensor-audio/README.md.
- MPU6050: sensor primario para comportamiento defensivo vía vibración
  estructural. Montar en contacto directo con la madera de la colmena.
- SHT31 interno: "autocalibración" por encima de ~80–85% HR — verificar
  contra la hoja de datos (SHT3x-DIS) antes de usarlo como hecho.
- DHT22 externo: degrada sin recuperación a HR sostenida alta.
  Alimentación a 3.3 V, pull-up de DATA a 3.3 V; alimentar a 3.3 V; verificar en la hoja de datos el alcance de cable con 3.3 V.
- Variable diagnóstica térmica: contraste SHT31(interno) - DHT22(externo),
  no el valor absoluto interno solo (M. beecheii es termoconformadora con
  desfase de 5–6 h — Moo-Valle et al. 2000).
- Sensor IR doble haz: 4 módulos comerciales TCRT5000 reflectivos
  (emisor IR y fototransistor en el mismo encapsulado + comparador LM393
  en la placa), 2 por "haz" (zona de detección). Cada módulo detecta la
  abeja por la luz IR que refleja su cuerpo; NO se forma haz directo entre
  módulos. Haz A: módulo principal GPIO26, secundario GPIO25 (redundancia/
  diagnóstico de banco). Haz B: principal GPIO27, secundario GPIO33.
  Rango de operación declarado por el fabricante (hoja Vishay TCRT5000):
  0.2–15 mm, pico a 2.5 mm — pendiente de validar en banco. Separación
  entre haces ≥ ~10 mm (ancho de la cabeza óptica del TCRT5000, única parte que va en la piquera; la placa queda en la caja, no se cuenta su ancho), a validar.
  Embebido en barreno
  ~15 mm en pared ≥25 mm. Lógica: A→B = entrada, B→A = salida. SIN
  mitigación integrada contra luz solar IR — el diseño discreto con
  modulación IR fue descartado; se depende únicamente del blindaje
  mecánico del tubo de madera. Alimentación de los módulos: 3.3 V (no 5 V: la salida D0 subiría a 5 V y el ESP32 no lo tolera);
  alimentar a 3.3 V; validar la sensibilidad en banco. Ver software/sensor-trafico/README.md.
- Frase "primero del mundo" → "primero documentado para la especie" en todo.
- Dispositivo edge confirmado: ESP32 DevKit V1 (no ESP32-CAM). Mapeo de
  pines confirmado, sin conflictos: I²C compartido SHT31 +
  DS3231 (0x68) + MPU6500 (0x69, AD0 a 3.3 V) (SDA=GPIO21,
  SCL=GPIO22); I²S INMP441 (SCK=GPIO14, WS=GPIO15, SD=GPIO32);
  DHT22 protocolo propio de un hilo (DATA=GPIO4); IR doble haz, 4 módulos
  TCRT5000 reflectivos (haz A:
  GPIO26 principal + GPIO25 secundario; haz B: GPIO27 principal + GPIO33
  secundario); microSD SPI/VSPI (CS=GPIO5, MOSI=GPIO23, MISO=GPIO19,
  SCK=GPIO18). Ver thesis/capitulo-2-materiales-y-metodos/capitulo-2.md,
  Tabla 2.3. Al ser DevKit V1 (no
  ESP32-CAM/AI-Thinker), no aplican las restricciones de pines reservados
  a cámara/PSRAM de ese módulo — no asumir esa limitación en tareas
  futuras.

## Parámetros de medición confirmados por el asesor

Temperatura, humedad y decibeles (nivel acústico de actividad).
Establecer rangos de bajo a alto nivel en el Capítulo II.

Umbrales provisionales de temperatura (confirmar con asesor):
- Rango intranidal documentado: 25.4–34.0 °C, media 30.2 °C
  (Moo-Valle et al., 2000, M. beecheii, Yucatán).
- Crítico: 40 °C → 90 % de mortalidad de pupas y 40 % de obreras;
  5 °C → 100 % de mortalidad de pupas (Macías-Macías et al., 2011,
  vía Quezada-Euán, 2018).
- < 28 °C: límite inferior de desarrollo de cría según Roubik y Peralta
  (1983), en Melipona de Brasil (congénere, no M. beecheii); provisional,
  no verificado contra el artículo original.
- 28–33 °C (zona óptima): SIN FUENTE: valor de diseño provisional,
  pendiente de confirmar con el asesor.
- ≥ 38–40 °C: SIN FUENTE: valor de diseño provisional, pendiente de
  confirmar con el asesor.

Nota: todos los umbrales de temperatura están sujetos a confirmación del
asesor. Se eliminó el umbral "≥ 34–35 °C: alerta temprana (LT50 pupas)":
Macías-Macías et al. (2011) no reporta LT50 a esa temperatura.

Umbrales provisionales de HR (confirmar con asesor):
- < 60% HR: alerta baja
- 60–90% HR: funcional
- > 90% HR: alerta alta

## Pendientes técnicos

- Confirmar umbrales temp/HR con asesor antes de finalizar Cap. 3
- Revisar libro de José Quezada sobre temperatura en M. beecheii (Cap. 2)
- Anotar dimensiones cuerpo de abeja y separación de haces en figuras IR
- Convertir referencias.md a formato .bib BibTeX
- Validación de banco pendiente — contador IR doble haz (TCRT5000
  reflectivo): confirmar la detección dentro del tubo de ~15 mm (rango
  declarado por el fabricante 0.2–15 mm, pico 2.5 mm, pendiente de validar
  en banco), el reflejo de la pared opuesta del tubo y la separación
  ≥ ~10 mm entre haces (a validar); no hay mitigación
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
├── software/
│   ├── kaablab_pipeline/
│   ├── nodo_kaablab/       # firmware integrado ESP32 DevKit V1 (5 sensores, microSD, HTTP)
│   ├── sensor-vibracion/   # doc: config muestreo vibración estructural (README, arduino/, raspberry/, SVG)
│   ├── sensor-audio/       # doc: config muestreo audio I²S (README, arduino/, raspberry/, SVG)
│   ├── sensor-trafico/     # doc: config conteo tráfico IR doble haz (README, arduino/, raspberry/, SVG)
│   ├── sensor-temperatura-humedad-basico/     # DHT22 (README, arduino/, raspberry/, SVG)
│   └── sensor-temperatura-humedad-precision/  # SHT31 (README, arduino/, raspberry/, SVG)
│       # Cada sketch en arduino/<sketch>/<sketch>.ino (exigencia del Arduino IDE);
│       # diagrama ESP32 en arduino/diagrama_conexion.svg; Python opcional en raspberry/
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
    └── arquitectura-hardware/README.md  # ruta dual ESP32 / Raspberry Pi, mapeo BCM
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

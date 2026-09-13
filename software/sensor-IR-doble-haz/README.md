# Contador IR doble haz (FC-51 / KY-033) — conteo direccional de tráfico en piquera

Sensor de conteo de tráfico de forrajeo del sistema KaabLab. A diferencia
del INMP441 y el MPU6050 (ver `../sensor-INMP441/` y `../sensor-MPU6050/`),
este sensor no mide una magnitud continua con un rango de frecuencia: mide
**eventos discretos de cruce** (entrada/salida) por la piquera, usados
como proxy de la actividad de forrajeo y la vitalidad general de la
colonia.

Documento dirigido a nivel licenciatura en mecatrónica: se explican tanto
los conceptos (interrupción de haz, debounce, lógica de secuencia) como
la configuración concreta para el ESP32 DevKit V1.

> **Este documento describe un punto de diseño no cerrado, no una
> configuración validada.** Las secciones 1 y 2 documentan una limitación
> crítica pendiente de resolver en banco antes de instalar en campo.

## Contenido de esta carpeta

| Archivo | Contenido |
|---|---|
| `README.md` | Este documento |
| `ir_doble_haz_conteo.ino` | Lectura digital con debounce y lógica de secuencia direccional |
| `diagrama_conexion.svg` | Esquema de conexión ESP32 DevKit V1 ↔ módulos FC-51/KY-033 |
| `concepto_deteccion.svg` | Diagrama conceptual: qué es un evento de cruce y cómo se detecta |

---

## 0. ¿Qué mide este sensor y en qué rango?

![Concepto: detección de tráfico por interrupción de haz IR](./concepto_deteccion.svg)

El contador IR doble haz **no mide una magnitud física continua con un
rango de frecuencia o amplitud**, a diferencia del INMP441 (60 Hz–15 kHz)
o el MPU6050 (300–600 Hz objetivo). Mide **eventos discretos**: cada vez
que una abeja cruza el tubo de la piquera, interrumpe primero un haz
infrarrojo y luego el otro, en un orden que depende de si entra o sale.
Lo que se registra es un **conteo de eventos por unidad de tiempo**
(entradas y salidas agregadas por intervalo, típicamente cada 5 minutos —
ver `thesis/capitulo-3-metodologia/capitulo-3.md`, sección 3.9.2), no una
señal de audio o vibración que deba muestrearse a una tasa fija.

La "unidad de medida" relevante aquí no es Hz sino:

- **Eventos de entrada** (secuencia Haz A → Haz B)
- **Eventos de salida** (secuencia Haz B → Haz A)
- **Tasa neta** (entradas − salidas) por intervalo de agregación

---

## 1. Contexto del problema (pendiente real, diseño no cerrado)

La arquitectura vigente para este sensor usa **módulos integrados
FC-51 y/o KY-033** — cada uno combina en una sola placa: LED emisor IR,
fototransistor receptor, comparador **LM393** y un potenciómetro para
ajustar la sensibilidad/umbral de disparo.

**Problema crítico sin resolver:** la distancia mínima de detección
especificada por estos módulos es de **20–300 mm**, pero el diámetro del
tubo de la piquera donde se instala el sensor es de **~15 mm** — por
debajo del mínimo especificado del fabricante. No hay garantía, solo por
lectura de datasheet, de que el módulo detecte de forma confiable un
objeto (la abeja cruzando) a una distancia menor a la que fue
especificado y calibrado de fábrica. **Este es un punto crítico de
validación en banco antes de instalar (sección 5), no un diseño
cerrado.**

### 1.1 Nota sobre la arquitectura física del doble haz con módulos integrados

**Confirmado:** el proyecto usa 4 módulos FC-51/KY-033 (2 pares), no 2.
Cada módulo integra emisor y receptor en una sola placa (pensado
originalmente para detección por reflexión, no por haz directo). Para
lograr los **dos haces independientes y espacialmente separados** que
requiere la lógica de conteo direccional (Haz A y Haz B, ~4 mm de
separación a lo largo del eje del túnel — ver
`thesis/capitulo-3-metodologia/capitulo-3.md`, sección 3.2.3), el diseño
requiere **dos pares emisor-receptor — es decir, 4 módulos físicos en
total**: dos formando el Haz A (uno a cada lado del tubo) y dos formando
el Haz B, desplazados ~4 mm respecto al primer par.

Dentro de cada par, **ambos módulos tienen su propio fototransistor y
producen una señal `OUT` utilizable** — no hay un módulo "emisor puro" y
otro "receptor puro": ambos son unidades completas enfrentadas. Por eso
se conectan al ESP32 las dos señales `OUT` de cada par (una declarada
"principal" y la otra "secundaria"), en vez de una sola: esto permite,
durante la validación de banco (sección 5), comparar ambas lecturas y
detectar diafonía entre el LED propio de un módulo y su propio receptor,
o decidir cuál de las dos señales resulta más limpia para el conteo
final. Solo la alimentación (VCC/GND) es compartida sin necesidad de
señal adicional al ESP32. Ver el esquema de conexión (sección 4) para el
detalle de pines.

Esta necesidad de 4 módulos con 4 señales digitales (en vez de 2 módulos
con 2 señales) es una consecuencia directa de usar módulos integrados
reflectivos en una configuración de haz directo, y es otro punto a
confirmar físicamente en el montaje real antes de dar el diseño por
cerrado.

---

## 2. Riesgo adicional: falsos positivos por luz solar IR

Los módulos FC-51/KY-033 **no tienen mitigación integrada** contra luz
solar directa u otras fuentes de IR ambiental (a diferencia de un diseño
con modulación IR activa, donde el receptor solo responde a un LED
emisor pulsado a una frecuencia conocida, rechazando luz IR continua de
fondo). En este diseño, la única barrera contra falsos positivos por luz
solar es el **blindaje mecánico del tubo de madera** de la piquera: al
estar el sensor embebido dentro del barreno, se asume que la madera
bloquea la luz solar directa sobre el fototransistor.

Esto es una asunción, no una validación. Si el tubo tiene alguna
filtración de luz (por ejemplo, en el extremo exterior expuesto a la
piquera abierta), el sensor puede generar conteos falsos durante horas de
sol intenso. Debe probarse explícitamente en banco (sección 5).

---

## 3. Código de manejo del sensor (ESP32)

Ver [`ir_doble_haz_conteo.ino`](./ir_doble_haz_conteo.ino).

Pin mapping confirmado del proyecto:

| Señal | Pin ESP32 |
|---|---|
| Haz A — receptor principal | GPIO26 |
| Haz A — receptor secundario (mismo par, diagnóstico) | GPIO25 |
| Haz B — receptor principal | GPIO27 |
| Haz B — receptor secundario (mismo par, diagnóstico) | GPIO33 |

GPIO25 quedó libre para este uso porque el diseño discreto anterior (que
lo usaba como línea de drive de un LED IR) fue descartado en favor de los
módulos FC-51/KY-033 — ver `CLAUDE.md`, sección "Decisiones de diseño
confirmadas". GPIO33 es un GPIO de propósito general sin uso previo en el
mapeo de pines del proyecto (ver `thesis/capitulo-3-metodologia/capitulo-3.md`,
Tabla 3.3), sin conflicto con I²C (21/22), I²S (14/15/32) ni el 1-Wire del
DHT22 (4).

Puntos clave del código:

- **Lectura digital simple** de las 4 señales (`HAZ_A_PIN`, `HAZ_A_SEC_PIN`,
  `HAZ_B_PIN`, `HAZ_B_SEC_PIN`) con `digitalRead()` — sin librerías
  adicionales, ya que los módulos entregan una salida digital ya
  acondicionada por su comparador LM393 interno.
- **Debounce por software no bloqueante** (`updateDebounced()`), aplicado
  a las 4 señales: exige que el estado leído se mantenga estable durante
  `DEBOUNCE_MS` (15 ms por defecto) antes de aceptarlo como un cambio
  real, evitando conteos falsos por rebote/ruido eléctrico de la salida
  del comparador.
- **Lógica de secuencia direccional basada en las señales principales**
  (GPIO26/GPIO27): una máquina de estados (`SEQ_IDLE` / `SEQ_A_FIRST` /
  `SEQ_B_FIRST`) determina si el Haz A se interrumpió antes que el B
  (entrada) o viceversa (salida), con un timeout (`SEQUENCE_TIMEOUT_MS`)
  que descarta la secuencia si el segundo haz no se interrumpe a tiempo.
- **Registro diagnóstico de las señales secundarias** (GPIO25/GPIO33):
  se imprimen por separado cada vez que cambian, para compararlas en
  banco contra la señal principal del mismo par y decidir, tras la
  validación (sección 5), cuál de las dos usar en la versión final —o si
  conviene combinarlas con un OR lógico—.
- **Polaridad configurable** (`BEAM_BROKEN_LEVEL`): documentada como
  pendiente de confirmar en banco, ya que el ajuste del potenciómetro de
  cada módulo puede invertir el nivel lógico de "haz interrumpido".
- Imprime timestamp + evento (`entrada`/`salida`/cambios de señal
  secundaria) + contadores acumulados por puerto serie en formato CSV.

---

## 4. Esquema de conexión

Ver [`diagrama_conexion.svg`](./diagrama_conexion.svg).

Incluye: bus VCC (3.3V) y GND compartido entre los 4 módulos, y las
**cuatro** señales digitales — par A: GPIO26 (principal) y GPIO25
(secundario); par B: GPIO27 (principal) y GPIO33 (secundario) — con la
disposición enfrentada a través del tubo y la separación de ~4 mm entre
pares.

---

## 5. Validación requerida antes de instalación en campo

**No dar por resuelto este diseño únicamente por inspección de datasheet
o de código.** Antes de instalar en una colmena real, se requiere:

1. **Prueba de banco con el tubo real (~15 mm de diámetro):** confirmar
   si los módulos FC-51/KY-033, montados a esa distancia — por debajo de
   su mínimo especificado de 20–300 mm —, detectan de forma confiable el
   cruce de un objeto del tamaño de una obrera de *M. beecheii* (~10 mm),
   sin zonas ciegas ni disparos erráticos. Ajustar el potenciómetro de
   sensibilidad de cada módulo como parte de esta prueba, no asumir el
   ajuste de fábrica.
2. **Prueba de exposición a luz solar directa:** con el sensor embebido
   en el barreno real, exponer el extremo exterior del tubo a sol directo
   e intenso y verificar si se generan conteos falsos (transiciones de
   `OUT` sin cruce real de un objeto).
3. **Confirmación de polaridad de `BEAM_BROKEN_LEVEL`** (sección 3) con
   multímetro u osciloscopio sobre la salida real de cada módulo.
4. **Verificación de la lógica de secuencia** con cruces reales o
   simulados en ambas direcciones, confirmando que `SEQUENCE_TIMEOUT_MS`
   (300 ms) es adecuado para la velocidad de tránsito observada.

### Si la validación falla

Si el bench de banco muestra que los módulos FC-51/KY-033 no detectan de
forma confiable a ~15 mm, o que los falsos positivos por luz solar
persisten pese al blindaje mecánico, se deja anotado como alternativas a
evaluar:

- **Sensores con menor distancia mínima de detección** especificada,
  compatibles con el diámetro real del tubo.
- **Rediseño con el circuito discreto** (fototransistor **PT333-3B** +
  comparador **LM393** + transistor driver para el LED, descrito en
  `thesis/capitulo-3-metodologia/capitulo-3.md`, sección 3.2.3) —
  descartado previamente en favor de los módulos integrados por
  simplicidad de ensamblaje, pero que sí permite ajustar libremente la
  distancia física y la modulación del emisor/receptor sin las
  restricciones de un módulo comercial cerrado.

Solo después de completar esta validación se debe considerar el diseño
listo para cableado final en campo.

---

## Referencias

- Muniz, [Nombres pendientes]. (s.f.). [Título completo pendiente —
  conteo por infrarrojo en *Melipona* sp.]. Ver `thesis/referencias.md`.
- Datasheets de los módulos FC-51 y KY-033 (fabricante genérico,
  variable según proveedor) — sección de distancia de detección
  especificada y ajuste del potenciómetro de sensibilidad. Confirmar
  edición/proveedor exacto del lote de módulos usado antes de la entrega
  final de la tesis.
- `thesis/capitulo-3-metodologia/capitulo-3.md`, sección 3.2.3 — diseño
  de referencia con circuito discreto (PT333-3B + LM393 + 2N2222).

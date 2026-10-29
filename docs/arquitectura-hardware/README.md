# Arquitectura de hardware — nodo de borde dual (ESP32 / Raspberry Pi)

Documento de arquitectura del sistema KaabLab. Describe las dos
implementaciones de hardware soportadas para el nodo de borde que
adquiere las cinco señales sensoriales del proyecto, y el mapeo de
pines de la variante Raspberry Pi. Dirigido a nivel licenciatura en
mecatrónica.

El detalle de implementación específico de cada sensor (principio
físico, rangos, justificación de diseño) vive en
`thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, sección 2.2. Este
documento cubre exclusivamente la capa de hardware/firmware del nodo
de borde: qué microcontrolador o computador de placa única lo ejecuta,
y cómo se conecta cada sensor a él.

---

## 1. Resumen de la arquitectura dual

El nodo de borde del sistema KaabLab puede implementarse sobre **dos
plataformas de hardware distintas**, ambas activas en paralelo dentro
del proyecto — **ninguna reemplaza a la otra**:

| Ruta | Plataforma | Estado de documentación |
|---|---|---|
| **A — Arduino/ESP32** | ESP32 DevKit V1, firmware en C++ (Arduino framework) | **Ya documentada y vigente.** Código (`.ino`, cada sketch en `arduino/<nombre_sketch>/<nombre_sketch>.ino`, como exige el Arduino IDE) y diagrama de conexión (`arduino/diagrama_conexion.svg`) en la subcarpeta `arduino/` de cada sensor: `software/sensor-vibracion/arduino/`, `software/sensor-audio/arduino/`, `software/sensor-trafico/arduino/`, `software/sensor-temperatura-humedad-basico/arduino/` y `software/sensor-temperatura-humedad-precision/arduino/`. El README conceptual (qué mide, rango, por qué) vive un nivel arriba, en la raíz de cada carpeta de sensor. |
| **B — Raspberry Pi** | Raspberry Pi (modelo mínimo recomendado: sección 2), firmware en Python (Linux). **Opcional, fuera del alcance de la tesis** (ver `CLAUDE.md`) | Arquitectura y mapeo de pines documentados en este archivo (secciones 2–4). Código Python de adquisición disponible para los **cinco** sensores: vibración estructural (`software/sensor-vibracion/raspberry/`, Ruta A únicamente, riesgo de jitter pendiente de validar en banco — sección 3.1), sonido aéreo (`software/sensor-audio/raspberry/`, I²S por hardware/DMA — sin el mismo riesgo de jitter, sección 3), tráfico de forrajeo (`software/sensor-trafico/raspberry/`, detección por eventos GPIO — riesgo de orden de eventos en el conteo direccional, sección 3.3), temperatura/humedad básico (`software/sensor-temperatura-humedad-basico/raspberry/`, protocolo de un solo hilo vía `pigpio` — riesgo de confiabilidad confirmado, con mitigación parcial, pendiente de validar en banco — sección 3.2) y temperatura/humedad de precisión (`software/sensor-temperatura-humedad-precision/raspberry/`, I²C compartido con el sensor de vibración — throughput analizado, latencia puntual pendiente de confirmar en banco — sección 3.2). |

Los cinco sensores son los mismos en ambas rutas — solo cambia el
microcontrolador/computador que los lee y el lenguaje del firmware:

| Sensor (nombre funcional) | Rol | Protocolo | `arduino/` (código vigente) | `raspberry/` (código Python) |
|---|---|---|---|---|
| Sensor de vibración estructural | Comportamiento defensivo (sustrato) | I²C | `software/sensor-vibracion/arduino/` | `software/sensor-vibracion/raspberry/` (Ruta A; jitter pendiente de validar, sección 3.1) |
| Sensor de sonido aéreo | Nivel acústico / vitalidad de la colonia | I²S | `software/sensor-audio/arduino/` | `software/sensor-audio/raspberry/` (I²S por hardware/DMA; validación de equivalencia pendiente, ver README del sensor sección 5) |
| Sensor de tráfico de forrajeo | Conteo direccional en piquera | GPIO digital (4 señales) | `software/sensor-trafico/arduino/` | `software/sensor-trafico/raspberry/` (detección por eventos; orden A/B pendiente de validar, sección 3.3) |
| Sensor de temperatura y humedad (rango básico) | Externo secundario | Protocolo propietario de un hilo | `software/sensor-temperatura-humedad-basico/arduino/` | `software/sensor-temperatura-humedad-basico/raspberry/` (vía `pigpio`; riesgo de confiabilidad confirmado, mitigación parcial, pendiente de validar en banco, sección 3.2) |
| Sensor de temperatura y humedad (rango de precisión) | Interno primario | I²C | `software/sensor-temperatura-humedad-precision/arduino/` | `software/sensor-temperatura-humedad-precision/raspberry/` (bus I²C compartido con vibración; throughput analizado, latencia puntual pendiente de confirmar en banco, sección 3.2) |

**¿Por qué dos rutas de hardware?** El ESP32 DevKit V1 es la
implementación de referencia del proyecto: bajo costo, bajo consumo
(crítico para operación con batería/panel solar), y firmware bare-metal
con temporización predecible — ver sección 3 sobre por qué esto
importa para el sensor de vibración. La ruta Raspberry Pi se documenta
como alternativa porque comparte el mismo ecosistema Python/Linux que
la capa de inferencia de IA del proyecto (Raspberry Pi 4 como soporte
opcional, fuera del alcance de la tesis, ver `CLAUDE.md`), lo que simplifica correr el modelo de
clasificación **directamente en el nodo de borde** en vez de un
dispositivo separado, a costa de perder el determinismo temporal del
ESP32 (sección 3).

---

## 2. Nodo de borde Raspberry Pi: modelo mínimo recomendado

Para que la ruta B sea viable, el modelo de Raspberry Pi elegido debe
tener RAM/CPU suficiente para: (a) muestrear las cinco señales en
paralelo (I²C, I²S, GPIO digital), y (b) correr inferencia con
**TensorFlow Lite** sobre el vector de características resultante,
simultáneamente.

### 2.1 Candidatos evaluados

| Característica | Raspberry Pi Zero 2W | Raspberry Pi 4 (2GB) |
|---|---|---|
| SoC | Broadcom BCM2710A1 | Broadcom BCM2711 |
| CPU | Quad-core Cortex-A53 @ 1.0 GHz | Quad-core Cortex-A72 @ 1.5 GHz |
| RAM | 512 MB LPDDR2 | 2 GB LPDDR4 |
| Conectividad | WiFi 2.4 GHz + BT 4.2 | WiFi dual-band + BT 5.0 + Ethernet |
| GPIO | 40 pines (mismo layout) | 40 pines (mismo layout) |
| Consumo típico | ~1–1.5 W | ~3–5 W |

### 2.2 Justificación: Raspberry Pi 4 (2GB) como mínimo recomendado

**La Raspberry Pi Zero 2W no se recomienda como mínimo** para este
proyecto, pese a compartir el mismo layout de GPIO:

- Sus **512 MB de RAM** deben cubrir simultáneamente el sistema
  operativo Linux, el runtime de Python, los buffers de los cinco
  sensores (en particular el buffer de audio I²S del sensor de sonido
  aéreo y el muestreo continuo del sensor de vibración estructural), y
  el intérprete de **TensorFlow Lite** con el modelo cargado en
  memoria. En la práctica, esto deja muy poco margen antes de recurrir
  a swap sobre tarjeta microSD — que es órdenes de magnitud más lento
  que RAM y puede introducir latencia impredecible justo en la etapa
  de inferencia.
- Su CPU a 1.0 GHz (misma microarquitectura Cortex-A53, sin el salto a
  Cortex-A72) es sensiblemente más lenta para inferencia que la Pi 4,
  incrementando la latencia de alerta (objetivo del proyecto: < 60 s,
  Tabla 2.5 del Capítulo 2).

**La Raspberry Pi 4 (2GB) sí se recomienda como mínimo**: sus 2 GB de
RAM dan margen cómodo para el sistema operativo, los cinco drivers de
sensor y el runtime de TensorFlow Lite corriendo de forma concurrente,
sin recurrir a swap en operación normal, y su CPU Cortex-A72 a 1.5 GHz
reduce la latencia de inferencia frente a la Zero 2W.

### 2.3 Compatibilidad hacia modelos superiores

Modelos superiores — **Raspberry Pi 4 (4GB/8GB)** (soporte opcional,
fuera del alcance de la tesis, ver `CLAUDE.md`) y
**Raspberry Pi 5** — son compatibles con esta arquitectura **sin
rediseño de pines ni de código**: todos comparten el mismo layout de
GPIO de 40 pines y las mismas interfaces I²C/I²S por software (`Wire`
equivalente vía `smbus2`/`python-periphery`, I²S vía `alsa`/overlay de
device tree). Migrar de un modelo a otro es un cambio de capacidad de
cómputo, no de arquitectura de hardware.

---

## 3. Notas de riesgo: Linux no es tiempo real

Tres sensores de la arquitectura dependen de temporización fina a nivel
de firmware para funcionar correctamente, cada uno de forma distinta
(tasa de muestreo sostenida, timing de protocolo de un solo cable, y
orden relativo de eventos de interrupción). Los tres riesgos son
explícitos y quedan pendientes de validación en banco antes de dar la
ruta Raspberry Pi por cerrada para esos sensores — ver secciones 3.1,
3.2 y 3.3. El sensor de sonido aéreo es la excepción explícita: su uso
de I²S por hardware/DMA no está sujeto a esta clase de riesgo (ver el
docstring de `software/sensor-audio/raspberry/captura_inmp441.py`).

### 3.1 Jitter en el muestreo del sensor de vibración estructural

**Riesgo explícito, pendiente de validación en banco antes de decidir
la migración del sensor de vibración estructural.**

El ESP32 DevKit V1 ejecuta el firmware de adquisición en modo
bare-metal (sin sistema operativo de propósito general): la
temporización del bucle de muestreo, calculada en
`software/sensor-vibracion/README.md` (sección 2.1) para sostener
`FS_VIB` = 1500 Hz con el MPU6500 (DLPF del acelerómetro desactivado,
Nyquist = 750 Hz; periodo ~667 µs), es predecible porque no compite con un planificador
de procesos ni con un sistema de archivos con latencia variable.
Aun así, que la lectura I²C por polling sostenga esos 1500 Hz en el
ESP32 está **pendiente de validar en banco** (ver
`software/sensor-vibracion/README.md`, sección 2.2): la comparación
con Raspberry Pi descrita abajo parte de esa misma validación.

**Raspberry Pi corre Linux, un sistema operativo de propósito general
sin garantías de tiempo real.** El planificador de Linux puede
interrumpir el proceso de muestreo en cualquier momento para atender
otros procesos, interrupciones de hardware, o E/S de red — introduciendo
**jitter** (variación no determinista en el intervalo entre muestras)
que no existe en el firmware bare-metal del ESP32. Este riesgo se
agrava específicamente si:

- La misma Raspberry Pi que muestrea el sensor de vibración también
  ejecuta la inferencia de TensorFlow Lite de forma concurrente
  (sección 2), compitiendo por CPU en el momento exacto en que el
  muestreo de alta tasa necesita atención puntual.
- La tasa objetivo (1500 Hz) deja poco margen: un jitter de solo
  algunos cientos de microsegundos ya representa una fracción
  significativa del intervalo entre muestras (~667 µs a 1500 Hz).

**Esto queda marcado como pendiente de validación en banco, no como
diseño cerrado.** Antes de decidir si el sensor de vibración
estructural migra a la Raspberry Pi junto con el resto de los
sensores, o si se mantiene en un **ESP32 dedicado** (actuando como
coprocesador de tiempo real que entrega al Raspberry Pi ya las
muestras o características extraídas, mientras el resto de los
sensores sí migran), se requiere:

1. Medir en banco el jitter real del muestreo del sensor de vibración
   sobre Raspberry Pi (con y sin inferencia concurrente), usando la
   misma metodología de validación con analizador lógico descrita en
   `software/sensor-vibracion/README.md`, sección 5.
2. Comparar la tasa efectiva resultante contra el criterio de diseño
   del sensor (Nyquist ≥ 750 Hz, es decir `FS_VIB` ≥ 1500 Hz, ver
   `software/sensor-vibracion/README.md`, secciones 2.1–2.2) — si el
   jitter de Linux impide sostener esa tasa, la arquitectura híbrida (vibración en ESP32 dedicado,
   resto en Raspberry Pi) pasa de alternativa a recomendación.

Los sensores de temperatura/humedad básico (sección 3.2) y de tráfico
de forrajeo (sección 3.3) tienen requisitos de temporización propios,
de naturaleza distinta a este. El sensor de sonido aéreo (I²S por
hardware/DMA) es el único sin este tipo de riesgo — ver el docstring de
`software/sensor-audio/raspberry/captura_inmp441.py`.

### 3.2 Confiabilidad del muestreo del sensor de temperatura/humedad básico

**Riesgo confirmado, con mitigación parcial implementada — NO resuelto,
pendiente de validación en banco antes de decidir si el sensor de
temperatura/humedad básico se lee de forma confiable en Raspberry Pi.**

`software/sensor-temperatura-humedad-basico/raspberry/lectura_dht22.py`
ya implementa una mitigación parcial de este riesgo: usa la librería
`pigpio`, cuyo daemon captura el timestamp de cada flanco GPIO (`tick`)
desde un proceso separado que programa hardware de temporizador del
SoC, fuera del planificador de procesos de Python — esto reduce, sin
eliminar, la ventana de vulnerabilidad al jitter descrita más abajo, y
el propio script agrega reintentos automáticos y logging de tasa de
fallos para poder cuantificar el riesgo remanente. Esto **confirma**
que el riesgo es real y mitigable, no que esté cerrado: la mitigación
no cubre el timing del propio pulso de arranque (host manteniendo la
línea en bajo antes de soltarla), que sigue dependiendo de
`time.sleep()` en espacio de usuario — ver el docstring de ese script
para el detalle completo. Ver también
`software/sensor-temperatura-humedad-basico/README.md`, sección 5.

El sensor de temperatura/humedad básico (rango básico, ver
`software/sensor-temperatura-humedad-basico/README.md`, sección 3) usa
un **protocolo digital propietario de un solo cable** que no es I²C ni
1-Wire estándar Dallas: el microcontrolador dispara un pulso de inicio
y decodifica la respuesta del sensor midiendo el ancho de cada pulso
del tren de 40 bits, con umbrales del orden de **decenas de
microsegundos** (p. ej., distinguir un bit `0` de un bit `1` depende de
si el pulso alto dura ~26–28 µs o ~70 µs). Este protocolo no tiene
margen de error de temporización: leerlo requiere que el firmware
muestree el pin de datos con precisión de microsegundo, de forma
ininterrumpida durante la transacción completa (~5 ms).

En el **ESP32 bare-metal**, esta temporización de microsegundos es
confiable: el firmware controla el pin directamente sin un sistema
operativo de propósito general de por medio (ver
`software/sensor-temperatura-humedad-basico/arduino/dht22_lectura/dht22_lectura.ino`,
que usa la librería DHT sensor library para el bit-banging).

**En Raspberry Pi, la misma lectura por software es más frágil que en
el ESP32 bare-metal**, incluso con la mitigación parcial vía `pigpio`
ya implementada en
`software/sensor-temperatura-humedad-basico/raspberry/lectura_dht22.py`
(ver el recuadro de arriba). El planificador de Linux puede
interrumpir el proceso host —por las mismas razones descritas en la
sección 3.1: otros procesos, interrupciones de hardware, E/S de red, o
la propia inferencia de TensorFlow Lite corriendo de forma
concurrente— durante partes de la transacción que sí dependen de
`time.sleep()` en espacio de usuario (el pulso de arranque). Una
interrupción de solo unas pocas decenas de microsegundos en el momento
equivocado ya es suficiente para leer mal un bit (confundir un `0` con
un `1`), lo que se traduce en **lecturas erróneas con mayor
frecuencia** que en el ESP32, o en fallos de lectura directos
(checksum inválido, timeout del protocolo) — mitigados, no eliminados,
por los reintentos automáticos ya implementados en el script.

**Esto queda marcado como pendiente de validación en banco, no como
diseño cerrado.** Antes de decidir si el sensor de temperatura/humedad
básico se lee de forma confiable sobre Raspberry Pi junto con el resto
de los sensores, o si conviene **delegar su lectura a un
microcontrolador auxiliar** (un ESP32 u otro microcontrolador
dedicado, que entregue al Raspberry Pi el valor ya decodificado por un
canal simple —I²C, UART o incluso un par de GPIO con protocolo propio—
en vez de que Raspberry Pi bit-banguee el protocolo propietario
directamente), se requiere:

1. Medir en banco, con el logging de tasa de fallos ya incluido en
   `raspberry/lectura_dht22.py` (clase `RastreadorTasaFallos`), la tasa
   de fallos/lecturas erróneas (checksum inválido, timeout) del sensor
   de temperatura/humedad básico sobre Raspberry Pi durante al menos
   24 h continuas, comparada contra la tasa de fallos ya observada en
   ESP32, bajo carga variable (con y sin inferencia concurrente, igual
   que en la sección 3.1).
2. Si la tasa de fallos en Raspberry Pi resulta significativamente
   mayor, evaluar si basta con reintentos por software (el protocolo
   ya es tolerante a leerse cada ~2 s, sección 0 de
   `software/sensor-temperatura-humedad-basico/README.md`) o si se
   requiere el microcontrolador auxiliar descrito arriba.

### 3.3 Orden de eventos en el conteo direccional del sensor de tráfico de forrajeo

**Riesgo explícito, distinto a los de las secciones 3.1 y 3.2, pendiente
de validación en banco antes de confiar en el conteo DIRECCIONAL de
este sensor sobre Raspberry Pi.**

El sensor de tráfico de forrajeo (ver
`software/sensor-trafico/README.md`, sección 3) no se lee por polling
de alta tasa (como el sensor de vibración) ni por un protocolo de
timing de microsegundos (como el sensor básico de temperatura/humedad):
se lee por **detección de eventos (interrupción) sobre 4 líneas GPIO**,
usando `RPi.GPIO.add_event_detect()`. La lógica de conteo direccional
—si el Haz A se interrumpe antes que el Haz B es una entrada, y
viceversa una salida— depende de que el ORDEN relativo en que este
script recibe los callbacks de ambos haces coincida con el orden real
en que la abeja los interrumpió físicamente.

**En Raspberry Pi/Linux, la detección de eventos GPIO vía
RPi.GPIO/gpiozero no es una interrupción de kernel en tiempo estricto:**
el evento se detecta en el kernel, pero el callback de Python se
despacha en espacio de usuario, con **latencia típica del orden de
milisegundos** — muy por encima de la latencia de una interrupción real
de microcontrolador bare-metal como la del ESP32 (microsegundos). Si el
tiempo real entre la interrupción de un haz y el otro es menor que esa
latencia típica de milisegundos, el orden de llegada de los callbacks a
este script podría no coincidir con el orden físico real, **invirtiendo
la dirección detectada** (una entrada real registrada como salida, o
viceversa).

**El conteo total de cruces (sin dirección) es considerablemente más
robusto a este riesgo** que el conteo direccional: cada interrupción de
haz sigue generando un evento con alta probabilidad, independientemente
del orden en que los callbacks lleguen a Python — solo la asignación de
dirección (entrada vs. salida) es lo que puede degradarse.

**Esto queda marcado como pendiente de validación en banco, no como
diseño cerrado.** Antes de confiar en el conteo direccional producido
por Raspberry Pi, se requiere (ver
`software/sensor-trafico/README.md`, sección 5, para el detalle
completo):

1. Comparar el conteo direccional (entradas/salidas) de
   `software/sensor-trafico/raspberry/conteo_trafico.py` contra el de
   `software/sensor-trafico/arduino/ir_doble_haz_conteo/ir_doble_haz_conteo.ino`, usando el
   mismo patrón de cruces controlados y repetibles en ambas
   plataformas, para cuantificar la tasa de inversión de dirección.
2. Confirmar que la lectura simultánea de las 4 señales no satura la
   GPIO de la Raspberry Pi ni genera falsos triggers por rebote no
   filtrado, comparando contra un analizador lógico independiente.
3. Si la tasa de inversión resulta inaceptable para el objetivo de
   precisión del proyecto (Tabla 2.5 de
   `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`), mantener el conteo
   **direccional** de este sensor en un ESP32 dedicado (entregando a
   Raspberry Pi solo los contadores agregados), aunque el resto de los
   sensores migre a Raspberry Pi — el mismo patrón de arquitectura
   híbrida ya planteado en la sección 3.1 para el sensor de vibración.

---

## 4. Mapeo de pines Raspberry Pi (GPIO BCM)

Equivalente al mapeo de pines ya documentado para ESP32 DevKit V1
(`thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, Tabla 2.3). Numeración
BCM (Broadcom), la que usan las librerías GPIO de Raspberry Pi
(`RPi.GPIO`, `gpiozero`, `python-periphery`) — no confundir con el
número físico de pin del header de 40 pines.

| Sensor | Señal | Protocolo | Pin Raspberry Pi (BCM) | Pin ESP32 equivalente |
|---|---|---|---|---|
| Sensor de sonido aéreo | BCLK (reloj de bit) | I²S | GPIO18 (pin físico 12) | GPIO14 |
| Sensor de sonido aéreo | LRCLK / WS (word select) | I²S | GPIO19 (pin físico 35) | GPIO15 |
| Sensor de sonido aéreo | DIN (datos) | I²S | GPIO20 (pin físico 38) | GPIO32 |
| Sensor de precisión (0x44) + RTC DS3231 (0x68) + sensor de vibración estructural (0x69) | SDA | I²C (bus 1) | GPIO2 (pin físico 3) | GPIO21 |
| Sensor de precisión (0x44) + RTC DS3231 (0x68) + sensor de vibración estructural (0x69) | SCL | I²C (bus 1) | GPIO3 (pin físico 5) | GPIO22 |
| Sensor básico | DATA | Protocolo propietario, un hilo | GPIO4 (pin físico 7) | GPIO4 |
| Sensor de tráfico de forrajeo | Haz A (principal) | GPIO digital | GPIO5 (pin físico 29) | GPIO26 |
| Sensor de tráfico de forrajeo | Haz A (secundario) | GPIO digital | GPIO6 (pin físico 31) | GPIO25 |
| Sensor de tráfico de forrajeo | Haz B (principal) | GPIO digital | GPIO12 (pin físico 32) | GPIO27 |
| Sensor de tráfico de forrajeo | Haz B (secundario) | GPIO digital | GPIO13 (pin físico 33) | GPIO33 |

Notas:

- **Direcciones I²C del bus compartido:** idénticas a la variante
  ESP32 (`thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, sección 2.3.1 y Tabla 2.3):

  | Dispositivo | Dirección | Configuración |
  |---|---|---|
  | SHT31 (sensor de precisión) | 0x44 | ADDR a GND |
  | DS3231 (RTC del sistema) | 0x68 | fija |
  | MPU6500 / GY-6500 (vibración estructural) | 0x69 | AD0 a 3.3 V — obligatorio: 0x68 la ocupa el DS3231 |

  El bus I²C 1 de Raspberry Pi (GPIO2/GPIO3) los soporta sin conflicto,
  igual que en ESP32.
- **Velocidad del bus I²C:** fijar `dtparam=i2c_arm_baudrate=400000` en
  `/boot/firmware/config.txt`. El valor por defecto es 100 kHz y a esa
  velocidad una lectura del MPU6500 (~81 bits) ocupa ~810 µs, más que el
  periodo de ~667 µs: **los 1500 Hz son imposibles a 100 kHz**. La
  velocidad es única para todo el bus (SHT31, DS3231 y MPU6500).
- **DS3231 como RTC del sistema:** la Raspberry Pi no tiene reloj de
  tiempo real propio; el DS3231 se habilita como RTC del kernel con
  `dtoverlay=i2c-rtc,ds3231` en `/boot/config.txt`
  (`/boot/firmware/config.txt` en Raspberry Pi OS Bookworm), retirando
  `fake-hwclock`. Tras reiniciar, el driver toma la dirección 0x68 —
  `sudo i2cdetect -y 1` la muestra como `UU` — y la hora se sincroniza
  con `hwclock`. Los scripts de `raspberry/` no leen el DS3231
  directamente: sus marcas de tiempo provienen del reloj del sistema,
  que el RTC mantiene sin red. Equivale al rol del DS3231 en el ESP32
  (marca de tiempo de cada ventana).
- **I²S en Raspberry Pi** requiere habilitar el overlay de device tree
  correspondiente al micrófono I²S (`dtoverlay` en `/boot/config.txt`)
  y no está disponible por defecto como en el ESP32 (donde el
  periférico I²S se configura directamente en el firmware) — detalle
  de configuración a documentar junto con el código Python (sección 5).
- **Alimentación de los módulos TCRT5000: 3.3 V** (pin 1 o 17), no 5 V: la salida D0
  subiría a 5 V y los GPIO de Raspberry Pi tampoco lo toleran; alimentar a 3.3 V; validar la sensibilidad en banco.
- **GPIO5/6/12/13** para el sensor de tráfico de forrajeo se eligieron
  por ser pines de propósito general sin función reservada, libres de
  conflicto con I²C (2/3), I²S (18/19/20), UART (14/15) y SPI (7-11).
- El pin GPIO4, usado tanto en ESP32 como en Raspberry Pi para el
  sensor básico, coincide con el pin que Raspberry Pi OS reserva por
  defecto para el overlay 1-Wire estándar (`w1-gpio`) — **no aplica
  aquí**, ya que el protocolo del sensor básico es propietario de un
  hilo, no 1-Wire Dallas estándar, y no debe habilitarse ese overlay
  para este uso; verificar que ningún otro periférico active el
  overlay 1-Wire en `/boot/config.txt` antes de cablear.

---

## 5. Código Python — estado y referencia cruzada

Cada carpeta `software/sensor-*/` sigue la misma estructura dual: un
`README.md` y una imagen conceptual a nivel de sensor (independientes
de plataforma), y dos subcarpetas — `arduino/` y `raspberry/` — con el
código y el diagrama de conexión específicos de cada plataforma. El
código de adquisición vigente, completo y validado para los cinco
sensores es el de la **ruta A (Arduino/ESP32)**, en la subcarpeta
`arduino/` de cada carpeta:

| Carpeta | Sensor | `arduino/` (código Arduino/ESP32) | `raspberry/` (código Python) |
|---|---|---|---|
| `software/sensor-vibracion/` | Vibración estructural | ✅ `mpu6500_polling/mpu6500_polling.ino`, `mpu6500_interrupt_fifo/mpu6500_interrupt_fifo.ino`, `diagrama_conexion.svg` | ✅ `lectura_mpu6500.py` (Ruta A únicamente, MPU6500 en 0x69), `diagrama_conexion.svg` (incluye DS3231 en 0x68) — ver sección 3.1 sobre el riesgo de jitter pendiente de validar en banco |
| `software/sensor-audio/` | Sonido aéreo | ✅ `inmp441_i2s_capture/inmp441_i2s_capture.ino`, `diagrama_conexion.svg` | ✅ `captura_inmp441.py`, `diagrama_conexion.svg` — I²S por hardware/DMA, sin el riesgo de jitter de los sensores anteriores (ver el docstring de `captura_inmp441.py`); validación de equivalencia con ESP32 pendiente (README del sensor, sección 5) |
| `software/sensor-trafico/` | Tráfico de forrajeo | ✅ `ir_doble_haz_conteo/ir_doble_haz_conteo.ino`, `diagrama_conexion.svg` | ✅ `conteo_trafico.py`, `diagrama_conexion.svg` — detección por eventos GPIO, riesgo de orden A/B en el conteo direccional pendiente de validar (sección 3.3) |
| `software/sensor-temperatura-humedad-basico/` | Temp/HR básico | ✅ `dht22_lectura/dht22_lectura.ino`, `diagrama_conexion.svg` | ✅ `lectura_dht22.py` (vía `pigpio`), `diagrama_conexion.svg` — ver sección 3.2 sobre el riesgo de confiabilidad confirmado, con mitigación parcial, pendiente de validar en banco |
| `software/sensor-temperatura-humedad-precision/` | Temp/HR precisión | ✅ `sht31_lectura/sht31_lectura.ino`, `diagrama_conexion.svg` | ✅ `lectura_sht31.py` (I²C vía `smbus2`), `diagrama_conexion.svg` — bus compartido con el sensor de vibración y el DS3231, throughput analizado (ver el docstring de `lectura_sht31.py`); latencia puntual pendiente de confirmar en banco (sección 3.2 de este documento) |

**Este documento no incluye código Python.** Es exclusivamente de
arquitectura y mapeo de pines; el código en sí vive en cada carpeta de
sensor (columna anterior). Los cinco sensores ya cuentan con código
Python equivalente en su subcarpeta `raspberry/`; lo pendiente en todos
los casos (secciones 3.1–3.3) es la **validación de banco** de los
riesgos de temporización específicos de cada uno bajo Linux, no la
implementación del código en sí.

---

## 6. Rieles de alimentación

Todos los GPIO del ESP32 DevKit V1 y de la Raspberry Pi trabajan a 3.3 V y
no toleran 5 V. Por eso todo componente cuya salida o cuyos pull-ups llegan
a un GPIO o al bus I²C se alimenta a **3.3 V**; solo la microSD HW-125 usa
5 V, porque su regulador interno la baja a 3.3 V.

| Componente | Riel | ESP32 DevKit V1 | Raspberry Pi | Nota |
|---|---|---|---|---|
| MPU6500 (GY-6500) | 3.3 V | 3V3 | 3V3 (pin 1/17) | Trae pull-ups I²C y regulador propio — **verificar en el módulo recibido** |
| SHT31 (breakout) | 3.3 V | 3V3 | 3V3 | Trae pull-ups I²C — **verificar en el módulo recibido** |
| DS3231 (ZS-042) | 3.3 V | 3V3 | 3V3 | Trae pull-ups I²C y circuito de carga de la pila — **verificar en el módulo recibido** |
| INMP441 | 3.3 V | 3V3 | 3V3 | — |
| DHT22 | 3.3 V | 3V3 | 3V3 | Pull-up de DATA a 3.3 V; verificar en la hoja de datos el alcance de cable con 3.3 V |
| Módulos TCRT5000 (×4) | 3.3 V | 3V3 | 3V3 | Salida D0 a 3.3 V; validar la sensibilidad en banco |
| microSD pequeña de 3.3 V (sin regulador) | 3.3 V | 3V3 | No aplica | — |
| microSD HW-125 | 5 V (VIN) | VIN | No aplica | Regulador AMS1117 y buffer de nivel en el módulo; líneas SPI a 3.3 V — **verificar en el módulo recibido** |

> **Advertencia — bus I²C:** los módulos que traen pull-ups (ZS-042 del
> DS3231, GY-6500, breakout del SHT31) **no deben alimentarse a 5 V**: sus
> pull-ups subirían SDA y SCL a 5 V y pondrían 5 V en el bus I²C del ESP32 o
> de la Raspberry Pi. El valor de esos pull-ups y si van a VCC del módulo o a
> la salida de su regulador dependen del fabricante — **verificar en el
> módulo recibido**.

---

## Referencias

- `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, sección 2.2 (Tabla
  2.2, arquitectura sensorial heterogénea) y sección 2.3.1 (Tabla 2.3,
  protocolos y pines ESP32).
- `CLAUDE.md`, tabla de stack de sensores confirmado y sección
  "Decisiones de diseño confirmadas".
- `software/sensor-vibracion/README.md`, secciones 2.1–2.2 (criterio
  `FS_VIB` = 1500 Hz y capacidad de 4 kHz del MPU6500) y sección 5
  (metodología de validación en banco).
- Raspberry Pi Foundation. *Raspberry Pi 4 Model B* y *Raspberry Pi
  Zero 2 W* — especificaciones oficiales (SoC, RAM, GPIO).

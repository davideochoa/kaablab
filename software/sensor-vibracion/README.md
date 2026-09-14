# MPU6050 / MPU6500 — Muestreo de vibración estructural (300–600 Hz)

Sensor de vibración estructural del sistema KaabLab. Vía este acelerómetro
se busca capturar señales vibracionales relacionadas con comportamiento
defensivo en *Melipona beecheii*, en la banda **300–600 Hz** reportada por
Hrncir et al. (2006) para señalización vibracional en meliponinos (título
completo pendiente de completar en `thesis/referencias.md`).

Documento dirigido a nivel licenciatura en mecatrónica: se explican tanto
los conceptos (Nyquist, DLPF, FIFO) como la configuración concreta.

> Sensor a instalar en contacto directo con la madera de la colmena (ver
> `CLAUDE.md`, sección "Decisiones de diseño confirmadas").

## Contenido de esta carpeta

| Archivo | Contenido |
|---|---|
| `README.md` | Este documento |
| `mpu6050_polling.ino` | Ruta A: polling con librería, tasa alta de muestreo |
| `mpu6050_interrupt_fifo.ino` | Ruta B (opcional): interrupción INT + FIFO interno |
| `diagrama_conexion.svg` | Esquema de conexión ESP32 DevKit V1 ↔ MPU6050/MPU6500 |
| `concepto_vibracion.svg` | Diagrama conceptual: qué es la vibración estructural medida y su rango de frecuencia objetivo |

---

## 0. ¿Qué mide este sensor y en qué rango?

![Concepto: vibración estructural medida por el MPU6050](./concepto_vibracion.svg)

El MPU6050 es un **acelerómetro MEMS**: mide aceleración lineal en sus
tres ejes, no sonido. En este proyecto, montado **en contacto directo con
la madera de la colmena**, esa aceleración captura la **vibración
estructural** — el movimiento mecánico de la pared del nido cuando las
abejas la excitan directamente golpeándola o presionándola con el cuerpo,
a diferencia del sonido aéreo (variación de presión que viaja por el
aire, captado por el INMP441 — ver `../sensor-audio/README.md`). Es la
vía por la que *M. beecheii*, como el resto de los meliponinos, expresa
señalización relacionada con el forrajeo y ciertos comportamientos
sociales mediante vibración del sustrato (dos Santos et al., 2025).

**Rango de frecuencia objetivo: 300–600 Hz**, banda reportada por Hrncir
et al. (2006) para señalización vibracional en meliponinos asociada al
forrajeo/comunicación (título completo pendiente en
`thesis/referencias.md`). Como ya se documenta en la sección 2.2, el ADC
del acelerómetro del MPU6050 tiene una limitación de hardware que deja el
**Nyquist real en ~500 Hz** — al límite del extremo superior de esta
banda, sin margen —, por lo que la cobertura completa de 600 Hz debe
confirmarse empíricamente en banco (sección 5).

---

## 1. Contexto del problema

La configuración por defecto de la mayoría de librerías Arduino para el
MPU6050 deja el sensor en:

- **Sample Rate ≈ 100 Hz** (registro `SMPLRT_DIV` con divisor por defecto)
- **DLPF activo** (filtro digital pasa-bajas interno habilitado, `DLPF_CFG` entre 1 y 6)

Por el **teorema de Nyquist**, una señal solo puede reconstruirse sin
ambigüedad (aliasing) si se muestrea a más del doble de la frecuencia
máxima de interés:

```
f_muestreo > 2 × f_señal_max
```

Con Sample Rate = 100 Hz, la frecuencia máxima representable sin aliasing
es 50 Hz (Nyquist = 100/2). La banda objetivo reportada por Hrncir et al.
(2006) es **300–600 Hz** — muy por encima de esos 50 Hz. Con la
configuración por defecto, cualquier vibración en esa banda aparecería
como ruido de baja frecuencia (aliasing), no como la señal real.

**Conclusión:** la configuración por defecto es inutilizable para este
propósito. Es necesario reconfigurar el sample rate y el DLPF antes de
cualquier captura de banco.

---

## 2. Configuración objetivo

### 2.1 Cálculo de SMPLRT_DIV y DLPF_CFG

El MPU6050 genera su "Sample Rate" (la tasa a la que se actualizan los
registros de salida, el FIFO y las interrupciones data-ready) según:

```
Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
```

donde `Gyroscope Output Rate` depende del DLPF (Registro 26, `DLPF_CFG`):

- `DLPF_CFG = 0` o `7` (DLPF deshabilitado): reloj base = **8 kHz**
- `DLPF_CFG = 1..6` (DLPF habilitado): reloj base = 1 kHz

Objetivo del proyecto: Sample Rate ≥ 2 kHz **y** Nyquist ≥ 1200 Hz (margen
sobre el límite superior de la banda, 600 Hz). Esto exige Sample Rate ≥ 2400 Hz,
no solo ≥ 2000 Hz:

| DLPF_CFG | SMPLRT_DIV | Sample Rate | Nyquist | ¿Cumple ≥1200 Hz? |
|---|---|---|---|---|
| 0 (deshabilitado) | 3 | 8000/4 = 2000 Hz | 1000 Hz | ❌ insuficiente |
| **0 (deshabilitado)** | **2** | **8000/3 ≈ 2667 Hz** | **≈1333 Hz** | ✅ |

**Configuración recomendada: `DLPF_CFG = 0`, `SMPLRT_DIV = 2`** →
Sample Rate ≈ 2667 Hz, Nyquist ≈ 1333 Hz, con margen cómodo sobre los
600 Hz superiores de la banda objetivo.

### 2.2 Limitación crítica: el acelerómetro del MPU6050 muestrea internamente a 1 kHz fijo

Este es el punto más fácil de pasar por alto y **debe verificarse en banco**
(ver sección 5):

> Según el Register Map oficial del MPU-6000/6050 (Registro 25,
> `SMPLRT_DIV`): *"The accelerometer output rate is 1kHz. This means that
> for a Sample Rate greater than 1kHz, the same accelerometer sample may
> be output to the FIFO, DMP, and sensor registers more than once."*

En otras palabras: el ADC del acelerómetro del **MPU6050** actualiza su
valor internamente cada 1 ms sin importar cómo se configure `SMPLRT_DIV`.
Si se lee el registro de aceleración a 2667 Hz, aproximadamente 1 de cada
~2.67 lecturas será un valor genuinamente nuevo; el resto serán
repeticiones del mismo dato. El Nyquist *real* del canal de aceleración
queda limitado a ~500 Hz — **al límite, no con margen, del extremo
superior de la banda de 600 Hz**.

Esto no es un error de configuración: es una limitación de hardware del
ADC del acelerómetro documentada por el fabricante. Implicaciones:

- La configuración de la sección 2.1 sigue siendo la correcta y necesaria
  (da margen completo para el **giroscopio**, cuyo ADC sí sigue el reloj
  de 8 kHz, y evita que el firmware sea el cuello de botella).
- Para el **acelerómetro**, la cobertura de la banda 300–600 Hz debe
  confirmarse empíricamente en banco (sección 5): si la energía relevante
  de la señal reportada por Hrncir et al. (2006) se concentra en la mitad
  baja de la banda (300–500 Hz), la limitación es aceptable; si hay
  energía significativa cerca de 600 Hz, existirá aliasing parcial.
- Si el módulo físico instalado resulta ser un **MPU6500** (algunas
  placas "GY-521" genéricas montan el die MPU6500 en vez del MPU6050),
  el registro `ACCEL_CONFIG2` (0x1D) de ese chip permite deshabilitar el
  DLPF del acelerómetro de forma independiente del giroscopio, alcanzando
  una tasa de actualización interna del acelerómetro más alta. **Verificar
  el datasheet exacto del chip montado en la placa física antes de asumir
  esta ruta** — no se documenta código para esto aquí porque depende del
  chip real, no de la librería.

**Acción requerida:** dejar constancia de esta limitación en el capítulo
de metodología/resultados de la tesis si la validación de banco (sección 5)
confirma pérdida de resolución cerca de 600 Hz.

### 2.3 El bus I²C no es el cuello de botella

Límite físico del bus I²C del MPU6050: **400 kHz (Fast Mode)** — no es
configurable más allá de eso (el chip no soporta Fast Mode Plus ni High-Speed).

Cálculo de throughput para una lectura típica de 6 bytes (aceleración
X/Y/Z, 2 bytes cada eje) vía "escribir puntero de registro + repeated
start + leer N bytes":

```
Bits por transacción ≈ dirección+W (9) + registro (9) + repeated start +
                        dirección+R (9) + 6 bytes de datos (6×9=54)
                      ≈ 81 bits

Límite teórico del bus a 400 kHz:
  400 000 bits/s ÷ 81 bits ≈ 4938 transacciones/s
```

Ese es el límite *teórico* ignorando condiciones START/STOP y tiempo de
bus libre (`t_BUF`). En la práctica, con el overhead real del protocolo
I²C y de la librería `Wire` sobre ESP32, un estimado conservador realista
es de **~3000–4000 lecturas/s**.

**En cualquiera de los dos casos (teórico ~4900/s, conservador
~3000–4000/s), el bus I²C tiene margen sobrado sobre las ~2667 lecturas/s
requeridas por la configuración objetivo de la sección 2.1.**

> **Nota explícita:** el bus I²C *no* es el riesgo. El riesgo real está en
> la eficiencia del firmware — específicamente, en **polling bloqueante**
> con `delay()`, que puede introducir jitter, perder ventanas de muestreo,
> o bloquear otras tareas del ESP32 (WiFi, otros sensores) mientras se
> espera. Por eso el código de la Ruta A (sección 3) evita `delay()` y usa
> temporización no bloqueante basada en `micros()`.

### 2.4 Nota sobre GPIO14

`CLAUDE.md` documenta un conflicto pendiente de resolver en GPIO14
(asignado simultáneamente a SCK de I²S para el INMP441 y a SDA de I²C).
Ese conflicto **no afecta a este sensor**: el MPU6050 en este proyecto usa
el bus I²C por defecto del ESP32 (SDA=GPIO21, SCL=GPIO22), no GPIO14. Se
deja la nota aquí solo para que quede claro que ambos temas son
independientes.

---

## 3. Código de manejo del sensor (ESP32)

Pin mapping confirmado del proyecto: **SDA = GPIO21, SCL = GPIO22**.

### 3.1 Ruta A — Polling con librería (recomendada para primera prueba)

Ver [`mpu6050_polling.ino`](./mpu6050_polling.ino).

Usa la librería **I2Cdevlib** (`MPU6050.h`, de Jeff Rowberg —
https://github.com/jrowberg/i2cdevlib), porque expone `setRate()` y
`setDLPFMode()` como métodos nombrados que mapean directamente a
`SMPLRT_DIV` y `DLPF_CFG` sin necesidad de escribir registros a mano byte
por byte. (`Adafruit_MPU6050` y `MPU6050_light` son alternativas válidas,
pero su API de alto nivel no siempre expone el divisor de sample rate de
forma tan directa; si se usa una de ellas, confirmar en su documentación
cómo fijar `SMPLRT_DIV`.)

Puntos clave del código:

- Configura `DLPF_CFG=0` y `SMPLRT_DIV=2` (sección 2.1).
- `Wire.setClock(400000)` para operar en I²C Fast Mode.
- El bucle principal usa temporización no bloqueante con `micros()` — **no
  usa `delay()`** — para respetar la nota de la sección 2.3.
- Imprime timestamp + valores crudos de aceleración por puerto serie en
  formato CSV, listo para capturar con un terminal serie o script y
  analizar (p. ej. FFT) en banco.

### 3.2 Ruta B — Interrupción + FIFO (opcional, solo si Ruta A pierde muestras)

Ver [`mpu6050_interrupt_fifo.ino`](./mpu6050_interrupt_fifo.ino).

Solo implementar esta ruta si la prueba de banco de la Ruta A (sección 5)
muestra pérdida de muestras. Usa el pin `INT` (data-ready) del MPU6050 y
el FIFO interno del sensor para que el ESP32 no tenga que hacer polling
continuo: el sensor avisa por interrupción cuando hay una muestra nueva,
y los datos se acumulan en su FIFO interno hasta que el ESP32 los retira
en bloque. Esto evita que el `delay()`/polling bloqueante consuma ciclos
del procesador.

El pin `INT` sugerido en el código (GPIO4) **no está confirmado contra el
mapeo global de pines del proyecto** (`firmware/esp32_main`) — verificar
que no choque con otro sensor antes de cablear.

---

## 4. Esquema de conexión

Ver [`diagrama_conexion.svg`](./diagrama_conexion.svg).

Incluye: VCC (3.3V), GND, SDA (GPIO21), SCL (GPIO22), y el pin INT
(marcado como opcional, solo necesario para la Ruta B).

---

## 5. Validación requerida antes de instalación en campo

**No dar por resuelta la Ruta A únicamente por inspección de código.**
Antes de instalar el sensor en una colmena, se requiere una prueba de
banco que confirme, con instrumentación externa (osciloscopio o
analizador lógico en el bus I²C, o un generador de vibración calibrado
sobre el que se monte el sensor):

1. **Que no hay pérdida de muestras** a la tasa configurada (~2667 Hz) —
   comparar el número de transacciones I²C observadas en el analizador
   lógico contra las esperadas por segundo.
2. **Que la tasa de muestreo real y consistente** coincide con la
   configurada (verificar jitter entre muestras consecutivas del bucle
   `micros()`).
3. **Que el canal de aceleración captura información nueva y no
   duplicada** en cada lectura, dada la limitación de la sección 2.2 —
   por ejemplo, aplicando una vibración conocida y verificando que la FFT
   de las muestras leídas no muestre un "escalón" de valores repetidos.
4. Si se detecta pérdida de muestras con la Ruta A, implementar y probar
   la Ruta B (interrupción + FIFO) antes de continuar.

Solo después de esta validación de banco se debe considerar la
configuración lista para cableado final en campo.

---

## Referencias

- Hrncir, M., Jarau, S., Zucchi, R., & Barth, F. G. (2006). [Título
  completo pendiente — comunicación y señalización vibracional en
  Melipona]. Ver `thesis/referencias.md`.
- InvenSense. *MPU-6000 and MPU-6050 Register Map and Descriptions*
  (RM-MPU-6000A-00), Registro 25 (`SMPLRT_DIV`) y Registro 26 (`CONFIG` /
  `DLPF_CFG`).

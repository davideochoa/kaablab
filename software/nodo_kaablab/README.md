# Nodo KaabLab — Firmware integrado ESP32

Firmware del **nodo de campo** del sistema KaabLab. A diferencia de los
README de `../sensor-*/`, que documentan **cada sensor por separado**
(un sketch por sensor en `arduino/<sketch>/<sketch>.ino`, pensado para
pruebas de banco aisladas), este
directorio integra los **5 sensores en un solo firmware** para operar la
colmena de forma autónoma:

- Captura periódica de audio, vibración, temperatura/humedad y tráfico de
  piquera, con marca de tiempo del RTC.
- Almacenamiento local en **microSD** (sin depender de red durante la
  captura).
- **Servidor HTTP local** (ESP32 como punto de acceso WiFi) para que la
  app Android descargue y, tras confirmar, borre los ciclos guardados.
- Ciclo de energía: 5 min activo (captura + servidor) y 55 min en deep sleep.

El procesamiento (características, clasificación) **no** ocurre en el nodo:
el ESP32 solo adquiere y almacena datos crudos; el análisis se hace fuera
del nodo (celular / pipeline en `../kaablab_pipeline/`).

## Contenido de esta carpeta

| Archivo | Contenido |
|---|---|
| `nodo_kaablab.ino` | Ciclo principal: init → captura periódica + servidor → deep sleep |
| `config.h` | Pines, direcciones I²C, parámetros de captura, identidad del nodo, puerto HTTP |
| `sensores.h` / `sensores.cpp` | Inicialización y lectura de SHT31, DHT22, MPU6500, INMP441, contadores IR y DS3231 |
| `captura.h` / `captura.cpp` | Montaje de la microSD, carpetas de ciclo y escritura de cada ventana |
| `servidor_http.h` / `servidor_http.cpp` | Punto de acceso WiFi y API HTTP de descarga/borrado |

## Sensores y periféricos integrados

| Periférico | Bus / pines (ESP32 DevKit V1) | Rol |
|---|---|---|
| SHT31 (0x44) | I²C — SDA = GPIO21, SCL = GPIO22 | Temperatura y humedad interna |
| MPU6500 / GY-6500 (**0x69**) | I²C — SDA = GPIO21, SCL = GPIO22; INT = GPIO13 (opcional, sin uso en este firmware) | Vibración estructural |
| DS3231 (0x68) | I²C — SDA = GPIO21, SCL = GPIO22 | Reloj de tiempo real (marca de tiempo) |
| DHT22 | Protocolo propio de un hilo — DATA = GPIO4 | Temperatura y humedad exterior |
| INMP441 | I²S — SCK = GPIO14, WS = GPIO15, SD = GPIO32 | Nivel acústico |
| IR doble haz (4 módulos TCRT5000 reflectivos) | Haz A: GPIO26 (principal) + GPIO25 (secundario); Haz B: GPIO27 (principal) + GPIO33 (secundario) | Conteo de tráfico en piquera |
| microSD (SPI, VSPI) | CS = GPIO5, MOSI = GPIO23, MISO = GPIO19, SCK = GPIO18 | Almacenamiento local |

Los pines de los sensores, del DS3231 y de la microSD coinciden con
`thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, Tabla 2.3.

**MPU6500 en 0x69:** el pin `AD0` del MPU6500 debe conectarse a 3.3 V. Con
`AD0` a GND el sensor responde en 0x68, la misma dirección que el DS3231,
y ambos chocarían en el bus I²C compartido.

## Librerías Arduino necesarias

Instalar desde el Gestor de Librerías del Arduino IDE (o `arduino-cli lib install`):

| Librería | Autor | Uso en el firmware |
|---|---|---|
| **DHT sensor library** | Adafruit | DHT22 (`DHT.h`) |
| **Adafruit SHT31 Library** | Adafruit | SHT31 (`Adafruit_SHT31.h`) |
| **MPU9250_WE** | Wolfgang Ewald | MPU6500 (`MPU6500_WE.h`, clase `MPU6500_WE`) |
| **RTClib** | Adafruit | DS3231 (`RTClib.h`) |
| **ArduinoJson** | Benoît Blanchon | Metadatos `meta_NN.json` y respuestas de la API (el código usa `StaticJsonDocument`) |

Dependencias que el Gestor de Librerías instala junto con las anteriores:
**Adafruit Unified Sensor** y **Adafruit BusIO**. `sensores.cpp` incluye
`Adafruit_Sensor.h` de forma explícita (tipo `sensors_event_t`).

`MPU9250_WE` se instala con ese nombre, pero el firmware usa su clase
`MPU6500_WE` (espera `WHO_AM_I` = 0x70), no `MPU9250_WE` (espera 0x71 y un
magnetómetro que el MPU6500 no tiene).

Incluidas en el **core Arduino-ESP32** (no requieren instalación aparte):
`SD`, `SPI`, `Wire`, `WiFi`, `WebServer` y `driver/i2s.h` (driver I²S clásico).

Placa en el Arduino IDE: **ESP32 Dev Module** (ESP32 DevKit V1).

> Este firmware y los sketches de `../sensor-vibracion/arduino/` usan `MPU6500_WE`
> (librería MPU9250_WE): `imu.init()` con dirección explícita 0x69,
> verificando `whoAmI() == 0x70`, y leen la aceleración con
> `imu.getGValues()` (en g, convertida a mg en el buffer).

## Componentes pasivos del nodo

Pasivos comunes del nodo (los de cada sensor están en la sección 4.1 del README de cada
`../sensor-*/`). Todos los diagramas `../sensor-*/arduino/diagrama_conexion.svg` y
`../sensor-*/raspberry/diagrama_conexion.svg` incluyen un panel con estos componentes.

| Componente | Valor | Cant. | Dónde va | ¿Lo trae el módulo? | Estado del valor |
|---|---|---|---|---|---|
| Condensador electrolítico (ESP32) | 100 µF | 1 | Entre 3V3 y GND, junto a la placa | No | **Pendiente de verificar** (valor de diseño, no de hoja de datos) |
| Condensador cerámico (ESP32) | 100 nF | 1 | Entre 3V3 y GND, en paralelo con el de 100 µF | No | **Pendiente de verificar** (valor de diseño) |
| Diodo 1N4007 (ESP32) | 1 A / 1000 V, caída ≈ 1.1 V a 1 A | 1 | En serie **solo** en la entrada externa de 6.5–16 V hacia VIN; nunca en el riel de 5 V/USB | No | Hoja 1N4007 (caída). **Pendiente de verificar** el tope de entrada del regulador de la placa (AMS1117: máximo no confirmado; algunas fuentes dan 15 V) |
| Condensador electrolítico (microSD HW-125) | 100 µF | 1 | Entre VIN y GND del módulo | No | **Pendiente de verificar** (valor de diseño) |
| Condensador cerámico (microSD HW-125) | 100 nF | 1 | Entre VIN y GND del módulo | No | **Pendiente de verificar** (valor de diseño) |
| Variante microSD 3.3 V sin regulador | 100 µF + 100 nF | 1 + 1 | Entre 3V3 y GND del módulo | No | **Pendiente de verificar** (valor de diseño) |
| Regulador y buffer de nivel (HW-125) | AMS1117-3.3 / 74LVC125 (según lote) | — | En el módulo | Sí — **verificar en el módulo recibido** | Vendedores; no hay esquema oficial |
| Pull-ups I²C | 4.7 kΩ o 5.1 kΩ | 0 (2 solo si hace falta) | SDA y SCL a 3.3 V, solo si ningún módulo del bus los trae | Normalmente sí — **verificar en el módulo recibido** | Criterio de diseño |
| DS3231: circuito de carga de la pila | ≈ 200 Ω + diodo (ZS-042) | — | VCC → VBAT del módulo RTC | Sí — **verificar en el módulo recibido** | Foros, no hoja de datos. Usar LIR2032, o con CR2032 retirar el diodo o la resistencia de carga |

## Configuración por nodo (`config.h`)

| Macro | Valor actual | Nota |
|---|---|---|
| `NODO_ID` | `"nodo1"` | Cambiar a `nodo2`/`nodo3` al flashear cada nodo |
| `WIFI_SSID` | `"KaabLab-Nodo1"` | Ídem; red abierta (`WIFI_OPEN true`), sin contraseña, decisión de diseño de esta fase |
| `FS_AUDIO` / `DUR_AUDIO_S` | 16000 Hz / 1 s | Igual que `FS_AUDIO`/`DUR_AUDIO` de `../kaablab_pipeline/config.py` |
| `FS_VIB` / `DUR_VIB_S` | 1500 Hz / 2 s | Igual que `FS_VIB`/`DUR_VIB` del pipeline; elección de diseño dentro de la capacidad del MPU6500 (salida programable hasta 4000 Hz con el DLPF desactivado). Nyquist = 750 Hz, cubre la banda de forrajeo 300–600 Hz con margen de diseño 1.25× sobre el límite superior (`N_MUESTRAS_VIB` = 3000). **Pendiente de validar en banco**: revisar la ADVERTENCIA por Serial de `sensores_capturar_vibracion()` (ver `../sensor-vibracion/README.md`, sección 2.2) |
| `VENTANAS_POR_CICLO` | 10 | Capturas por despertar |
| `INTERVALO_VENTANA_MS` | 30 000 | 30 s entre ventanas |
| `TIEMPO_ACTIVO_MS` / `TIEMPO_DORMIDO_US` | 5 min / 55 min | Ciclo de energía |
| `HTTP_PORT` | 80 | Puerto del servidor |

## Datos almacenados en la microSD

Cada despertar crea una carpeta `/ciclo_NNNNN` (contador persistido en
`/contador_ciclo.txt`). Cada ventana `NN` (00–09) escribe:

| Archivo | Formato |
|---|---|
| `audio_NN.pcm` | `int16` mono, 16 kHz, 16 000 muestras (1 s) |
| `vib_NN.raw` | `int16` en mg, intercalado x,y,z, 1500 Hz, 3000 muestras × 3 ejes (2 s, ≈ 18 KB) |
| `meta_NN.json` | `ts` (Unix, DS3231), nombres de archivo, `dht_T`, `dht_RH`, `sht_T`, `sht_RH`, `trafico_entradas`, `trafico_salidas` |

## API HTTP (celular conectado al AP del nodo)

| Método y ruta | Respuesta |
|---|---|
| `GET /ciclos` | JSON con las carpetas `ciclo_*` en la SD |
| `GET /ciclos/{ciclo}` | JSON con los `meta_*.json` de ese ciclo |
| `GET /ciclos/{ciclo}/{archivo}` | Archivo crudo (`.json`, `.pcm`, `.raw`) |
| `DELETE /ciclos/{ciclo}` | Borra la carpeta completa del ciclo |

El servidor solo está activo durante la ventana de 5 min; al terminar, el
nodo apaga el WiFi y entra en deep sleep.

## Flujo de un despertar

```
despertar → microSD → sensores (SHT31, MPU6500, DS3231, I²S, IR) → AP WiFi + HTTP
          → crear /ciclo_NNNNN
          → 5 min: atender HTTP + capturar ventana cada 30 s (máx. 10)
          → apagar WiFi → deep sleep 55 min
```

Si la microSD o algún sensor I²C no se detecta, el nodo omite el ciclo y
entra directamente a deep sleep.

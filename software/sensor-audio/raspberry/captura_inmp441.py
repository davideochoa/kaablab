#!/usr/bin/env python3
"""
INMP441 — Captura de audio vía I²S (Raspberry Pi 4 Model B, 2GB)
KaabLab — nivel acústico / vitalidad de la colonia (Melipona beecheii)

Equivalente Python de ../arduino/inmp441_i2s_capture/inmp441_i2s_capture.ino. Replica la
MISMA configuración ya validada en la versión ESP32 (ver README.md,
secciones 2 y 3, antes de modificar este script):

    Sample rate = 16,000 Hz (Nyquist = 8,000 Hz, cubre la banda de
                  alarma/intrusos documentada hasta 8,000 Hz — README
                  sección 2.1)
    Canal mono  = L/R a GND, selecciona el canal izquierdo (README
                  sección 2.4)
    Formato     = 24 bits válidos alineados a la izquierda en una trama
                  I²S de 32 bits, protocolo I²S estándar (no PDM) —
                  README sección 2.3

---------------------------------------------------------------------
VENTAJA DE ESTA PLATAFORMA PARA ESTE SENSOR ESPECÍFICO
---------------------------------------------------------------------
Contraste explícito con ../../sensor-vibracion/raspberry/lectura_mpu6500.py
y ../../sensor-temperatura-humedad-basico/raspberry/ (ver
docs/arquitectura-hardware/README.md, secciones 3.1 y 3.2):

El MPU6500 se lee por software vía I²C (el CPU dispara cada transacción
uno por uno) y el sensor básico de temperatura/humedad usa un protocolo
de un solo cable con timing de microsegundos hecho también por
software — ambos casos dependen de que el planificador de Linux le dé
al proceso de Python su turno de CPU en el instante exacto en que hace
falta, lo cual Linux (no tiempo real) no garantiza.

**El I²S en Raspberry Pi 4 es distinto: usa un periférico de HARDWARE
dedicado (el bloque PCM/I2S del SoC BCM2711) con transferencia por DMA
gestionada enteramente por el driver ALSA/kernel.** Este proceso de
Python en espacio de usuario nunca "bit-banguea" la señal ni mide
anchos de pulso: solo copia bloques ya ensamblados desde un buffer que
el hardware llena de forma autónoma, con la temporización generada por
el propio reloj de bit (BCLK) del periférico I²S — el mismo principio,
a nivel de concepto, que ya usa el ESP32 (periférico I²S + DMA interno,
ver `../arduino/inmp441_i2s_capture/inmp441_i2s_capture.ino` y README.md sección 2.2).

**Por eso el riesgo de jitter documentado para el sensor de vibración y
el sensor básico de temperatura/humedad NO aplica de la misma forma
aquí.** Esta es una ventaja específica de ESTE sensor en Raspberry Pi —
no debe asumirse que se extiende al resto de la arquitectura. La
integridad de la señal de audio depende del hardware I²S y del driver
ALSA, no de que el intérprete de Python logre temporización de
microsegundos en espacio de usuario. Aun así, la sección 5 del README
exige validar en banco que no hay diferencias de calidad de señal
frente al ESP32 (xruns del driver, saturación, resolución efectiva) —
la ventaja arquitectónica no exime de esa validación.
---------------------------------------------------------------------

Configuración de hardware previa requerida (Raspberry Pi OS):
  1. Habilitar el bus I²S: agregar `dtparam=i2s=on` en
     `/boot/config.txt` (o `/boot/firmware/config.txt` en imágenes
     recientes de Raspberry Pi OS basadas en Bookworm).
  2. Cargar un overlay de tarjeta de sonido I²S para micrófono genérico
     (solo captura, sin códec real) — el overlay exacto depende de la
     versión de kernel/imagen usada (p. ej. variantes de
     `simple-audio-card` con códec "dummy", o `googlevoicehat-soundcard`
     en algunas distribuciones). **Pendiente de fijar el overlay
     definitivo en la validación de banco (README.md, sección 5)** —
     no se asume aquí un nombre único de overlay porque varía entre
     imágenes de Raspberry Pi OS.
  3. Verificar con `arecord -l` que aparece una tarjeta de captura
     (p. ej. "card 1: ... device 0: ...") antes de ejecutar este script.
  4. Si el micrófono I²S no queda como dispositivo de captura por
     defecto, seleccionarlo explícitamente con la variable de entorno
     `INMP441_DEVICE` (nombre o índice — ver `sounddevice.query_devices()`).

Librería: sounddevice (pip install sounddevice; requiere PortAudio:
`sudo apt install libportaudio2`)
  Se eligió sounddevice sobre pyalsaaudio porque expone la captura
  directamente como arreglos NumPy — el mismo formato que usará el
  resto del pipeline de extracción de características del proyecto
  (MFCCs, ZCR, centroide espectral; ver
  `thesis/capitulo-2-materiales-y-metodos/capitulo-2.md`, sección 2.7) — sin
  necesidad de empaquetar/desempaquetar bytes a mano como con
  pyalsaaudio directamente.

Pin mapping (Raspberry Pi 4 Model B, ver
docs/arquitectura-hardware/README.md, sección 4 — mapeo GPIO BCM
equivalente al de ESP32 DevKit V1):
  BCLK (SCK)  = GPIO18 (pin físico 12)
  LRCLK (WS)  = GPIO19 (pin físico 35)
  DIN   (SD)  = GPIO20 (pin físico 38)
  L/R -> GND  (canal mono, igual que en la versión ESP32, README sección 2.4)
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sys.exit(
        "ERROR: falta la libreria sounddevice. Instalar con: pip install sounddevice\n"
        "       (requiere PortAudio: sudo apt install libportaudio2)"
    )

# --- Configuracion objetivo (identica a arduino/inmp441_i2s_capture/inmp441_i2s_capture.ino, README seccion 2.1) ---
SAMPLE_RATE_HZ = 16_000
CHANNELS = 1                    # mono: L/R a GND (README seccion 2.4)
SAMPLE_DTYPE = "int32"          # trama I2S de 32 bits (README seccion 2.3)
BIT_SHIFT = 8                   # extraer los 24 bits validos -- ver nota de validacion abajo
BLOCK_SIZE = 256                # muestras por bloque, analogo a DMA_BUF_LEN del firmware ESP32

# Nota de validacion (identica a la del firmware ESP32, ver README.md
# seccion 3 y arduino/inmp441_i2s_capture/inmp441_i2s_capture.ino): el corrimiento >>8 asume
# alineacion a la izquierda estandar de 24 bits en una trama de 32. Si
# el driver ALSA/overlay usado en Raspberry Pi introduce una alineacion
# distinta (analoga al corrimiento de bit conocido en algunas versiones
# del periferico I2S del ESP32), este valor debe confirmarse en banco
# con un tono conocido antes de asumirlo correcto (README seccion 5).

DEVICE = os.environ.get("INMP441_DEVICE")  # nombre o indice; ver docstring, punto 4


def _extract_24bit(raw_block: np.ndarray) -> np.ndarray:
    """Extrae los 24 bits validos de cada muestra de 32 bits (ver docstring del modulo)."""
    return np.right_shift(raw_block, BIT_SHIFT)


def main() -> None:
    print(
        f"# I2S configurado: {SAMPLE_RATE_HZ} Hz, mono, trama de 32 bits (24 bits validos)",
        file=sys.stderr,
    )
    print("timestamp_us,sample_24bit")

    def callback(indata: np.ndarray, frames: int, time_info, status: sd.CallbackFlags) -> None:
        if status:
            # xruns (underrun/overrun) del driver ALSA: a diferencia del
            # jitter de espacio de usuario del sensor de vibracion, un
            # xrun aqui es evidencia de perdida real de datos en el
            # buffer DMA -- reportar siempre, no descartar en silencio.
            print(f"# ALSA status: {status}", file=sys.stderr)

        # Mismo timestamp para todas las muestras del bloque, igual que
        # el firmware ESP32 (un solo micros() por llamada a i2s_read()):
        # se mantiene la paridad de formato entre ambas plataformas.
        timestamp_us = time.perf_counter_ns() // 1_000
        samples = _extract_24bit(indata[:, 0])
        for sample in samples:
            print(f"{timestamp_us},{int(sample)}")

    try:
        stream = sd.InputStream(
            device=DEVICE,
            samplerate=SAMPLE_RATE_HZ,
            channels=CHANNELS,
            dtype=SAMPLE_DTYPE,
            blocksize=BLOCK_SIZE,
            callback=callback,
        )
    except sd.PortAudioError as exc:
        sys.exit(
            f"ERROR: no se pudo abrir el dispositivo de captura I2S ({exc}).\n"
            "       Verificar: 1) dtparam=i2s=on y el overlay de tarjeta de\n"
            "       sonido en /boot/config.txt, 2) que `arecord -l` liste el\n"
            "       microfono, 3) la variable de entorno INMP441_DEVICE si el\n"
            "       dispositivo por defecto no es el correcto (ver docstring)."
        )

    with stream:
        print("# Captura iniciada. Ctrl+C para detener.", file=sys.stderr)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

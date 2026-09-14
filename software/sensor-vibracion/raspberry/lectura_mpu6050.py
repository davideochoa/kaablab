#!/usr/bin/env python3
"""
MPU6050 — Lectura por polling via I2C (Raspberry Pi 4 Model B, 2GB)
KaabLab — vibracion estructural, banda objetivo 300-600 Hz (Hrncir et al. 2006)

Equivalente Python de ../arduino/mpu6050_polling.ino (Ruta A). Replica la
MISMA configuracion de muestreo ya validada en la version ESP32 (ver
README.md, secciones 2 y 3, antes de modificar este script):

    SMPLRT_DIV = 2, DLPF_CFG = 0 (deshabilitado, reloj base 8 kHz)
    Sample Rate objetivo = 8000 / (1 + 2) = 2666.67 Hz
    Nyquist objetivo     = ~1333 Hz  (>= 1200 Hz requerido, README seccion 2.1)

ADVERTENCIA — misma limitacion documentada en README.md seccion 2.2:
el ADC del acelerometro del MPU6050 actualiza su valor internamente a
1 kHz FIJO sin importar como se configure SMPLRT_DIV (Register Map
oficial RM-MPU-6000A-00, Registro 25). El Nyquist REAL del canal de
aceleracion queda limitado a ~500 Hz, no a los ~1333 Hz que sugeriria
el Sample Rate configurado. Esta limitacion es identica en ESP32 y en
Raspberry Pi: es del sensor, no de la plataforma que lo lee.

RIESGO ESPECIFICO DE ESTA PLATAFORMA (Raspberry Pi / Linux) — ver
docs/arquitectura-hardware/README.md, seccion 3.1, y la seccion "Manejo
de temporizacion" mas abajo en este archivo: a diferencia del firmware
bare-metal del ESP32, Linux no es un sistema operativo de tiempo real.
Este script NO puede garantizar 2667 Hz estables en espacio de usuario
estandar de Python — ver esa seccion para el analisis completo y la
tasa real esperable.

Libreria: smbus2 (pip install smbus2)
  https://pypi.org/project/smbus2/
  Se eligio smbus2 en vez de la libreria de alto nivel
  "mpu6050-raspberrypi" (paquete PyPI) porque esta ultima no siempre
  expone de forma directa el divisor de sample rate (SMPLRT_DIV) ni el
  filtro pasa-bajas digital (DLPF_CFG) — igual que en la version Arduino
  (README.md seccion 3.1), donde se prefirio I2Cdevlib sobre
  Adafruit_MPU6050 por la misma razon. smbus2 da acceso directo a los
  registros del MPU6050, permitiendo replicar EXACTAMENTE la misma
  configuracion validada en el firmware ESP32.

Pin mapping (Raspberry Pi 4 Model B, ver docs/arquitectura-hardware/README.md,
seccion 4 — mapeo GPIO BCM equivalente al de ESP32 DevKit V1):
  SDA = GPIO2  (pin fisico 3)  — bus I2C 1 (/dev/i2c-1)
  SCL = GPIO3  (pin fisico 5)
  Bus compartido con el sensor de temperatura/humedad de precision
  (ver ../../sensor-temperatura-humedad-precision/), sin conflicto de
  direcciones (MPU6050 en 0x68/0x69, sensor de precision en 0x44/0x45).

Requisitos del sistema antes de ejecutar:
  1. Habilitar el bus I2C: `sudo raspi-config` -> Interface Options -> I2C.
  2. Verificar que el sensor responde: `sudo i2cdetect -y 1` (debe listar
     0x68, o 0x69 si AD0 esta a VCC).
  3. Para la promocion a tiempo real (ver mas abajo), ejecutar con
     privilegios: `sudo python3 lectura_mpu6050.py`, o en su defecto
     otorgar la capability sin usar root completo:
     `sudo setcap cap_sys_nice+ep $(readlink -f $(which python3))`
     (afecta a TODO lo ejecutado con ese interprete: usar con criterio).
"""

from __future__ import annotations

import os
import struct
import sys
import threading
import time

try:
    from smbus2 import SMBus
except ImportError:
    sys.exit(
        "ERROR: falta la libreria smbus2. Instalar con: pip install smbus2"
    )

# --- Direccion I2C y registros del MPU6050 (RM-MPU-6000A-00) ---
MPU6050_ADDR = 0x68            # AD0 a GND (por defecto en este proyecto); 0x69 si AD0 a VCC
REG_PWR_MGMT_1 = 0x6B
REG_SMPLRT_DIV = 0x19
REG_CONFIG = 0x1A              # DLPF_CFG en bits [2:0]
REG_GYRO_CONFIG = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_ACCEL_XOUT_H = 0x3B        # lectura burst de 6 bytes: ACCEL_X/Y/Z (H+L cada eje)
REG_WHO_AM_I = 0x75

I2C_BUS_NUM = 1                 # /dev/i2c-1, GPIO2 (SDA) / GPIO3 (SCL)

# --- Calculo de sample rate (ver README.md seccion 2.1 — identico al firmware ESP32) ---
SMPLRT_DIV_TARGET = 2
DLPF_CFG = 0                    # 0 (o 7) = DLPF deshabilitado, reloj base 8 kHz
SAMPLE_RATE_HZ = 8000.0 / (1 + SMPLRT_DIV_TARGET)   # ~2666.67 Hz
SAMPLE_INTERVAL_S = 1.0 / SAMPLE_RATE_HZ            # ~375 us

ACCEL_FS_4G = 0x08              # AFS_SEL=01 en bits [4:3] de ACCEL_CONFIG -> +/-4g (igual que Arduino)
GYRO_FS_500 = 0x08              # FS_SEL=01  en bits [4:3] de GYRO_CONFIG  -> 500 dps (igual que Arduino)


# ---------------------------------------------------------------------------
# Manejo de temporizacion: por que Linux no es tiempo real, y que hacemos
# ---------------------------------------------------------------------------
#
# El firmware ESP32 (arduino/mpu6050_polling.ino) logra temporizacion
# confiable con un simple bucle no bloqueante basado en micros() porque
# corre bare-metal: no hay planificador de procesos, no hay otros programas
# compitiendo por CPU, y la latencia de cada instruccion es predecible.
#
# Raspberry Pi corre Linux (sistema operativo de proposito general, sin
# garantias de tiempo real bajo el planificador por defecto CFS). Tres
# fuentes de jitter que NO existen en el ESP32:
#
#   1. El planificador puede preemptar este proceso en cualquier momento
#      para atender otros procesos, interrupciones de hardware o E/S.
#   2. time.sleep() en Linux estandar (no-RT) tiene granularidad real de
#      varios cientos de microsegundos a un par de milisegundos — muy por
#      encima del intervalo objetivo de ~375 us a 2667 Hz. Por eso este
#      script NO usa time.sleep() para temporizar el muestreo: usa un
#      busy-wait (spin) sobre time.perf_counter(), a costa de mantener un
#      nucleo de CPU ocupado al 100% mientras muestrea.
#   3. El interprete de Python anade su propio overhead por iteracion
#      (dispatch de bytecode, GIL, la llamada a smbus2 que dispara una
#      syscall ioctl() al driver del kernel) por encima del limite fisico
#      del bus I2C. El propio README (seccion 2.3) ya calcula ese limite
#      fisico en ESP32: ~4900 transacciones/s teoricas, ~3000-4000/s
#      conservador. Python anade tipicamente cientos de microsegundos
#      adicionales de overhead de interprete + syscall por lectura, sobre
#      ese mismo limite de bus.
#
# Mitigacion implementada (mejor esfuerzo, no garantia):
#
#   - El muestreo corre en un hilo dedicado (_sampling_loop), separado del
#     hilo principal que solo espera/imprime.
#   - Ese hilo intenta promoverse a la politica de planificacion POSIX de
#     tiempo real SCHED_FIFO via os.sched_setscheduler() (requiere
#     privilegios: root o capability CAP_SYS_NICE, ver docstring del
#     modulo). Bajo SCHED_FIFO, el planificador no puede preemptar este
#     hilo en favor de procesos de prioridad normal, reduciendo (no
#     eliminando) el jitter de la fuente (1).
#   - Ese hilo intenta ademas fijar su afinidad a un nucleo especifico
#     (os.sched_setaffinity) para reducir jitter por migracion entre
#     nucleos — la Raspberry Pi 4 tiene 4 nucleos; se reserva el ultimo
#     para este hilo.
#   - El bucle de muestreo usa busy-wait sobre time.perf_counter() en vez
#     de time.sleep(), evitando la fuente (2).
#   - Ninguna mitigacion aqui resuelve la fuente (3): el overhead de
#     interprete + syscall de Python es inherente a leer registro por
#     registro desde espacio de usuario en Python puro.
#
# TASA REAL ESPERABLE (estimacion de ingenieria, NO medida en banco
# todavia — ver seccion 5 del README y la nota de validacion mas abajo):
# incluso con SCHED_FIFO y afinidad fijada, un estimado conservador y
# realista para muestreo sostenido, de bajo jitter, en Python puro sobre
# Raspberry Pi 4 es del orden de **500-1000 Hz** — muy por debajo de los
# ~2667 Hz configurados en el propio sensor. Acercarse al objetivo de
# 2667 Hz de forma sostenida probablemente requiera, en una iteracion
# futura, leer rafagas de multiples muestras ya acumuladas en el FIFO
# interno del MPU6050 en cada transaccion I2C (equivalente Python de la
# Ruta B / arduino/mpu6050_interrupt_fifo.ino), amortizando el overhead
# de cada syscall entre varias muestras en vez de pagarlo por muestra
# individual — o mover el bucle de muestreo critico a una extension en C
# o a un driver de kernel (IIO), dejando Python solo para post-proceso.
# Este script implementa unicamente el equivalente de la Ruta A
# (polling simple); no implementa la ruta FIFO.
# ---------------------------------------------------------------------------


def _try_set_realtime_priority(priority: int = 30) -> bool:
    """Intenta promover el hilo/proceso actual a SCHED_FIFO.

    Requiere privilegios (root o capability CAP_SYS_NICE). Si falla,
    el muestreo continua bajo planificacion normal (SCHED_OTHER), con
    mayor jitter esperado (ver seccion "Manejo de temporizacion" arriba).
    Devuelve True si la promocion tuvo exito.
    """
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(priority))
        return True
    except (AttributeError, PermissionError, OSError):
        return False


def _try_pin_cpu_affinity(cpu_id: int = 3) -> bool:
    """Intenta fijar la afinidad del hilo actual a un solo nucleo.

    Reduce jitter por migracion entre nucleos. La Raspberry Pi 4 tiene
    4 nucleos (0-3); por defecto se reserva el ultimo. No requiere
    privilegios especiales, pero puede no estar disponible en todas las
    plataformas (solo Linux). Devuelve True si tuvo exito.
    """
    try:
        os.sched_setaffinity(0, {cpu_id})
        return True
    except (AttributeError, OSError):
        return False


def _verify_connection(bus: SMBus) -> None:
    who_am_i = bus.read_byte_data(MPU6050_ADDR, REG_WHO_AM_I)
    # 0x68 = MPU6050, 0x70 = MPU6500 (algunas placas "GY-521" genericas
    # montan ese die en su lugar — ver README.md seccion 2.2, ultimo punto).
    if who_am_i not in (0x68, 0x70):
        sys.exit(
            f"ERROR: MPU6050 no responde como se esperaba en 0x{MPU6050_ADDR:02X} "
            f"(WHO_AM_I=0x{who_am_i:02X}). Verificar cableado/direccion "
            f"(ver diagrama_conexion.svg)."
        )


def _configure_mpu6050(bus: SMBus) -> None:
    # Despertar el sensor (sale de modo sleep tras power-on/reset).
    bus.write_byte_data(MPU6050_ADDR, REG_PWR_MGMT_1, 0x00)
    time.sleep(0.1)  # margen de arranque tras salir de sleep; no es temporizacion de muestreo

    # DLPF_CFG = 0: deshabilita el filtro pasa-bajas interno -> reloj base 8 kHz.
    # ADVERTENCIA (README.md seccion 2.2): el ADC del acelerometro sigue
    # muestreando internamente a 1 kHz fijo sin importar este ajuste.
    bus.write_byte_data(MPU6050_ADDR, REG_CONFIG, DLPF_CFG)
    bus.write_byte_data(MPU6050_ADDR, REG_SMPLRT_DIV, SMPLRT_DIV_TARGET)

    bus.write_byte_data(MPU6050_ADDR, REG_ACCEL_CONFIG, ACCEL_FS_4G)   # +/-4g, igual que Arduino
    bus.write_byte_data(MPU6050_ADDR, REG_GYRO_CONFIG, GYRO_FS_500)    # 500 dps, igual que Arduino


def _read_acceleration(bus: SMBus) -> tuple[int, int, int]:
    # Lectura burst de 6 bytes (equivalente a mpu.getAcceleration() en el
    # firmware ESP32): un unico bloque I2C en vez de 3 lecturas de 2 bytes.
    data = bus.read_i2c_block_data(MPU6050_ADDR, REG_ACCEL_XOUT_H, 6)
    ax, ay, az = struct.unpack(">hhh", bytes(data))
    return ax, ay, az


def _sampling_loop(bus: SMBus, stop_event: threading.Event) -> None:
    rt_ok = _try_set_realtime_priority()
    affinity_ok = _try_pin_cpu_affinity()
    print(
        f"# hilo de muestreo: SCHED_FIFO={'si' if rt_ok else 'NO (sin privilegios; ver docstring)'}"
        f", afinidad de CPU fijada={'si' if affinity_ok else 'no'}",
        file=sys.stderr,
    )

    next_sample_time = time.perf_counter()
    while not stop_event.is_set():
        now = time.perf_counter()
        if now < next_sample_time:
            # Busy-wait, NO time.sleep(): ver "Manejo de temporizacion" arriba.
            continue

        next_sample_time += SAMPLE_INTERVAL_S
        timestamp_us = time.perf_counter_ns() // 1_000
        ax, ay, az = _read_acceleration(bus)
        print(f"{timestamp_us},{ax},{ay},{az}")

        # Si nos atrasamos mas de un intervalo completo (p. ej. tras una
        # preemption larga del planificador), resincronizar en vez de
        # intentar "recuperar" muestras perdidas con lecturas en rafaga:
        # una muestra perdida aqui es evidencia de jitter, no un error a
        # ocultar — debe quedar visible en la validacion de banco (seccion 5).
        if next_sample_time < now:
            next_sample_time = now + SAMPLE_INTERVAL_S


def main() -> None:
    with SMBus(I2C_BUS_NUM) as bus:
        _verify_connection(bus)
        _configure_mpu6050(bus)

        print(f"# Sample Rate configurado: {SAMPLE_RATE_HZ:.2f} Hz", file=sys.stderr)
        print(
            "# ADVERTENCIA: tasa real sujeta a jitter de Linux no-RT — "
            "ver docstring del modulo y docs/arquitectura-hardware/README.md seccion 3.1",
            file=sys.stderr,
        )
        print("timestamp_us,ax,ay,az")

        stop_event = threading.Event()
        sampling_thread = threading.Thread(
            target=_sampling_loop, args=(bus, stop_event), daemon=True
        )
        sampling_thread.start()

        try:
            while sampling_thread.is_alive():
                sampling_thread.join(timeout=1.0)
        except KeyboardInterrupt:
            stop_event.set()
            sampling_thread.join()


if __name__ == "__main__":
    main()

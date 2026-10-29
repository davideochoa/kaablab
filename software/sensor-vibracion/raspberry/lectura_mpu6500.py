#!/usr/bin/env python3
"""
MPU6500 — Lectura por polling via I2C (Raspberry Pi 4 Model B, 2GB)
KaabLab — vibracion estructural, banda objetivo 300-600 Hz (Hrncir et al. 2000, 2006)

Equivalente Python de ../arduino/mpu6500_polling/mpu6500_polling.ino
(Ruta A). Replica la MISMA configuracion de muestreo del firmware ESP32
(ver ../README.md, secciones 2 y 3, antes de modificar este script):

    FS_VIB  = 1500 Hz  (Nyquist = 750 Hz, margen 1.25x sobre 600 Hz)
    DLPF del acelerometro DESACTIVADO (ACCEL_CONFIG2, accel_fchoice_b = 1)
    -> salida interna del acelerometro a 4 kHz; SMPLRT_DIV no la divide.
    La tasa de 1500 Hz se impone por temporizacion en este script, igual
    que en el firmware ESP32 (polling con periodo ~667 us).

Hardware: MPU6500 (modulo GY-6500), NO MPU6050. A diferencia del MPU6050
(ADC del acelerometro fijo en 1 kHz), el acelerometro del MPU6500 admite
salida de hasta 4 kHz con el DLPF desactivado (MPU-6500 Product
Specification Rev 1.1, Tabla 2; ver ../README.md seccion 2.2).

RIESGO ESPECIFICO DE ESTA PLATAFORMA (Raspberry Pi / Linux) — ver
docs/arquitectura-hardware/README.md, seccion 3.1, y la seccion "Manejo
de temporizacion" mas abajo en este archivo: a diferencia del firmware
bare-metal del ESP32, Linux no es un sistema operativo de tiempo real.
Este script NO puede garantizar 1500 Hz estables en espacio de usuario
estandar de Python — ver esa seccion para el analisis completo y la
tasa real esperable.

Libreria: smbus2 (pip install smbus2)
  https://pypi.org/project/smbus2/
  smbus2 da acceso directo a los registros del MPU6500 (ACCEL_CONFIG2,
  ACCEL_CONFIG, WHO_AM_I), permitiendo replicar EXACTAMENTE la misma
  configuracion del firmware ESP32 (que usa la clase MPU6500_WE de la
  libreria MPU9250_WE).

Pin mapping (Raspberry Pi 4 Model B, ver docs/arquitectura-hardware/README.md,
seccion 4 — mapeo GPIO BCM equivalente al de ESP32 DevKit V1):
  SDA = GPIO2  (pin fisico 3)  — bus I2C 1 (/dev/i2c-1)
  SCL = GPIO3  (pin fisico 5)
  AD0 del MPU6500 a 3.3 V -> direccion I2C 0x69.
  Bus compartido, sin conflicto de direcciones:
    SHT31  (sensor de precision) 0x44 — ../../sensor-temperatura-humedad-precision/
    DS3231 (RTC del sistema)     0x68 — por eso el MPU6500 NO puede quedar en 0x68
    MPU6500 (este sensor)        0x69

Requisitos del sistema antes de ejecutar:
  1. Habilitar el bus I2C: `sudo raspi-config` -> Interface Options -> I2C.
     OBLIGATORIO: fijar la velocidad del bus a 400 kHz con
     `dtparam=i2c_arm_baudrate=400000` en /boot/firmware/config.txt
     (/boot/config.txt en versiones anteriores) y reiniciar. Por defecto el
     bus corre a 100 kHz; a esa velocidad una lectura de ~81 bits ocupa
     ~810 us, mas que el periodo de ~667 us: los 1500 Hz son IMPOSIBLES a
     100 kHz. La velocidad es unica para todo el bus (SHT31, DS3231 y
     MPU6500 la comparten).
  2. Verificar que el sensor responde: `sudo i2cdetect -y 1` (debe listar
     0x69 para el MPU6500; 0x68 aparece como "UU" si el DS3231 ya esta
     tomado por el driver RTC del kernel, ver docs/arquitectura-hardware/
     README.md seccion 4).
  3. Para la promocion a tiempo real (ver mas abajo), ejecutar con
     privilegios: `sudo python3 lectura_mpu6500.py`, o en su defecto
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

# --- Direccion I2C y registros del MPU6500 (MPU-6500 Register Map Rev 2.1) ---
MPU6500_ADDR = 0x69            # AD0 a 3.3 V (0x68 lo ocupa el DS3231)
MPU6500_WHO_AM_I = 0x70        # valor esperado de WHO_AM_I en el MPU6500
REG_PWR_MGMT_1 = 0x6B
REG_ACCEL_CONFIG = 0x1C        # ACCEL_FS_SEL en bits [4:3]
REG_ACCEL_CONFIG2 = 0x1D       # ACCEL_FCHOICE_B en bit 3, A_DLPF_CFG en bits [2:0]
REG_ACCEL_XOUT_H = 0x3B        # lectura burst de 6 bytes: ACCEL_X/Y/Z (H+L cada eje)
REG_WHO_AM_I = 0x75

I2C_BUS_NUM = 1                 # /dev/i2c-1, GPIO2 (SDA) / GPIO3 (SCL)

# --- Tasa de muestreo (ver ../README.md seccion 2.1 — identica al firmware ESP32) ---
FS_VIB = 1500                   # Hz, igual que FS_VIB en nodo_kaablab/config.h
SAMPLE_INTERVAL_S = 1.0 / FS_VIB            # ~667 us
LATE_THRESHOLD_S = SAMPLE_INTERVAL_S * 1.10 # +10 %, mismo criterio que sensores_capturar_vibracion()

ACCEL_FS_4G = 0x08              # ACCEL_FS_SEL=01 -> +/-4g (igual que Arduino)
ACCEL_LSB_PER_G = 8192.0        # sensibilidad a +/-4g (datasheet MPU-6500, Tabla 2)
ACCEL_DLPF_OFF = 0x08           # ACCEL_FCHOICE_B = 1 -> DLPF desactivado, salida a 4 kHz


# ---------------------------------------------------------------------------
# Manejo de temporizacion: por que Linux no es tiempo real, y que hacemos
# ---------------------------------------------------------------------------
#
# El firmware ESP32 (arduino/mpu6500_polling/mpu6500_polling.ino) logra
# temporizacion confiable con un simple bucle no bloqueante basado en
# micros() porque corre bare-metal: no hay planificador de procesos, no hay
# otros programas compitiendo por CPU, y la latencia de cada instruccion es
# predecible.
#
# Raspberry Pi corre Linux (sistema operativo de proposito general, sin
# garantias de tiempo real bajo el planificador por defecto CFS). Tres
# fuentes de jitter que NO existen en el ESP32:
#
#   1. El planificador puede preemptar este proceso en cualquier momento
#      para atender otros procesos, interrupciones de hardware o E/S.
#   2. time.sleep() en Linux estandar (no-RT) tiene granularidad real de
#      varios cientos de microsegundos a un par de milisegundos — del mismo
#      orden que el intervalo objetivo de ~667 us a 1500 Hz. Por eso este
#      script NO usa time.sleep() para temporizar el muestreo: usa un
#      busy-wait (spin) sobre time.perf_counter(), a costa de mantener un
#      nucleo de CPU ocupado al 100% mientras muestrea.
#   3. El interprete de Python anade su propio overhead por iteracion
#      (dispatch de bytecode, GIL, la llamada a smbus2 que dispara una
#      syscall ioctl() al driver del kernel) por encima del limite fisico
#      del bus I2C. El README (seccion 2.3) calcula ese limite fisico:
#      ~4900 transacciones/s teoricas, ~3000-4000/s conservador. Python
#      anade tipicamente cientos de microsegundos adicionales de overhead
#      de interprete + syscall por lectura, sobre ese mismo limite de bus.
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
#   - Igual que el firmware del nodo, se cuentan las muestras que llegan
#     con un intervalo > +10 % del esperado y se reporta al terminar, para
#     que el jitter quede visible en la validacion de banco.
#
# TASA REAL ESPERABLE (estimacion de ingenieria, NO medida en banco
# todavia — ver seccion 5 del README y la nota de validacion mas abajo):
# incluso con SCHED_FIFO y afinidad fijada, un estimado conservador y
# realista para muestreo sostenido, de bajo jitter, en Python puro sobre
# Raspberry Pi 4 es del orden de **500-1000 Hz** — por debajo de los
# 1500 Hz objetivo. Alcanzar 1500 Hz de forma sostenida probablemente
# requiera, en una iteracion futura, leer rafagas de multiples muestras
# ya acumuladas en el FIFO interno del MPU6500 en cada transaccion I2C
# (equivalente Python de la Ruta B /
# arduino/mpu6500_interrupt_fifo/mpu6500_interrupt_fifo.ino), amortizando
# el overhead de cada syscall entre varias muestras — o mover el bucle de
# muestreo critico a una extension en C o a un driver de kernel (IIO),
# dejando Python solo para post-proceso. Este script implementa
# unicamente el equivalente de la Ruta A (polling simple).
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
    who_am_i = bus.read_byte_data(MPU6500_ADDR, REG_WHO_AM_I)
    if who_am_i != MPU6500_WHO_AM_I:
        sys.exit(
            f"ERROR: MPU6500 no detectado en 0x{MPU6500_ADDR:02X} "
            f"(WHO_AM_I=0x{who_am_i:02X}, esperado 0x{MPU6500_WHO_AM_I:02X}). "
            f"Verificar cableado y AD0 a 3.3 V (ver diagrama_conexion.svg)."
        )


def _configure_mpu6500(bus: SMBus) -> None:
    # Despertar el sensor (sale de modo sleep tras power-on/reset).
    bus.write_byte_data(MPU6500_ADDR, REG_PWR_MGMT_1, 0x00)
    time.sleep(0.1)  # margen de arranque tras salir de sleep; no es temporizacion de muestreo

    bus.write_byte_data(MPU6500_ADDR, REG_ACCEL_CONFIG, ACCEL_FS_4G)  # +/-4g, igual que Arduino

    # Tras el reset el DLPF del acelerometro queda activo (5-260 Hz) y
    # atenuaria la banda 300-600 Hz. Se desactiva (accel_fchoice_b = 1):
    # salida a 4 kHz, ancho de banda ~1046 Hz. Equivale a enableAccDLPF(false).
    bus.write_byte_data(MPU6500_ADDR, REG_ACCEL_CONFIG2, ACCEL_DLPF_OFF)


def _read_acceleration_mg(bus: SMBus) -> tuple[int, int, int]:
    # Lectura burst de 6 bytes (equivalente a mpu.getGValues() en el
    # firmware ESP32): un unico bloque I2C en vez de 3 lecturas de 2 bytes.
    data = bus.read_i2c_block_data(MPU6500_ADDR, REG_ACCEL_XOUT_H, 6)
    raw = struct.unpack(">hhh", bytes(data))
    # A mg, mismo formato de salida que el .ino y nodo_kaablab.
    ax, ay, az = (int(v * 1000.0 / ACCEL_LSB_PER_G) for v in raw)
    return ax, ay, az


def _sampling_loop(bus: SMBus, stop_event: threading.Event, stats: dict) -> None:
    rt_ok = _try_set_realtime_priority()
    affinity_ok = _try_pin_cpu_affinity()
    print(
        f"# hilo de muestreo: SCHED_FIFO={'si' if rt_ok else 'NO (sin privilegios; ver docstring)'}"
        f", afinidad de CPU fijada={'si' if affinity_ok else 'no'}",
        file=sys.stderr,
    )

    next_sample_time = time.perf_counter()
    last_sample_time = None
    while not stop_event.is_set():
        now = time.perf_counter()
        if now < next_sample_time:
            # Busy-wait, NO time.sleep(): ver "Manejo de temporizacion" arriba.
            continue

        next_sample_time += SAMPLE_INTERVAL_S
        timestamp_us = time.perf_counter_ns() // 1_000
        ax, ay, az = _read_acceleration_mg(bus)
        print(f"{timestamp_us},{ax},{ay},{az}")

        stats["muestras"] += 1
        if last_sample_time is not None and now - last_sample_time > LATE_THRESHOLD_S:
            stats["tardias"] += 1
        last_sample_time = now

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
        _configure_mpu6500(bus)

        print(f"# Sample Rate objetivo: {FS_VIB} Hz", file=sys.stderr)
        print(
            "# ADVERTENCIA: tasa real sujeta a jitter de Linux no-RT — "
            "ver docstring del modulo y docs/arquitectura-hardware/README.md seccion 3.1",
            file=sys.stderr,
        )
        print("timestamp_us,ax_mg,ay_mg,az_mg")

        stats = {"muestras": 0, "tardias": 0}
        stop_event = threading.Event()
        sampling_thread = threading.Thread(
            target=_sampling_loop, args=(bus, stop_event, stats), daemon=True
        )
        sampling_thread.start()

        try:
            while sampling_thread.is_alive():
                sampling_thread.join(timeout=1.0)
        except KeyboardInterrupt:
            stop_event.set()
            sampling_thread.join()

        if stats["tardias"]:
            print(
                f"# ADVERTENCIA: {stats['tardias']} de {stats['muestras']} muestras "
                f"excedieron el periodo esperado (+10 %, {LATE_THRESHOLD_S * 1e6:.0f} us)",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()

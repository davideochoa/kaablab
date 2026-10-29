#!/usr/bin/env python3
"""
SHT31 — Lectura de temperatura y humedad relativa interna via I2C
(Raspberry Pi 4 Model B, 2GB)
KaabLab — sensor interno primario (ver README.md, secciones 0-2, para
la justificacion de por que existe este sensor junto al DHT22 externo).

Equivalente Python de ../arduino/sht31_lectura/sht31_lectura.ino.

Libreria: smbus2 (pip install smbus2)
    Se eligio smbus2, con acceso directo a los registros/comandos I2C
    del SHT31, por la misma razon documentada en
    ../../sensor-vibracion/raspberry/lectura_mpu6500.py para preferir
    smbus2 sobre una libreria de alto nivel: acceso explicito al modo
    de medicion exacto (aqui, "single shot, sin clock stretching" — ver
    seccion "Por que sin clock stretching" mas abajo), en vez de
    depender de que una libreria de alto nivel (p. ej.
    `adafruit-circuitpython-sht31d`) lo exponga de forma directa.
    `adafruit-circuitpython-sht31d` es una alternativa valida; si se
    usa, confirmar en su documentacion que use el mismo modo sin clock
    stretching antes de asumir el analisis de bus de este archivo.

Nota de confiabilidad (a diferencia de ../../sensor-temperatura-humedad-basico/raspberry/lectura_dht22.py):
    El SHT31 usa I2C estandar, no un protocolo de timing critico de un
    solo hilo. Por lo tanto NO hereda el riesgo de jitter de
    planificador documentado en docs/arquitectura-hardware/README.md,
    seccion 3.2 (ese riesgo es especifico del protocolo de un solo
    hilo del DHT22). Lo que SI comparte este sensor es el bus I2C fisico
    con el sensor de vibracion estructural (MPU6500, ver
    ../../sensor-vibracion/raspberry/lectura_mpu6500.py) y con el RTC
    DS3231 del sistema — ver el
    analisis de throughput en la seccion siguiente, replicando el
    mismo tipo de calculo ya hecho para ese sensor.

Pin mapping confirmado del proyecto (docs/arquitectura-hardware/README.md,
seccion 4): SDA = GPIO2 (pin fisico 3), SCL = GPIO3 (pin fisico 5) — bus
I2C 1 (/dev/i2c-1), compartido sin conflicto de direcciones:
    SHT31   (este sensor)          0x44 (ADDR a GND)
    DS3231  (RTC del sistema)      0x68 (driver rtc-ds1307 del kernel)
    MPU6500 (vibracion)            0x69 (AD0 a 3.3 V)
El DS3231 solo transacciona al leer/ajustar la hora del sistema (arranque,
hwclock), por lo que su ocupacion del bus es despreciable.

---------------------------------------------------------------------
Analisis de throughput del bus compartido (SHT31 baja frecuencia +
MPU6500 alta frecuencia) — replica del calculo de
../../sensor-vibracion/README.md, seccion 2.3, aplicado a este sensor
---------------------------------------------------------------------

Por que este script usa el comando "single shot, sin clock stretching"
(0x2400, alta repetibilidad) en vez de un modo con clock stretching:

    El SHT31 soporta dos formas de indicar "todavia estoy convirtiendo,
    espera": (a) clock stretching, donde el propio sensor mantiene la
    linea SCL en bajo durante la conversion (~15 ms en modo alta
    repetibilidad), bloqueando FISICAMENTE el bus I2C completo — ningun
    otro dispositivo (incluido el MPU6500) puede transaccionar mientras
    tanto; o (b) polling explicito sin clock stretching, donde el host
    envia el comando de medicion, libera el bus de inmediato, espera
    por software, y luego hace una transaccion de lectura separada.

    Este script usa (b) precisamente para NO bloquear el bus compartido
    durante los ~15 ms de conversion: ese tiempo de espera transcurre
    con el bus I2C completamente libre para que el MPU6500 (leido desde
    otro hilo/proceso a 1500 Hz, ver sensor-vibracion) siga
    transaccionando sin interrupcion. Usar el modo con clock stretching
    aqui seria el equivalente exacto, en el bus I2C, al riesgo de
    `delay()` bloqueante que sensor-vibracion/README.md (seccion 2.3)
    ya identifica como el riesgo real para ese sensor.

Calculo de ocupacion real del bus por este sensor:

    Una lectura completa del SHT31 son dos transacciones I2C separadas:
      1. Escritura del comando (2 bytes): direccion+W(9) + cmd_msb(9) +
         cmd_lsb(9) ~= 27 bits
      2. Lectura de 6 bytes (temp MSB/LSB/CRC + hum MSB/LSB/CRC), tras
         el retardo de conversion: repeated start + direccion+R(9) +
         6 bytes*9 = 54 ~= 63 bits

    Bits totales de bus ocupado por ciclo de lectura ~= 90 bits.
    El bus I2C tiene UNA sola velocidad para todos sus dispositivos
    (dtparam=i2c_arm_baudrate). Como el MPU6500 exige 400 kHz para
    sostener 1500 Hz (ver ../../sensor-vibracion/raspberry/lectura_mpu6500.py),
    el SHT31 tambien transacciona a 400 kHz:
    90 / 400_000 ~= 225 us de bus ocupado.

    Este script lee el SHT31 una vez por segundo (mismo intervalo que
    ../arduino/sht31_lectura/sht31_lectura.ino, READ_INTERVAL_S = 1.0), por lo que su
    "duty cycle" sobre el bus es aproximadamente:

        225 us / 1_000_000 us ~= 0.02% del tiempo de bus por segundo

    Frente al presupuesto del MPU6500 (sensor-vibracion/README.md,
    seccion 2.3): 1500 lecturas/s, ~81 bits cada una, a 400 kHz
    (Fast Mode) ~= 203 us de bus ocupado por lectura, ~30% de duty
    cycle continuo sobre el bus a 400 kHz.

    CONCLUSION DEL ANALISIS (no sustituye la validacion de banco,
    ver README.md seccion de validacion): el SHT31, leido una vez por
    segundo en modo sin clock stretching, consume una fraccion
    despreciable (~0.02%) del tiempo de bus frente al presupuesto ya
    del MPU6500 (~30% a 400 kHz). El riesgo de contencion
    NO esta en el ancho de banda agregado del bus, sino en la
    posibilidad de que una transaccion del SHT31 se intercale, en el
    peor caso, justo en medio de la ventana de tiempo entre dos
    muestras consecutivas del MPU6500 (~667 us a 1500 Hz) e introduzca
    un retardo puntual de hasta ~225 us (a 400 kHz) en esa muestra especifica —
    un jitter puntual, no un problema de throughput sostenido. Esto
    debe confirmarse empiricamente (ver README.md, seccion de
    validacion): capturar con analizador logico el bus compartido
    mientras ambos sensores leen de forma concurrente, y verificar que
    ninguna muestra del MPU6500 se retrasa mas alla de lo que el
    analisis de jitter de sensor-vibracion (seccion 3.1 de
    docs/arquitectura-hardware/README.md) ya considera tolerable.

    NOTA: si ambos sensores corren en el mismo proceso Python pero en
    hilos distintos, cada uno abriendo su propio descriptor `SMBus(1)`,
    el driver i2c-dev del kernel serializa las transacciones reales a
    nivel de adaptador (cada ioctl() individual es atomico); no se
    requiere un lock explicito en la aplicacion para evitar corrupcion
    de datos — el escenario a validar en banco es de LATENCIA/jitter
    puntual, no de corrupcion de las lecturas de ninguno de los dos
    sensores.
---------------------------------------------------------------------
"""

from __future__ import annotations

import logging
import struct
import sys
import time

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    sys.exit(
        "ERROR: falta la libreria smbus2. Instalar con: pip install smbus2"
    )

SHT31_ADDR = 0x44  # ADDR a GND en este proyecto (ver diagrama_conexion.svg); 0x45 si ADDR a VCC
I2C_BUS_NUM = 1  # /dev/i2c-1, GPIO2 (SDA) / GPIO3 (SCL)

# Comando "single shot, alta repetibilidad, SIN clock stretching"
# (datasheet SHT3x-DIS, tabla de comandos): 0x2400. Elegido
# deliberadamente sobre el equivalente con clock stretching — ver
# "Por que sin clock stretching" en el docstring del modulo.
CMD_MEDICION_SIN_CLOCK_STRETCH = (0x24, 0x00)

# Tiempo maximo de conversion en modo alta repetibilidad (datasheet
# SHT3x-DIS): 15 ms. Se espera con margen antes de leer el resultado.
TIEMPO_CONVERSION_S = 0.020

READ_INTERVAL_S = 1.0  # igual que ../arduino/sht31_lectura/sht31_lectura.ino (READ_INTERVAL_MS = 1000)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("sht31")


class SHT31ChecksumError(Exception):
    """Un byte de CRC no coincide con el dato recibido (temperatura u humedad)."""


def _crc8_sensirion(datos: bytes) -> int:
    """CRC8 usado por el SHT31 (polinomio 0x31, init 0xFF) sobre pares de bytes.

    Ver datasheet SHT3x-DIS, seccion "Checksum Calculation".
    """
    crc = 0xFF
    for byte in datos:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def _verificar_conexion(bus: SMBus) -> None:
    try:
        # Lectura de estado (0xF32D) como sondeo de presencia: si el
        # dispositivo no responde en esta direccion, smbus2 lanza OSError.
        write = i2c_msg.write(SHT31_ADDR, [0xF3, 0x2D])
        read = i2c_msg.read(SHT31_ADDR, 3)
        bus.i2c_rdwr(write)
        time.sleep(0.001)
        bus.i2c_rdwr(read)
    except OSError as exc:
        sys.exit(
            f"ERROR: SHT31 no responde en 0x{SHT31_ADDR:02X} ({exc}). "
            f"Verificar cableado/direccion (ver diagrama_conexion.svg)."
        )


def leer_una_vez(bus: SMBus) -> tuple[float, float]:
    """Dispara una medicion sin clock stretching y devuelve (temperatura_C, humedad_pct).

    Dos transacciones I2C separadas por un `time.sleep()` — ver "Por
    que sin clock stretching" en el docstring del modulo: el bus queda
    libre durante la espera, no ocupado por el propio SHT31.
    """
    cmd_msb, cmd_lsb = CMD_MEDICION_SIN_CLOCK_STRETCH
    bus.write_i2c_block_data(SHT31_ADDR, cmd_msb, [cmd_lsb])

    time.sleep(TIEMPO_CONVERSION_S)  # bus libre durante esta espera

    datos = bus.read_i2c_block_data(SHT31_ADDR, 0x00, 6)
    # Nota: read_i2c_block_data() antepone un byte de comando (0x00 aqui,
    # ignorado por el SHT31 en este modo) porque smbus asume el modelo
    # "registro + datos"; el SHT31 no usa registros, pero acepta esta
    # forma de lectura porque el primer byte no altera su estado interno
    # tras haber emitido ya el comando de medicion.

    temp_msb, temp_lsb, temp_crc, hum_msb, hum_lsb, hum_crc = datos

    if _crc8_sensirion(bytes([temp_msb, temp_lsb])) != temp_crc:
        raise SHT31ChecksumError("CRC invalido en el campo de temperatura")
    if _crc8_sensirion(bytes([hum_msb, hum_lsb])) != hum_crc:
        raise SHT31ChecksumError("CRC invalido en el campo de humedad")

    raw_temp = struct.unpack(">H", bytes([temp_msb, temp_lsb]))[0]
    raw_hum = struct.unpack(">H", bytes([hum_msb, hum_lsb]))[0]

    # Formulas de conversion del datasheet SHT3x-DIS.
    temperatura_c = -45.0 + 175.0 * (raw_temp / 65535.0)
    humedad_pct = 100.0 * (raw_hum / 65535.0)

    return temperatura_c, humedad_pct


def main() -> None:
    with SMBus(I2C_BUS_NUM) as bus:
        _verificar_conexion(bus)

        print("timestamp_ms,temperatura_C,humedad_relativa_pct")
        try:
            while True:
                inicio_ciclo = time.monotonic()
                try:
                    temperatura_c, humedad_pct = leer_una_vez(bus)
                    print(
                        f"{int(time.time() * 1000)},"
                        f"{temperatura_c:.2f},"
                        f"{humedad_pct:.2f}"
                    )
                except (OSError, SHT31ChecksumError) as exc:
                    # Falla de bus I2C o CRC: descartar la lectura en vez
                    # de propagarla al pipeline de fusion (mismo criterio
                    # que ../arduino/sht31_lectura/sht31_lectura.ino con isnan()).
                    log.warning("lectura fallida del SHT31: %s", exc)

                transcurrido = time.monotonic() - inicio_ciclo
                time.sleep(max(0.0, READ_INTERVAL_S - transcurrido))
        except KeyboardInterrupt:
            log.info("detenido por el usuario.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DHT22 (AM2302) — Lectura de temperatura y humedad relativa externa
(Raspberry Pi 4 Model B, 2GB)
KaabLab — sensor externo secundario (ver README.md, secciones 0-2, para
la justificación de por qué existe este sensor junto al SHT31 interno).

Equivalente Python de ../arduino/dht22_lectura/dht22_lectura.ino.

NOTA TECNICA SOBRE LA LIBRERIA ELEGIDA (corrige una confusion frecuente):
    La libreria "adafruit-circuitpython-dht" (modulo `adafruit_dht`) NO
    usa pigpio internamente. Es una libreria de bit-banging en espacio
    de usuario: en Raspberry Pi usa la extension C `pulseio`/`Adafruit
    Blinka`, que mide los pulsos por polling estrecho de CPU dentro del
    propio proceso Python — sujeta exactamente al mismo riesgo de
    jitter del planificador de Linux ya documentado en
    docs/arquitectura-hardware/README.md, seccion 3.2. No lo mitiga.

    Este script usa en su lugar la libreria `pigpio`
    (https://abyz.me.uk/rpi/pigpio/, `pip install pigpio`; requiere el
    daemon `pigpiod` corriendo en background: `sudo pigpiod`). El
    daemon pigpio muestrea los pines GPIO desde un proceso separado que
    programa el hardware de temporizador del SoC (DMA sobre el
    periferico PCM/PWM) para generar "ticks" —timestamps en
    microsegundos— independientes del planificador de procesos de
    Python. Cuando este script recibe un callback de flanco
    (`pigpio.EITHER_EDGE`), el tick que acompaña a ese callback ya fue
    capturado por el daemon en el instante real del flanco, no en el
    instante (potencialmente retrasado por el planificador) en que
    Python logra ejecutar el callback. Esto es lo que **mitiga, sin
    eliminar**, el riesgo de la seccion 3.2: decodificar el ancho de
    cada pulso a partir de los ticks es robusto a que el callback de
    Python se ejecute con cierto retraso, porque el retraso no
    contamina la medicion del ancho del pulso en si.

    Lo que esta mitigacion NO cubre: si el planificador retrasa el
    proceso host lo suficiente durante el propio pulso de arranque
    (host manteniendo la linea en bajo ~1-10 ms antes de soltarla, ver
    `_DHT22PigpioReader.leer_una_vez()`), el timing de ESE pulso si
    depende de `time.sleep()` en espacio de usuario y puede alargarse
    mas alla de lo esperado por el sensor. Por eso este riesgo se deja
    marcado como "mitigado parcialmente", no resuelto — ver README.md,
    seccion 5 ("Nota de validacion").

Tecnica de decodificacion: inspirada en el patron de referencia
"DHT22.py" de joan2937 (autor de pigpio) — callback de flancos +
`pigpio.tickDiff()` para medir el ancho de cada pulso alto y
clasificarlo como bit 0 o 1 por umbral. Reimplementada aqui de forma
propia, mas simple (sin el manejo de ruido/watchdog de la version
original), con logging de tasa de fallos propio del proyecto — ver
seccion 5 del README.md de este sensor ("nota de validacion"): el
detalle de decodificacion bit a bit debe verificarse contra un
analizador logico en banco antes de confiar en esta implementacion,
igual que ya se exige para sensor-vibracion y sensor-trafico.

Pin mapping confirmado del proyecto (docs/arquitectura-hardware/README.md,
seccion 4): DATA = GPIO4 (pin fisico 7) — mismo pin BCM que en ESP32.

NOTA sobre GPIO4 (docs/arquitectura-hardware/README.md, seccion 4): este
pin coincide con el reservado por defecto por Raspberry Pi OS para el
overlay 1-Wire estandar (`w1-gpio`). El protocolo del DHT22 NO es
1-Wire Dallas estandar (es un protocolo propietario de un solo hilo) —
no debe habilitarse ese overlay para este uso. Verificar en
`/boot/config.txt` que ningun otro periferico lo active antes de
cablear.

Protocolo DHT22 (ver tambien ../arduino/dht22_lectura/dht22_lectura.ino):
    1. El host mantiene la linea en bajo entre 1 y 10 ms (pulso de
       arranque), luego la libera (la resistencia pull-up la sube).
    2. El sensor responde tirando la linea a bajo ~80 us y luego
       liberandola (alto) ~80 us — cabecera, no son bits de datos.
    3. El sensor envia 40 bits. Cada bit: ~50 us en bajo, seguido de un
       pulso alto de ~26-28 us (bit 0) o ~70 us (bit 1).
    4. Los 40 bits son: humedad_alta(8) + humedad_baja(8) +
       temperatura_alta(8, bit7=signo) + temperatura_baja(8) +
       checksum(8) = suma de los primeros 4 bytes, truncada a 8 bits.

Requisitos del sistema antes de ejecutar:
  1. Instalar pigpio y arrancar el daemon:
       sudo apt install pigpio python3-pigpio
       sudo systemctl enable pigpiod --now
     (o `sudo pigpiod` para una sesion manual sin systemd).
  2. `pip install pigpio` si no se uso el paquete `python3-pigpio` del
     sistema.
"""

from __future__ import annotations

import logging
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass

try:
    import pigpio
except ImportError:
    sys.exit(
        "ERROR: falta la libreria pigpio. Instalar con: "
        "sudo apt install pigpio python3-pigpio (y arrancar el daemon "
        "con: sudo systemctl enable pigpiod --now)"
    )

DHT_GPIO = 4  # BCM, ver docs/arquitectura-hardware/README.md seccion 4

# Limite de tasa del propio sensor (identico al firmware ESP32, ver
# ../arduino/dht22_lectura/dht22_lectura.ino): no leer mas rapido de ~0.5 Hz.
READ_INTERVAL_S = 2.5

# Reintentos automaticos: el DHT22 falla intermitentemente incluso en
# ESP32 (ver ../arduino/dht22_lectura/dht22_lectura.ino, verificacion de isnan()); en
# Raspberry el riesgo es mayor por el jitter documentado arriba. Cada
# reintento respeta igualmente el limite de tasa del sensor.
MAX_REINTENTOS = 3
RETARDO_ENTRE_REINTENTOS_S = READ_INTERVAL_S

# Ventana para reportar la tasa de fallos en banco (item 6, README.md,
# seccion de validacion): cuantas lecturas recientes se promedian antes
# de emitir un resumen de tasa de fallos.
VENTANA_TASA_FALLOS = 20

TRIGGER_LOW_S = 0.003  # 3 ms: dentro del rango 1-10 ms del datasheet
TIMEOUT_RESPUESTA_S = 0.5  # margen amplio sobre los ~5 ms que dura la trama completa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("dht22")


class DHT22TimeoutError(Exception):
    """El sensor no completo la trama de 40 bits dentro del plazo esperado."""


class DHT22ChecksumError(Exception):
    """La trama se recibio completa pero el checksum no coincide."""


@dataclass
class LecturaDHT22:
    temperatura_c: float
    humedad_pct: float


class _DHT22PigpioReader:
    """Decodifica el protocolo DHT22 usando callbacks de flanco de pigpio.

    Ver la nota tecnica del docstring del modulo: el ancho de cada
    pulso se mide con los ticks de pigpio (timestamps de microsegundo
    capturados por el daemon en el instante real del flanco), no con
    timestamps tomados en el propio proceso Python al recibir el
    callback.
    """

    UMBRAL_BIT_US = 50  # diff >= 50 us de pulso alto => bit 1 (ver docstring del modulo)

    def __init__(self, pi: "pigpio.pi", gpio: int = DHT_GPIO):
        self._pi = pi
        self._gpio = gpio
        self._lock = threading.Lock()
        self._reset_estado()

    def _reset_estado(self) -> None:
        self._high_tick = 0
        self._num_flancos_bajada = 0
        self._bits: list[int] = []
        self._evento_completo = threading.Event()

    def _callback(self, gpio: int, level: int, tick: int) -> None:
        if level == 1:
            # Flanco de subida: inicio de un nuevo pulso alto.
            self._high_tick = tick
            return
        if level != 0:
            return  # pigpio.TIMEOUT del watchdog; no usado en esta implementacion

        # Flanco de bajada: el pulso alto que acaba de terminar dura
        # tickDiff(self._high_tick, tick) microsegundos.
        ancho_us = pigpio.tickDiff(self._high_tick, tick)
        self._num_flancos_bajada += 1

        # Los primeros 2 flancos de bajada cierran la cabecera de
        # respuesta del sensor (80 us + 80 us) — no son bits de datos,
        # ver docstring del modulo, "Protocolo DHT22", pasos 2-3.
        if self._num_flancos_bajada <= 2:
            return

        self._bits.append(1 if ancho_us >= self.UMBRAL_BIT_US else 0)
        if len(self._bits) >= 40:
            self._evento_completo.set()

    def leer_una_vez(self, timeout_s: float = TIMEOUT_RESPUESTA_S) -> LecturaDHT22:
        with self._lock:
            self._reset_estado()

            cb = self._pi.callback(self._gpio, pigpio.EITHER_EDGE, self._callback)
            try:
                # Pulso de arranque: host mantiene la linea en bajo.
                self._pi.set_mode(self._gpio, pigpio.OUTPUT)
                self._pi.write(self._gpio, pigpio.LOW)
                time.sleep(TRIGGER_LOW_S)

                # Libera la linea y pasa a escuchar la respuesta del
                # sensor. Pull-up interno como respaldo del pull-up del
                # propio modulo DHT22 (ver diagrama_conexion.svg).
                self._pi.set_pull_up_down(self._gpio, pigpio.PUD_UP)
                self._pi.set_mode(self._gpio, pigpio.INPUT)

                if not self._evento_completo.wait(timeout_s):
                    raise DHT22TimeoutError(
                        f"trama incompleta: {len(self._bits)}/40 bits recibidos "
                        f"en {timeout_s * 1000:.0f} ms"
                    )
            finally:
                cb.cancel()
                # Deja la linea en alto (idle) via pull-up, sin manejarla
                # activamente, para no interferir con la siguiente lectura.
                self._pi.set_mode(self._gpio, pigpio.INPUT)

            return self._decodificar(self._bits)

    @staticmethod
    def _decodificar(bits: list[int]) -> LecturaDHT22:
        def bits_a_byte(sub: list[int]) -> int:
            valor = 0
            for b in sub:
                valor = (valor << 1) | b
            return valor

        humedad_alta = bits_a_byte(bits[0:8])
        humedad_baja = bits_a_byte(bits[8:16])
        temp_alta = bits_a_byte(bits[16:24])
        temp_baja = bits_a_byte(bits[24:32])
        checksum_recibido = bits_a_byte(bits[32:40])

        checksum_calculado = (humedad_alta + humedad_baja + temp_alta + temp_baja) & 0xFF
        if checksum_calculado != checksum_recibido:
            raise DHT22ChecksumError(
                f"checksum invalido: recibido=0x{checksum_recibido:02X}, "
                f"calculado=0x{checksum_calculado:02X}"
            )

        humedad_pct = ((humedad_alta << 8) | humedad_baja) / 10.0

        signo = -1 if (temp_alta & 0x80) else 1
        temp_alta_sin_signo = temp_alta & 0x7F
        temperatura_c = signo * (((temp_alta_sin_signo << 8) | temp_baja) / 10.0)

        return LecturaDHT22(temperatura_c=temperatura_c, humedad_pct=humedad_pct)


class RastreadorTasaFallos:
    """Cuenta lecturas exitosas/fallidas para cuantificar el riesgo de
    timing en banco (README.md, seccion de validacion, item 6): compara
    la tasa de fallos de esta plataforma contra la ya conocida en la
    version ESP32 antes de dar viable esta ruta para este sensor.
    """

    def __init__(self, ventana: int = VENTANA_TASA_FALLOS):
        self._ventana = deque(maxlen=ventana)
        self.total_intentos = 0
        self.total_fallos = 0

    def registrar(self, exito: bool) -> None:
        self._ventana.append(exito)
        self.total_intentos += 1
        if not exito:
            self.total_fallos += 1

    def tasa_fallos_ventana(self) -> float:
        if not self._ventana:
            return 0.0
        fallos = sum(1 for exito in self._ventana if not exito)
        return fallos / len(self._ventana)

    def tasa_fallos_total(self) -> float:
        if self.total_intentos == 0:
            return 0.0
        return self.total_fallos / self.total_intentos

    def log_resumen_si_corresponde(self) -> None:
        if len(self._ventana) == self._ventana.maxlen:
            log.info(
                "tasa de fallos (ultimas %d lecturas): %.1f%% | acumulada (%d intentos): %.1f%%",
                self._ventana.maxlen,
                self.tasa_fallos_ventana() * 100,
                self.total_intentos,
                self.tasa_fallos_total() * 100,
            )


def leer_con_reintentos(
    reader: _DHT22PigpioReader,
    rastreador: RastreadorTasaFallos,
    max_reintentos: int = MAX_REINTENTOS,
) -> LecturaDHT22 | None:
    """Intenta leer el sensor, reintentando hasta `max_reintentos` veces.

    Cada intento (exitoso o no) se registra en `rastreador` para poder
    cuantificar la tasa de fallos real, en vez de solo ocultarla detras
    de los reintentos.
    """
    ultimo_error: Exception | None = None
    for intento in range(1, max_reintentos + 1):
        try:
            lectura = reader.leer_una_vez()
            rastreador.registrar(exito=True)
            return lectura
        except (DHT22TimeoutError, DHT22ChecksumError) as exc:
            ultimo_error = exc
            rastreador.registrar(exito=False)
            log.warning(
                "intento %d/%d fallido: %s", intento, max_reintentos, exc
            )
            if intento < max_reintentos:
                time.sleep(RETARDO_ENTRE_REINTENTOS_S)

    log.error(
        "lectura descartada tras %d intentos; ultimo error: %s",
        max_reintentos,
        ultimo_error,
    )
    return None


def main() -> None:
    pi = pigpio.pi()
    if not pi.connected:
        sys.exit(
            "ERROR: no se pudo conectar al daemon pigpiod. "
            "Iniciarlo con: sudo systemctl enable pigpiod --now "
            "(o sudo pigpiod para una sesion manual)."
        )

    reader = _DHT22PigpioReader(pi, DHT_GPIO)
    rastreador = RastreadorTasaFallos()

    print("timestamp_ms,temperatura_C,humedad_relativa_pct")
    try:
        while True:
            inicio_ciclo = time.monotonic()
            lectura = leer_con_reintentos(reader, rastreador)
            if lectura is not None:
                print(
                    f"{int(time.time() * 1000)},"
                    f"{lectura.temperatura_c:.1f},"
                    f"{lectura.humedad_pct:.1f}"
                )
            rastreador.log_resumen_si_corresponde()

            # Temporizacion del ciclo completo (lectura + reintentos ya
            # respetaron READ_INTERVAL_S entre si); se descuenta el
            # tiempo ya consumido para mantener el periodo total.
            transcurrido = time.monotonic() - inicio_ciclo
            time.sleep(max(0.0, READ_INTERVAL_S - transcurrido))
    except KeyboardInterrupt:
        log.info(
            "detenido por el usuario. Tasa de fallos final: %.1f%% (%d intentos)",
            rastreador.tasa_fallos_total() * 100,
            rastreador.total_intentos,
        )
    finally:
        pi.stop()


if __name__ == "__main__":
    main()

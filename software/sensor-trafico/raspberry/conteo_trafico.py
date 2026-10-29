#!/usr/bin/env python3
"""
Contador IR doble haz — lectura digital con debounce por software y
lógica de secuencia para conteo direccional (Raspberry Pi 4 Model B, 2GB)
KaabLab — conteo de tráfico de forrajeo en la piquera

Equivalente Python de ../arduino/ir_doble_haz_conteo/ir_doble_haz_conteo.ino. Replica la
MISMA lógica que la versión ESP32 (ver README.md, secciones 1-3, antes
de modificar este script):

    - 4 señales digitales leídas (Haz A principal/secundario, Haz B
      principal/secundario), una por módulo FC-51/KY-033.
    - Debounce por software: un cambio de estado solo se acepta como
      real si el nivel se mantiene estable durante DEBOUNCE_MS.
    - Lógica de secuencia direccional basada en las señales PRINCIPALES:
      Haz A interrumpido antes que Haz B -> entrada (A->B)
      Haz B interrumpido antes que Haz A -> salida  (B->A)
      con un timeout que descarta la secuencia si el segundo haz no se
      interrumpe a tiempo.
    - Las señales SECUNDARIAS solo se registran como diagnóstico, igual
      que en la versión Arduino.

ADVERTENCIA — DISEÑO NO CERRADO (idéntica a la del código Arduino, ver
README.md secciones 1, 2 y 5): la distancia mínima de detección
especificada de los módulos FC-51/KY-033 (20-300 mm) excede el diámetro
real del tubo de la piquera (~15 mm), y no hay mitigación integrada
contra falsos positivos por luz solar IR directa. Este script asume que
la validación de banco de la sección 5 del README ya se realizó. NO
instalar en campo sin esa validación — eso aplica igual en ambas
plataformas, es una limitación del sensor, no del código que lo lee.

---------------------------------------------------------------------
RIESGO ESPECÍFICO DE ESTA PLATAFORMA PARA ESTE SENSOR
---------------------------------------------------------------------
Contraste explícito con los otros dos scripts Python del proyecto (ver
docs/arquitectura-hardware/README.md, secciones 3.1-3.3):

- El sensor de sonido aéreo (I²S) usa un periférico de HARDWARE
  dedicado con DMA: no depende del scheduler de Linux para capturar
  cada muestra (ver ../../sensor-audio/raspberry/captura_inmp441.py).
- El sensor de vibración estructural (I²C) se lee por POLLING de
  software a alta tasa (1500 Hz): el riesgo ahí es no sostener esa
  tasa de forma estable (ver ../../sensor-vibracion/raspberry/lectura_mpu6500.py).
- **Este sensor es un caso distinto de ambos:** no se lee por polling
  de alta tasa ni por DMA de hardware, sino por **detección de eventos
  (interrupción) vía RPi.GPIO**, usando `add_event_detect()`. En
  Raspberry Pi/Linux, esas interrupciones NO son interrupciones de
  kernel en tiempo estricto: el evento se detecta en el kernel, pero el
  callback de Python se despacha en espacio de usuario a través de un
  hilo del intérprete, con latencia TÍPICA DEL ORDEN DE MILISEGUNDOS
  (no microsegundos, a diferencia de una interrupción real de
  microcontrolador bare-metal como la del ESP32).

**Consecuencia concreta para ESTE sensor:** la lógica de conteo
direccional (sección "Lógica de secuencia" arriba) depende del ORDEN
relativo en que se registran los callbacks del Haz A y del Haz B. Si
una abeja cruza el haz muy rápido (el tiempo real entre la interrupción
de un haz y el otro es menor que la latencia típica de milisegundos del
callback de Python), es posible que:

  - El orden de llegada de los callbacks a este script NO coincida con
    el orden real en que los haces se interrumpieron físicamente.
  - Esto invertiría la dirección detectada (una entrada real registrada
    como salida, o viceversa) — un **conteo direccional incorrecto**.
  - El **conteo total de cruces (sin dirección)** es mucho más robusto
    a este riesgo: cada interrupción de haz sigue generando un evento,
    solo el ORDEN relativo entre A y B es lo que puede degradarse.

**Esto queda marcado como pendiente de validación en banco, no como
diseño cerrado.** Antes de considerar esta plataforma viable para el
conteo DIRECCIONAL específicamente (el conteo total ya es más tolerante
a este riesgo), se requiere: comparar el conteo direccional (entradas/
salidas) que produce este script en Raspberry Pi contra el que produce
`../arduino/ir_doble_haz_conteo/ir_doble_haz_conteo.ino` en ESP32, usando el MISMO patrón
de cruces controlados (objeto o actuador mecánico cruzando ambos haces
a velocidad conocida y repetible) — ver README.md, sección 5.
---------------------------------------------------------------------

Pin mapping (Raspberry Pi 4 Model B, ver docs/arquitectura-hardware/README.md,
sección 4 — mapeo GPIO BCM equivalente al de ESP32 DevKit V1):
  Haz A — receptor principal    = GPIO5  (pin físico 29)
  Haz A — receptor secundario   = GPIO6  (pin físico 31)
  Haz B — receptor principal    = GPIO12 (pin físico 32)
  Haz B — receptor secundario   = GPIO13 (pin físico 33)

Librería: RPi.GPIO (pip install RPi.GPIO)
  Se eligió RPi.GPIO sobre gpiozero porque expone `add_event_detect()`
  con acceso directo al nivel del pin (`GPIO.input()`) dentro del
  callback, necesario para implementar el MISMO algoritmo de debounce
  por tiempo estable que la versión Arduino (sección "Debounce" más
  abajo) en vez de delegar en el debounce interno, distinto, de
  gpiozero/`Button` (que descarta eventos por tiempo transcurrido desde
  el último, no por estabilidad del nivel leído).

Requisitos del sistema antes de ejecutar:
  - Acceso a GPIO: ejecutar como usuario del grupo `gpio`, o con
    `sudo python3 conteo_trafico.py`.
"""

from __future__ import annotations

import sys
import threading
import time
from enum import Enum, auto

try:
    import RPi.GPIO as GPIO
except ImportError:
    sys.exit(
        "ERROR: falta la libreria RPi.GPIO. Instalar con: pip install RPi.GPIO\n"
        "       (solo funciona ejecutandose en una Raspberry Pi real)"
    )

# --- Pin mapping (ver docstring del modulo) ---
HAZ_A_PIN = 5
HAZ_A_SEC_PIN = 6
HAZ_B_PIN = 12
HAZ_B_SEC_PIN = 13

# Polaridad de salida de los modulos FC-51/KY-033: identica a la version
# Arduino (README.md seccion 3, "Polaridad configurable") — en la
# configuracion tipica, OUT permanece en HIGH con el haz intacto y baja
# a LOW cuando el haz se interrumpe. CONFIRMAR EN BANCO antes de confiar
# en esta constante (mismo punto pendiente que en la version ESP32).
BEAM_BROKEN_LEVEL = GPIO.LOW

# --- Debounce por software (ver README.md seccion 3, misma logica que Arduino) ---
# A diferencia del bucle de polling continuo del firmware ESP32 (que
# revisa "(now - lastChangeMs) >= DEBOUNCE_MS" en cada iteracion), este
# script es dirigido por eventos (add_event_detect): el debounce se
# implementa con un temporizador re-disparable (threading.Timer) por
# cada pin -- cada flanco nuevo cancela el temporizador anterior y arma
# uno nuevo; el cambio de estado solo se acepta como "estable" si el
# temporizador llega a disparar sin que haya llegado un flanco mas
# reciente. Es la traduccion mas fiel posible del mismo criterio
# ("estable durante DEBOUNCE_MS") a un modelo dirigido por eventos.
#
# Deliberadamente NO se usa el parametro `bouncetime` propio de
# `add_event_detect()`: ese mecanismo es distinto (descarta eventos por
# tiempo transcurrido desde el ultimo evento, no por estabilidad del
# nivel), y mezclar ambos complicaria comparar resultados 1:1 contra la
# version Arduino.
DEBOUNCE_S = 0.015  # 15 ms, igual que DEBOUNCE_MS en Arduino

SEQUENCE_TIMEOUT_S = 0.300  # 300 ms, igual que SEQUENCE_TIMEOUT_MS en Arduino


class SequenceState(Enum):
    IDLE = auto()
    A_FIRST = auto()
    B_FIRST = auto()


class DebouncedPin:
    """Traduccion a modelo por eventos del struct DebouncedPin de Arduino."""

    def __init__(self, gpio_pin: int, name: str):
        self.gpio_pin = gpio_pin
        self.name = name
        self.stable_state = GPIO.HIGH
        self._timer: threading.Timer | None = None

    def arm_debounce(self, on_stable_change) -> None:
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(DEBOUNCE_S, self._confirm, args=(on_stable_change,))
        self._timer.daemon = True
        self._timer.start()

    def _confirm(self, on_stable_change) -> None:
        raw = GPIO.input(self.gpio_pin)
        if raw != self.stable_state:
            self.stable_state = raw
            on_stable_change(self)


class TrafficCounter:
    """Logica de secuencia direccional -- equivalente al loop() de Arduino."""

    def __init__(self) -> None:
        self.seq_state = SequenceState.IDLE
        self.count_entradas = 0
        self.count_salidas = 0
        self._lock = threading.Lock()
        self._timeout_timer: threading.Timer | None = None

    def _start_sequence(self, new_state: SequenceState) -> None:
        self.seq_state = new_state
        if self._timeout_timer is not None:
            self._timeout_timer.cancel()
        self._timeout_timer = threading.Timer(
            SEQUENCE_TIMEOUT_S, self._on_sequence_timeout, args=(new_state,)
        )
        self._timeout_timer.daemon = True
        self._timeout_timer.start()

    def _on_sequence_timeout(self, expected_state: SequenceState) -> None:
        with self._lock:
            if self.seq_state == expected_state:
                self.seq_state = SequenceState.IDLE
                print(
                    f"# secuencia descartada por timeout ({int(SEQUENCE_TIMEOUT_S * 1000)} ms)",
                    file=sys.stderr,
                )

    def _print_event(self, evento: str) -> None:
        now_ms = time.monotonic_ns() // 1_000_000
        print(f"{now_ms},{evento},{self.count_entradas},{self.count_salidas}")

    def on_haz_a_changed(self, beam: DebouncedPin) -> None:
        with self._lock:
            broken = beam.stable_state == BEAM_BROKEN_LEVEL
            if not broken:
                return
            if self.seq_state == SequenceState.IDLE:
                self._start_sequence(SequenceState.A_FIRST)
            elif self.seq_state == SequenceState.B_FIRST:
                # B se interrumpio primero, ahora A -> salida (B->A)
                self.count_salidas += 1
                self._print_event("salida")
                self.seq_state = SequenceState.IDLE
                if self._timeout_timer is not None:
                    self._timeout_timer.cancel()

    def on_haz_b_changed(self, beam: DebouncedPin) -> None:
        with self._lock:
            broken = beam.stable_state == BEAM_BROKEN_LEVEL
            if not broken:
                return
            if self.seq_state == SequenceState.IDLE:
                self._start_sequence(SequenceState.B_FIRST)
            elif self.seq_state == SequenceState.A_FIRST:
                # A se interrumpio primero, ahora B -> entrada (A->B)
                self.count_entradas += 1
                self._print_event("entrada")
                self.seq_state = SequenceState.IDLE
                if self._timeout_timer is not None:
                    self._timeout_timer.cancel()

    def on_haz_a_sec_changed(self, beam: DebouncedPin) -> None:
        # Registro diagnostico: no participa en la logica de conteo,
        # igual que en la version Arduino (README.md secciones 3 y 5).
        now_ms = time.monotonic_ns() // 1_000_000
        estado = "interrumpido" if beam.stable_state == BEAM_BROKEN_LEVEL else "intacto"
        print(f"{now_ms},diag_haz_A_secundario={estado}", file=sys.stderr)

    def on_haz_b_sec_changed(self, beam: DebouncedPin) -> None:
        now_ms = time.monotonic_ns() // 1_000_000
        estado = "interrumpido" if beam.stable_state == BEAM_BROKEN_LEVEL else "intacto"
        print(f"{now_ms},diag_haz_B_secundario={estado}", file=sys.stderr)


def main() -> None:
    GPIO.setmode(GPIO.BCM)
    # Sin pull-up/down interno: los modulos FC-51/KY-033 entregan una
    # salida digital ya acondicionada (push-pull) por su comparador
    # LM393 interno, igual que asume la version Arduino (pinMode INPUT
    # simple, sin INPUT_PULLUP).
    for pin in (HAZ_A_PIN, HAZ_A_SEC_PIN, HAZ_B_PIN, HAZ_B_SEC_PIN):
        GPIO.setup(pin, GPIO.IN)

    counter = TrafficCounter()
    beam_a = DebouncedPin(HAZ_A_PIN, "haz_A")
    beam_a_sec = DebouncedPin(HAZ_A_SEC_PIN, "haz_A_secundario")
    beam_b = DebouncedPin(HAZ_B_PIN, "haz_B")
    beam_b_sec = DebouncedPin(HAZ_B_SEC_PIN, "haz_B_secundario")

    GPIO.add_event_detect(
        HAZ_A_PIN, GPIO.BOTH, callback=lambda ch: beam_a.arm_debounce(counter.on_haz_a_changed)
    )
    GPIO.add_event_detect(
        HAZ_A_SEC_PIN,
        GPIO.BOTH,
        callback=lambda ch: beam_a_sec.arm_debounce(counter.on_haz_a_sec_changed),
    )
    GPIO.add_event_detect(
        HAZ_B_PIN, GPIO.BOTH, callback=lambda ch: beam_b.arm_debounce(counter.on_haz_b_changed)
    )
    GPIO.add_event_detect(
        HAZ_B_SEC_PIN,
        GPIO.BOTH,
        callback=lambda ch: beam_b_sec.arm_debounce(counter.on_haz_b_sec_changed),
    )

    print(
        "# Contador IR doble haz iniciado (Raspberry Pi, deteccion por eventos RPi.GPIO)",
        file=sys.stderr,
    )
    print(
        "# ADVERTENCIA: conteo direccional sujeto a riesgo de orden de eventos -- "
        "ver docstring del modulo y docs/arquitectura-hardware/README.md seccion 3.3",
        file=sys.stderr,
    )
    print("timestamp_ms,evento,total_entradas,total_salidas")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()

"""Generador de tráfico de piquera (sensor IR doble haz, conteo direccional).
Simula conteos de entradas y salidas agregados por intervalo a lo largo de un
ciclo diurno (ver software/sensor-trafico/README.md: secuencia Haz A->B =
entrada, Haz B->A = salida, agregación típica cada 5 minutos).

Los parámetros por clase (nivel de actividad, sobredispersión, eventos
erráticos) son un supuesto de diseño propio, sin respaldo en literatura
publicada: no existe precedente de conteo IR bidireccional en M. beecheii ni
en ningún congénere con esta granularidad -- gap documentado en
thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md, sección
1.1.5d (el único precedente parcial, Justino y Hartfelder 2024 en
M. quadrifasciata, registra actividad continua sin diferenciar dirección)."""
import numpy as np
from .. import config as C

_LEVEL = {"sana": 1.0, "sin_reina": 0.80, "estres": 0.90}         # sin_reina: forrajeo/reclutamiento reducido
_OVERDISP_SHAPE = {"sana": 4.0, "sin_reina": 4.0, "estres": 1.8}  # estres: mayor sobredispersión (patrón errático), resto con algo de base

def _diurnal_shape(hour):
    """Pico de actividad de forrajeo ~10-16h, nula durante la noche."""
    return np.clip(np.sin(np.pi * np.clip((hour - 6.0) / 12.0, 0, 1)), 0, None)

def _counts(base_rate, shape_param, rng):
    gamma_factor = rng.gamma(shape_param, 1.0 / shape_param, size=base_rate.shape)
    base_rate = base_rate * gamma_factor
    return rng.poisson(np.clip(base_rate, 0, None))

def generate_traffic(label, rng):
    w = C.TRAFFIC_WINDOW
    hour = np.linspace(0, 24, w, endpoint=False)
    base_rate = (C.TRAFFIC_PEAK_RATE * _LEVEL[label] * (1 + rng.normal(0, 0.25))
                 * _diurnal_shape(hour))

    # picos/caídas abruptos superpuestos (perturbación/intrusión): más probables en
    # estrés, pero no exclusivos -- ocasionalmente ocurren en las otras clases también
    n_events = rng.poisson(2.6 if label == "estres" else 0.5)
    for _ in range(n_events):
        i = rng.integers(0, w)
        half = rng.integers(1, 4)
        lo, hi = max(0, i - half), min(w, i + half)
        factor = rng.choice([rng.uniform(1.6, 2.4), rng.uniform(0.15, 0.5)])
        base_rate[lo:hi] *= factor

    entradas = _counts(base_rate, _OVERDISP_SHAPE[label], rng)
    salidas = _counts(base_rate, _OVERDISP_SHAPE[label], rng)
    return dict(entradas=entradas.astype(np.float64), salidas=salidas.astype(np.float64))

"""Generador de series ambientales (DHT22 + SHT31).
El ambiente identifica sobre todo a 'sin_reina' (humedad elevada) -> sustenta H1b."""
import numpy as np
from .. import config as C

_RH = {"sana": 78.0, "sin_reina": 89.0, "estres": 80.0}
_TVAR = {"sana": 0.5, "sin_reina": 0.5, "estres": 0.9}

def generate_env(label, rng):
    w = C.ENV_WINDOW
    tt = np.linspace(0, 1, w)
    base_T = 30.0 + rng.normal(0, 0.4)
    true_T = base_T + 1.5 * np.sin(2 * np.pi * tt) + rng.normal(0, _TVAR[label], w)
    true_RH = _RH[label] + 3.0 * np.cos(2 * np.pi * tt) + rng.normal(0, 4.0, w)
    true_RH = np.clip(true_RH, 40, 99)
    sht_T = true_T + rng.normal(0, 0.2, w)
    sht_RH = true_RH + rng.normal(0, 1.0, w)
    dht_T = true_T + rng.normal(0, 0.5, w) + 0.3
    dht_RH = np.minimum(true_RH, C.DHT22_SAT) + rng.normal(0, 2.0, w)
    dht_RH = np.clip(dht_RH, 0, C.DHT22_SAT + 1)
    return dict(dht_T=dht_T, dht_RH=dht_RH, sht_T=sht_T, sht_RH=sht_RH)

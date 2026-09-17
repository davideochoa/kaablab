"""Generador de vibración estructural (MPU6050, 1-50 Hz).
La vibración identifica sobre todo a 'estres' (amplitud intensificada) -> sustenta H1a."""
import numpy as np
from .. import config as C

_GAIN = {"sana": 1.0, "sin_reina": 1.1, "estres": 2.4}

def generate_vibration(label, rng):
    n = int(C.FS_VIB * C.DUR_VIB)
    t = np.arange(n) / C.FS_VIB
    g = _GAIN[label] * (1 + rng.normal(0, 0.12))
    sig = g * (0.6 * np.sin(2 * np.pi * 6 * t) + 0.4 * np.sin(2 * np.pi * 13 * t))
    if label == "estres":
        sig += 0.7 * np.sin(2 * np.pi * 36 * t)
    sig += rng.normal(0, 0.08, n)
    return sig.astype(np.float32)

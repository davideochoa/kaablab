"""Generador de vibración estructural (MPU6500, banda de interés 180-600 Hz).
Componentes con fundamento físico: vuelo ~180-250 Hz (Hrncir et al., 2008) y
forrajeo/reclutamiento con fundamental ~300-600 Hz (Hrncir et al., 2000, 2006a; ver
thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md, 1.1.5e).
Con FS_VIB = 1500 Hz (Nyquist 750 Hz, margen 1.25x sobre los 600 Hz) toda la
banda de interés es capturable sin recorte; los componentes 220/380/460 Hz caen
dentro de ella. La vibración
identifica sobre todo a 'estres' (amplitud intensificada) -> sustenta H1a."""
import numpy as np
from .. import config as C

_GAIN = {"sana": 1.0, "sin_reina": 1.1, "estres": 2.4}

def generate_vibration(label, rng):
    n = int(C.FS_VIB * C.DUR_VIB)
    t = np.arange(n) / C.FS_VIB
    g = _GAIN[label] * (1 + rng.normal(0, 0.12))
    f_vuelo = 220.0 * (1 + rng.normal(0, 0.05))       # componente de vuelo, 180-250 Hz
    f_forrajeo = 380.0 * (1 + rng.normal(0, 0.05))    # fundamental de forrajeo, dentro de 300-600 Hz
    sig = g * (0.6 * np.sin(2 * np.pi * f_vuelo * t) + 0.4 * np.sin(2 * np.pi * f_forrajeo * t))
    if label == "estres":
        f_estres = 460.0 * (1 + rng.normal(0, 0.05))  # armónico adicional, dentro de 300-600 Hz
        sig += 0.7 * np.sin(2 * np.pi * f_estres * t)
    sig += rng.normal(0, 0.08, n)
    return sig.astype(np.float32)

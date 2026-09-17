"""Generador de vibración estructural (MPU6050, banda de interés 180-500 Hz).
Componentes con fundamento físico: vuelo ~180-250 Hz y forrajeo/reclutamiento
con fundamental ~300-600 Hz (Hrncir et al., 2000/2006/2008; ver
thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md, 1.1.5e).
El componente de forrajeo se limita a <=500 Hz porque el Nyquist real del
canal de aceleración del MPU6050 (ADC interno fijo a ~1 kHz, independiente de
SMPLRT_DIV) es ~500 Hz, no 600 Hz (ver software/sensor-vibracion/README.md,
sección 2.2). La vibración identifica sobre todo a 'estres' (amplitud
intensificada) -> sustenta H1a."""
import numpy as np
from .. import config as C

_GAIN = {"sana": 1.0, "sin_reina": 1.1, "estres": 2.4}

def generate_vibration(label, rng):
    n = int(C.FS_VIB * C.DUR_VIB)
    t = np.arange(n) / C.FS_VIB
    g = _GAIN[label] * (1 + rng.normal(0, 0.12))
    f_vuelo = 220.0 * (1 + rng.normal(0, 0.05))       # componente de vuelo, 180-250 Hz
    f_forrajeo = 380.0 * (1 + rng.normal(0, 0.05))    # fundamental de forrajeo, dentro de 300-500 Hz
    sig = g * (0.6 * np.sin(2 * np.pi * f_vuelo * t) + 0.4 * np.sin(2 * np.pi * f_forrajeo * t))
    if label == "estres":
        f_estres = 460.0 * (1 + rng.normal(0, 0.05))  # armónico adicional, dentro del techo de 500 Hz
        sig += 0.7 * np.sin(2 * np.pi * f_estres * t)
    sig += rng.normal(0, 0.08, n)
    return sig.astype(np.float32)

"""Generador de señal acústica sintética por clase (INMP441).
Diferencias acústicas débiles/ruidosas entre clases, para que el ambiente y la
vibración aporten información complementaria (experimentos de ablación H1a/H1b)."""
import numpy as np
from .. import config as C

_PROFILE = {
    "sana":      dict(f0=250, nharm=6, decay=0.60, hi_emph=0.04, noise=0.075, bursts=0),
    "sin_reina": dict(f0=250, nharm=6, decay=0.58, hi_emph=0.09, noise=0.075, bursts=0),
    "estres":    dict(f0=250, nharm=6, decay=0.60, hi_emph=0.05, noise=0.085, bursts=4),
}

def generate_audio(label, rng):
    p = _PROFILE[label]
    n = int(C.FS_AUDIO * C.DUR_AUDIO)
    t = np.arange(n) / C.FS_AUDIO
    f0 = p["f0"] * (1 + rng.normal(0, 0.08))
    sig = np.zeros(n)
    for k in range(1, p["nharm"] + 1):
        amp = (p["decay"] ** k) * (1 + rng.normal(0, 0.12))
        sig += amp * np.sin(2 * np.pi * f0 * k * t + rng.uniform(0, 2 * np.pi))
    fhi = 2200 * (1 + rng.normal(0, 0.06))
    sig += p["hi_emph"] * (1 + rng.normal(0, 0.3)) * np.sin(2 * np.pi * fhi * t)
    for _ in range(p["bursts"]):
        i = rng.integers(0, n - 200)
        sig[i:i + 200] += rng.normal(0, 0.35, 200) * np.hanning(200)
    sig += rng.normal(0, p["noise"], n)
    sig /= (np.max(np.abs(sig)) + 1e-9)
    return sig.astype(np.float32)

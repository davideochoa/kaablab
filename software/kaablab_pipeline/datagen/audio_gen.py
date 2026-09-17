"""Generador de señal acústica sintética por clase (INMP441).
Diferencias acústicas débiles/ruidosas entre clases, para que el ambiente y la
vibración aporten información complementaria (experimentos de ablación H1a/H1b)."""
import numpy as np
from .. import config as C

_PROFILE = {
    "sana":      dict(f0=250, nharm=6, decay=0.600, hi_emph=0.060, noise=0.115, burst_lambda=0.35),
    "sin_reina": dict(f0=250, nharm=6, decay=0.588, hi_emph=0.072, noise=0.120, burst_lambda=0.55),
    "estres":    dict(f0=250, nharm=6, decay=0.596, hi_emph=0.066, noise=0.125, burst_lambda=1.5),
}

def generate_audio(label, rng):
    p = _PROFILE[label]
    n = int(C.FS_AUDIO * C.DUR_AUDIO)
    t = np.arange(n) / C.FS_AUDIO
    f0 = p["f0"] * (1 + rng.normal(0, 0.20))
    sig = np.zeros(n)
    for k in range(1, p["nharm"] + 1):
        amp = (p["decay"] ** k) * (1 + rng.normal(0, 0.30))
        sig += amp * np.sin(2 * np.pi * f0 * k * t + rng.uniform(0, 2 * np.pi))
    fhi = 2200 * (1 + rng.normal(0, 0.06))
    sig += p["hi_emph"] * (1 + rng.normal(0, 0.55)) * np.sin(2 * np.pi * fhi * t)
    # bursts no deterministicos: conteo por Poisson (media distinta por clase, con traslape)
    n_bursts = rng.poisson(p["burst_lambda"])
    for _ in range(n_bursts):
        i = rng.integers(0, n - 200)
        amp_b = rng.uniform(0.15, 0.40)
        sig[i:i + 200] += rng.normal(0, amp_b, 200) * np.hanning(200)
    sig += rng.normal(0, p["noise"], n)
    sig *= (1 + rng.normal(0, 0.12))
    sig /= (np.max(np.abs(sig)) + 1e-9)
    return sig.astype(np.float32)

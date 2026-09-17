"""Extracción de descriptores de vibración (MPU6050)."""
import numpy as np
from scipy.fft import rfft, rfftfreq
from .. import config as C

_F = rfftfreq(int(C.FS_VIB * C.DUR_VIB), 1.0 / C.FS_VIB)

def extract_vibration(sig):
    mag = np.abs(rfft(sig))
    def band(lo, hi):
        m = (_F >= lo) & (_F < hi)
        return float(np.sum(mag[m] ** 2))
    dom = float(_F[np.argmax(mag)])
    return dict(
        vib_rms=float(np.sqrt(np.mean(sig ** 2))),
        vib_dom_freq=dom,
        vib_e_1_10=band(1, 10),
        vib_e_10_30=band(10, 30),
        vib_e_30_50=band(30, 50),
        vib_var=float(np.var(sig)),
    )

"""Extracción de descriptores de vibración (MPU6500)."""
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
        vib_e_150_250=band(150, 250),   # vuelo (~180 Hz, con margen)
        vib_e_250_400=band(250, 400),   # transición / armónicos bajos de forrajeo
        vib_e_400_600=band(400, 600),   # forrajeo intenso, hasta 600 Hz (Nyquist = 750 Hz)
        vib_var=float(np.var(sig)),
    )

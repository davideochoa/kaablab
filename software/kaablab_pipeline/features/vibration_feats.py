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
        vib_e_150_250=band(150, 250),   # vuelo (180-250 Hz, con margen)
        vib_e_250_400=band(250, 400),   # transición / armónicos bajos de forrajeo
        vib_e_400_500=band(400, 500),   # forrajeo intenso, techo por Nyquist real (~500 Hz)
        vib_var=float(np.var(sig)),
    )

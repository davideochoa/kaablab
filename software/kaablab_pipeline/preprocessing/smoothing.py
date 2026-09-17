"""Etapa 3: filtro de media móvil sobre variables ambientales."""
import numpy as np
from .. import config as C

def moving_average(x, w=None):
    w = w or C.MA_WINDOW
    kernel = np.ones(w) / w
    return np.convolve(x, kernel, mode="same")

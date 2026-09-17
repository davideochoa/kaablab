"""Generador de series ambientales (DHT22 + SHT31).
Modela termoconformidad real (Moo-Valle et al., 2000; ver
thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md, 1.1.5b):
la temperatura interna se mantiene cerca de un punto estable durante el día
(9:00-20:00h) y converge parcialmente hacia la externa durante la noche,
cuando las obreras no generan calor activamente para compensar el descenso
ambiental. El contraste interno-externo resultante no es ruido de sensor
independiente: es una señal que varía de forma predecible con la hora del
día (mayor de noche -el externo cae más rápido de lo que el interno lo
sigue-, menor de día -ambos rondan valores cercanos-).
El ambiente identifica sobre todo a 'sin_reina' (humedad elevada) -> sustenta H1b."""
import numpy as np
from .. import config as C

_RH = {"sana": 78.0, "sin_reina": 89.0, "estres": 80.0}
_TVAR = {"sana": 0.5, "sin_reina": 0.5, "estres": 0.9}

_DAY_START, _DAY_END = 9.0, 20.0   # horario diurno documentado (Moo-Valle et al., 2000)
_TRANS_H = 1.5                      # ancho de la transición día/noche (horas), para evitar escalones
_NIGHT_WEIGHT_MAX = 0.5             # convergencia parcial (no total) del interno hacia el externo de noche

def _smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

def _day_indicator(hour):
    """~1 durante 9:00-20:00h, ~0 de noche, con transición suave en los bordes."""
    rise = _smoothstep((hour - (_DAY_START - _TRANS_H)) / _TRANS_H)
    fall = _smoothstep(((_DAY_END + _TRANS_H) - hour) / _TRANS_H)
    return np.clip(rise * fall, 0, 1)

def generate_env(label, rng):
    w = C.ENV_WINDOW
    tt = np.linspace(0, 1, w)          # una ventana = un ciclo diurno completo (24h)
    hour = tt * 24.0
    day_ind = _day_indicator(hour)
    night_weight = _NIGHT_WEIGHT_MAX * (1.0 - day_ind)

    # --- Temperatura externa (DHT22): oscilación diurna completa del clima de Campeche ---
    T_ext_day = 31.5 + rng.normal(0, 0.3)
    T_ext_night = 26.5 + rng.normal(0, 0.3)
    true_T_ext = day_ind * T_ext_day + (1.0 - day_ind) * T_ext_night + rng.normal(0, 0.7, w)

    # --- Temperatura interna (SHT31): estable de día, blend hacia la externa de noche ---
    stable_point = 30.2 + rng.normal(0, 0.3)   # media documentada (Moo-Valle et al., 2000)
    true_T_int = ((1.0 - night_weight) * stable_point + night_weight * true_T_ext
                  + rng.normal(0, _TVAR[label], w))

    true_RH = _RH[label] + 3.0 * np.cos(2 * np.pi * tt) + rng.normal(0, 4.0, w)
    true_RH = np.clip(true_RH, 40, 99)

    sht_T = true_T_int + rng.normal(0, 0.2, w)
    sht_RH = true_RH + rng.normal(0, 1.0, w)
    dht_T = true_T_ext + rng.normal(0, 0.5, w) + 0.3
    dht_RH = np.minimum(true_RH, C.DHT22_SAT) + rng.normal(0, 2.0, w)
    dht_RH = np.clip(dht_RH, 0, C.DHT22_SAT + 1)
    return dict(dht_T=dht_T, dht_RH=dht_RH, sht_T=sht_T, sht_RH=sht_RH)

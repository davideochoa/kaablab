"""Etapas 1-2: conversión HR->humedad absoluta (Magnus) y fusión ponderada por confianza."""
import numpy as np
from .. import config as C

def magnus_abs_humidity(T_c, RH):
    """Humedad absoluta (g/m3) a partir de temperatura (C) y HR (%). Fórmula de Magnus."""
    es = 6.112 * np.exp(17.62 * T_c / (243.12 + T_c))
    e = (RH / 100.0) * es
    return 2.1674 * (e * 100.0) / (273.15 + T_c)

def confidence_weighted_fusion(env):
    """Fusiona DHT22 y SHT31; el peso del DHT22 cae al acercarse a su saturación."""
    dht_RH = env["dht_RH"]
    w_dht = 1.0 / (1.0 + np.exp((dht_RH - C.FUSION_KNEE) / 1.5))
    w_sht = 1.0 - w_dht
    fused_T = w_dht * env["dht_T"] + w_sht * env["sht_T"]
    ah_dht = magnus_abs_humidity(env["dht_T"], env["dht_RH"])
    ah_sht = magnus_abs_humidity(env["sht_T"], env["sht_RH"])
    fused_AH = w_dht * ah_dht + w_sht * ah_sht
    return fused_T, fused_AH

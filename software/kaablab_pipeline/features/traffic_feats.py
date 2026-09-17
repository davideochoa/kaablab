"""Extracción de descriptores de tráfico en piquera (sensor IR doble haz)."""
import numpy as np

def extract_traffic(traffic):
    entradas, salidas = traffic["entradas"], traffic["salidas"]
    neta = entradas - salidas
    return dict(
        trf_entradas_mean=float(entradas.mean()),
        trf_entradas_std=float(entradas.std()),
        trf_salidas_mean=float(salidas.mean()),
        trf_salidas_std=float(salidas.std()),
        trf_neta_mean=float(neta.mean()),
        trf_neta_std=float(neta.std()),
    )

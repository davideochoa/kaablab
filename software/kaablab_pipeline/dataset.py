"""Orquesta generación + preprocesamiento + extracción -> tabla de características."""
import numpy as np, pandas as pd
from . import config as C
from .datagen.audio_gen import generate_audio
from .datagen.env_gen import generate_env
from .datagen.vibration_gen import generate_vibration
from .datagen.traffic_gen import generate_traffic
from .preprocessing.audio_prep import pre_emphasis
from .preprocessing.env_fusion import confidence_weighted_fusion
from .preprocessing.smoothing import moving_average
from .features.acoustic_feats import extract_acoustic
from .features.vibration_feats import extract_vibration
from .features.traffic_feats import extract_traffic

ENV_COLS = ["env_T_mean", "env_AH_mean", "env_T_std", "env_AH_std"]
VIB_COLS = ["vib_rms", "vib_dom_freq", "vib_e_150_250", "vib_e_250_400", "vib_e_400_600", "vib_var"]
TRAFFIC_COLS = ["trf_entradas_mean", "trf_entradas_std", "trf_salidas_mean",
                "trf_salidas_std", "trf_neta_mean", "trf_neta_std"]

def build_dataset(seed=None):
    rng = np.random.default_rng(C.SEED if seed is None else seed)
    rows, labels = [], []
    for label in C.CLASSES:
        for _ in range(C.N_PER_CLASS):
            audio = generate_audio(label, rng)
            env = generate_env(label, rng)
            vib = generate_vibration(label, rng)
            traffic = generate_traffic(label, rng)
            audio_p = pre_emphasis(audio)                        # etapa 4
            fused_T, fused_AH = confidence_weighted_fusion(env)  # etapas 1-2
            fused_T = moving_average(fused_T)                    # etapa 3
            fused_AH = moving_average(fused_AH)
            feat = extract_acoustic(audio_p)                     # etapa 5 (gate RMS) interna
            feat.update(extract_vibration(vib))
            feat.update(extract_traffic(traffic))
            feat.update(env_T_mean=float(fused_T.mean()), env_AH_mean=float(fused_AH.mean()),
                        env_T_std=float(fused_T.std()), env_AH_std=float(fused_AH.std()))
            rows.append(feat); labels.append(label)
    X = pd.DataFrame(rows)
    y = pd.Series(labels, name="clase")
    return X, y

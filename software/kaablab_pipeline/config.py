"""Parámetros centralizados del pipeline KaabLab (prototipo con datos sintéticos)."""
SEED = 42
CLASSES = ["sana", "sin_reina", "estres"]
N_PER_CLASS = 220

# --- Audio (INMP441) ---
FS_AUDIO = 16000
DUR_AUDIO = 1.0
N_MFCC = 13
N_MELS = 26
N_FFT = 512
HOP = 256
PREEMPH = 0.97
RMS_GATE_PCTL = 15

# --- Ambiental (DHT22 + SHT31) ---
ENV_WINDOW = 60
DHT22_SAT = 85.0
FUSION_KNEE = 82.0
MA_WINDOW = 5

# --- Vibración (MPU6050) ---
FS_VIB = 200
DUR_VIB = 2.0

# --- Modelo / evaluación ---
TEST_SIZE = 0.30
XGB_PARAMS = dict(n_estimators=300, max_depth=4, learning_rate=0.05,
                  subsample=0.9, colsample_bytree=0.9,
                  objective="multi:softprob", eval_metric="mlogloss",
                  tree_method="hist", random_state=SEED)
THRESHOLDS = dict(auc_roc=0.85, f1=0.80)

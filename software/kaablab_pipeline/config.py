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

# --- Tráfico piquera (IR doble haz) ---
TRAFFIC_WINDOW = 60     # una ventana = un ciclo diurno completo (24h), igual que ENV_WINDOW
TRAFFIC_PEAK_RATE = 8.0  # eventos/intervalo en el pico de actividad; valor de diseño, no
                         # calibrado con datos reales (gap documentado, sección 1.1.5d)

# --- Vibración (MPU6050) ---
# Banda de interés real: vuelo ~180-250 Hz, forrajeo/reclutamiento con
# fundamental ~300-600 Hz (Hrncir et al., 2000/2006/2008; ver
# thesis/capitulo-1-antecedentes-planteamiento-objetivos/capitulo-1.md, 1.1.5e).
# FS_VIB = 1000 Hz replica la tasa real de actualización interna del ADC del
# acelerómetro del MPU6050 (~1 kHz fijo, independiente de SMPLRT_DIV; ver
# software/sensor-vibracion/README.md, sección 2.2), lo que fija el Nyquist
# real en 500 Hz -> techo efectivo de la banda capturable, no 600 Hz.
FS_VIB = 1000
DUR_VIB = 2.0

# --- Modelo / evaluación ---
TEST_SIZE = 0.30
XGB_PARAMS = dict(n_estimators=300, max_depth=4, learning_rate=0.05,
                  subsample=0.9, colsample_bytree=0.9,
                  objective="multi:softprob", eval_metric="mlogloss",
                  tree_method="hist", random_state=SEED)
THRESHOLDS = dict(auc_roc=0.85, f1=0.80)

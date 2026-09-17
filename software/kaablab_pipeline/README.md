# KaabLab — Pipeline de validación con datos sintéticos

Prototipo ejecutable de extremo a extremo del pipeline AIoT de KaabLab para
clasificación del estado de salud de colonias de *Melipona beecheii*
(clases: `sana`, `sin_reina`, `estres`). Usa **datos sintéticos fundamentados**
para validar que la arquitectura es correcta y capaz de aprender, antes de la
recolección en campo.

> Alcance: las etiquetas se asignan por construcción durante la generación.
> Las métricas validan la **arquitectura del pipeline**, no constituyen un
> resultado biológico sobre la especie.

## Estructura modular
```
kaablab/
├── config.py              # parámetros centralizados
├── datagen/               # generación sintética
│   ├── audio_gen.py       #   señal acústica (INMP441)
│   ├── env_gen.py         #   series ambientales (DHT22 + SHT31)
│   └── vibration_gen.py   #   vibración estructural (MPU6050)
├── preprocessing/         # protocolo de 5 etapas
│   ├── env_fusion.py      #   1) Magnus HR->HA  2) fusión ponderada por confianza
│   ├── smoothing.py       #   3) media móvil
│   └── audio_prep.py      #   4) pre-énfasis   5a) gate de energía RMS
├── features/
│   ├── acoustic_feats.py  #   13 MFCC + ZCR + centroide + rolloff
│   └── vibration_feats.py #   RMS, frecuencia dominante, energía por banda
├── dataset.py             # genera+preprocesa+extrae -> tabla de características
├── models/train_health.py # clasificador XGBoost (Gradient Boosting)
├── evaluation/metrics.py  # AUC-ROC (OvR macro), F1 macro, matriz de confusión
└── main.py                # orquesta el flujo + ablación + verificación de umbrales
```
La etapa 5b (normalización Z-score) se aplica en `main.py` con `StandardScaler`.

## Uso
```bash
pip install -r requirements.txt
python -m kaablab.main
```
Genera `dataset_sintetico.csv` y `resultados.json`, e imprime el reporte.

## Migración a datos reales
La modularidad permite sustituir únicamente `dataset.py` (o `datagen/`) por un
cargador de los datos de campo; el resto del flujo (preprocesamiento, features,
modelo, evaluación) permanece intacto.

## Experimentos de ablación
- **H1b** — con vs. sin fusión ambiental: mide el aporte de la arquitectura
  sensorial heterogénea (DHT22+SHT31).
- **H1a** — con vs. sin descriptores de vibración: mide el aporte del MPU6050.

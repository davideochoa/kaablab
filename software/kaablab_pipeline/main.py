"""Pipeline KaabLab — validación de arquitectura con datos sintéticos (extremo a extremo)."""
import json, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from . import config as C
from .dataset import build_dataset, ENV_COLS, VIB_COLS
from .models.train_health import train_health
from .evaluation.metrics import evaluate

def _run(X, y):
    y_codes = np.array([C.CLASSES.index(c) for c in y])   # XGBoost requiere enteros
    Xtr, Xte, ytr, yte = train_test_split(
        X, y_codes, test_size=C.TEST_SIZE, stratify=y_codes, random_state=C.SEED)
    sc = StandardScaler().fit(Xtr)                     # etapa 5: normalización Z-score
    Xtr = pd.DataFrame(sc.transform(Xtr), columns=X.columns)
    Xte = pd.DataFrame(sc.transform(Xte), columns=X.columns)
    model = train_health(Xtr, ytr)
    return evaluate(model, Xte, yte, C.CLASSES)

def main(save_dir="."):
    np.random.seed(C.SEED)
    print("== KaabLab :: prototipo de validación con datos sintéticos ==")
    print(f"Generando dataset: {len(C.CLASSES)} clases x {C.N_PER_CLASS} = "
          f"{len(C.CLASSES)*C.N_PER_CLASS} muestras...")
    X, y = build_dataset()
    full = X.copy(); full["clase"] = y.values
    full.to_csv(f"{save_dir}/dataset_sintetico.csv", index=False)
    print(f"Dataset guardado: dataset_sintetico.csv  ({X.shape[0]} filas, {X.shape[1]} características)")

    res = _run(X, y)
    print("\n--- Modelo completo (todas las características) ---")
    print(f"AUC-ROC (OvR macro): {res['auc_roc']:.3f}   F1 (macro): {res['f1']:.3f}")
    print("Matriz de confusión [filas=real, cols=pred] orden", C.CLASSES)
    print(res["confusion"])
    print(res["report"])

    res_no_env = _run(X.drop(columns=ENV_COLS), y)
    d_env = (res["f1"] - res_no_env["f1"]) * 100
    res_no_vib = _run(X.drop(columns=VIB_COLS), y)
    d_vib = (res["f1"] - res_no_vib["f1"]) * 100

    print("\n--- Experimentos de ablación (F1 macro) ---")
    print(f"Completo                  : {res['f1']:.3f}")
    print(f"Sin fusión ambiental      : {res_no_env['f1']:.3f}   (aporte ambiental = {d_env:+.1f} pp)  [H1b]")
    print(f"Sin descriptores vibración: {res_no_vib['f1']:.3f}   (aporte vibración = {d_vib:+.1f} pp)  [H1a]")

    ok_auc = res["auc_roc"] >= C.THRESHOLDS["auc_roc"]
    ok_f1 = res["f1"] >= C.THRESHOLDS["f1"]
    print("\n--- Verificación de umbrales de la hipótesis ---")
    print(f"AUC-ROC >= {C.THRESHOLDS['auc_roc']}: {'CUMPLE' if ok_auc else 'NO CUMPLE'}")
    print(f"F1      >= {C.THRESHOLDS['f1']}: {'CUMPLE' if ok_f1 else 'NO CUMPLE'}")

    summary = dict(auc_roc=res["auc_roc"], f1=res["f1"],
                   f1_sin_ambiental=res_no_env["f1"], aporte_ambiental_pp=d_env,
                   f1_sin_vibracion=res_no_vib["f1"], aporte_vibracion_pp=d_vib,
                   cumple_auc=bool(ok_auc), cumple_f1=bool(ok_f1))
    with open(f"{save_dir}/resultados.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("\nResumen guardado: resultados.json")
    print("\nNOTA DE ALCANCE: las etiquetas se asignan por construcción; estas métricas")
    print("validan que la arquitectura del pipeline es correcta y capaz de aprender,")
    print("no constituyen un resultado biológico sobre M. beecheii.")
    return summary

if __name__ == "__main__":
    main()

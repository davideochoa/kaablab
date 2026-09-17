"""Métricas de evaluación: AUC-ROC (OvR macro), F1 macro, matriz de confusión.
Trabaja con etiquetas codificadas (0..n-1) según el orden de `classes`."""
import numpy as np
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix, classification_report

def evaluate(model, X_test, y_test_codes, classes):
    proba = model.predict_proba(X_test)
    pred = model.predict(X_test)
    labs = list(range(len(classes)))
    auc = roc_auc_score(y_test_codes, proba, multi_class="ovr", average="macro")
    f1 = f1_score(y_test_codes, pred, average="macro")
    cm = confusion_matrix(y_test_codes, pred, labels=labs)
    report = classification_report(y_test_codes, pred, labels=labs,
                                   target_names=list(classes), digits=3, zero_division=0)
    return dict(auc_roc=float(auc), f1=float(f1), confusion=cm, report=report)

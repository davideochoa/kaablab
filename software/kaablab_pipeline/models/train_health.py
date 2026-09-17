"""Módulo de clasificación de salud: Gradient Boosting (XGBoost)."""
from xgboost import XGBClassifier
from .. import config as C

def train_health(X_train, y_train):
    model = XGBClassifier(**C.XGB_PARAMS)
    model.fit(X_train, y_train)
    return model

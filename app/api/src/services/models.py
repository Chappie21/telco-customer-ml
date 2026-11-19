"""Carga de modelos y predicción."""
import json

import joblib
import keras
import numpy as np
import pandas as pd

from src.core.config import LOGISTIC_MODEL, NEURAL_MODEL
from src.services.explain import LogisticExplainer


class ChurnModels:
    def __init__(self) -> None:
        self.logistic = joblib.load(LOGISTIC_MODEL)
        self.neural = keras.models.load_model(NEURAL_MODEL)
        self.columns: list[str] = list(self.logistic.feature_names_in_)
        assert self.neural.input_shape[-1] == len(self.columns), "red neuronal: número de columnas distinto"
        # La red no guarda nombres de columnas; ml/pipeline/train_neural.py los deja junto al modelo
        meta = json.loads(NEURAL_MODEL.with_suffix(".json").read_text())
        assert meta["feature_columns"] == self.columns, "red neuronal: orden de columnas distinto"
        # Perfil promedio de entrenamiento (ml/pipeline/train_logistic.py): referencia de la explicación
        ref = json.loads(LOGISTIC_MODEL.with_suffix(".json").read_text())
        assert ref["feature_columns"] == self.columns, "logística: orden de columnas distinto"
        self.explainer = LogisticExplainer(self.logistic, ref["reference"])

    def predict(self, x: pd.DataFrame) -> dict[str, np.ndarray]:
        """Probabilidad de abandono por fila, por modelo."""
        return {
            "logistic_regression": self.logistic.predict_proba(x)[:, 1],
            "neural_network": self.neural(x.to_numpy(dtype=np.float32), training=False).numpy()[:, 0],
        }

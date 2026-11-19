"""Segmentación K-Means: asigna un cliente a uno de los segmentos encontrados en ml/pipeline/train_kmeans.py."""
import json

import joblib
import numpy as np
import pandas as pd

from src.core.config import KMEANS_MODEL, KMEANS_SEGMENTS


class CustomerSegments:
    def __init__(self, columns: list[str]) -> None:
        bundle = joblib.load(KMEANS_MODEL)
        self.scaler, self.kmeans, self.pca = bundle["scaler"], bundle["kmeans"], bundle["pca"]
        # K-Means numera sus grupos al azar; el script los renumera de mayor a menor abandono
        self.segment_of_cluster = np.array([bundle["segment_of_cluster"][c] for c in range(self.kmeans.n_clusters)])
        self.meta = json.loads(KMEANS_SEGMENTS.read_text())
        assert self.meta["feature_columns"] == columns, "k-means: columnas distintas a las del modelo logístico"
        assert list(self.scaler.feature_names_in_) == columns, "k-means: orden de columnas distinto"
        self.by_id = {s["id"]: s for s in self.meta["segments"]}

    def classify(self, x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """(id de segmento, posición 2D en el mapa) por fila."""
        z = self.scaler.transform(x)
        return self.segment_of_cluster[self.kmeans.predict(z)], self.pca.transform(z)

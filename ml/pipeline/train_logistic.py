"""Regresión logística de churn (modelo recomendado).

Uso (desde ml/): .venv/bin/python -m pipeline.train_logistic

- Split 80/20 estratificado (telco.data.split): el mismo test que la red neuronal.
- Escala solo las 3 numéricas; las binarias/one-hot quedan en 0/1. Regularización L2 por defecto.
- Sin class_weight: el desbalance se resuelve con el umbral de costo (notebook 05), así las
  probabilidades quedan calibradas.
- El modelo entrega SOLO la probabilidad (predict_proba). La decisión de contactar se toma fuera.
- Precisión/recall necesitan un corte para contar aciertos; se reportan con 0.5 solo como referencia.

Salidas: ml/models/churn_logistic.joblib (lo usa la API) y ml/reports/metrics/metrics_logistic.json
"""
import json

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from telco import paths
from telco.data import NUMERIC, SEED, features, load_clean, split

EVAL_CUT = 0.5


def build() -> Pipeline:
    return Pipeline([
        ("scale", ColumnTransformer([("num", StandardScaler(), NUMERIC)], remainder="passthrough",
                                    verbose_feature_names_out=False)),
        ("logreg", LogisticRegression(max_iter=1000)),
    ])


def main() -> None:
    X, y = features(load_clean())
    X_train, X_test, y_train, y_test = split(X, y)
    print(f"Train: {len(X_train):,} ({y_train.mean():.1%} abandona) · Test: {len(X_test):,} ({y_test.mean():.1%} abandona)")

    model = build()
    cv = cross_validate(model, X_train, y_train, cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                        scoring=["roc_auc", "precision", "recall"])
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    assert ((proba >= 0) & (proba <= 1)).all()

    hit = proba >= EVAL_CUT
    metrics = {
        "auc": roc_auc_score(y_test, proba),
        "average_precision": average_precision_score(y_test, proba),
        f"precision@{EVAL_CUT}": precision_score(y_test, hit),
        f"recall@{EVAL_CUT}": recall_score(y_test, hit),
        "cv_auc_mean": cv["test_roc_auc"].mean(),
        "n_train": len(X_train), "n_test": len(X_test), "seed": SEED,
    }
    paths.MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, paths.LOGISTIC_MODEL)
    paths.metrics("metrics_logistic.json").write_text(
        json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in metrics.items()}, indent=2))
    print(f"CV AUC {metrics['cv_auc_mean']:.3f} · Test AUC {metrics['auc']:.3f} · AP {metrics['average_precision']:.3f}")
    print(f"Modelo: {paths.LOGISTIC_MODEL.relative_to(paths.ROOT)}")


if __name__ == "__main__":
    main()

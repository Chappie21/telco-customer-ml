"""Red neuronal de churn (32-16) con el mismo conjunto de prueba que la logística.

Uso (desde ml/): .venv/bin/python -m pipeline.train_neural

- Arquitectura: Normalization → Dense(32, ReLU) → Dropout(0.2) → Dense(16, ReLU) → Dense(1, sigmoide).
  La alternativa 64-32-16 se compara en el notebook 05: no mejora con este volumen de datos.
- 20 % de train se reserva como validación para early stopping (paciencia 12, restaura los mejores pesos).
- Determinista: semilla fija y operaciones deterministas de TensorFlow.

Salidas: ml/models/churn_neural.keras + churn_neural.json (columnas de entrada, las valida la API),
ml/reports/metrics/metrics_neural.json y ml/reports/tables/neural_training_history.csv
"""
import json

import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import average_precision_score, confusion_matrix, precision_score, recall_score, roc_auc_score

from telco import paths
from telco.data import SEED, features, load_clean, split, split_validation

THRESHOLD = 0.5   # solo para reportar precisión/recall
BATCH_SIZE = 64
EPOCHS = 100
PATIENCE = 12


def batches(x, y, *, shuffle=False):
    dataset = tf.data.Dataset.from_tensor_slices((x, y))
    if shuffle:
        dataset = dataset.shuffle(len(x), seed=SEED)
    options = tf.data.Options()
    options.threading.private_threadpool_size = 1
    return dataset.batch(BATCH_SIZE).with_options(options)


def build_model(x_train, units=(32, 16)):
    """Capas densas ReLU con Dropout 0.2 tras la primera; salida sigmoide (probabilidad)."""
    normalization = keras.layers.Normalization()
    normalization.adapt(x_train)
    layers = [keras.Input(shape=(x_train.shape[1],), name="clean_features"), normalization]
    for i, n in enumerate(units):
        layers.append(keras.layers.Dense(n, activation="relu"))
        if i == 0:
            layers.append(keras.layers.Dropout(0.2))
    layers.append(keras.layers.Dense(1, activation="sigmoid"))
    model = keras.Sequential(layers)
    model.compile(optimizer="adam", loss="binary_crossentropy")
    return model


def fit(model, x_train, y_train, x_val, y_val):
    return model.fit(
        batches(x_train, y_train, shuffle=True), validation_data=batches(x_val, y_val), shuffle=False,
        epochs=EPOCHS, verbose=0,
        callbacks=[keras.callbacks.EarlyStopping(monitor="val_loss", patience=PATIENCE, restore_best_weights=True)],
    ).history


def predict(model, x) -> np.ndarray:
    return model(np.asarray(x, dtype=np.float32), training=False).numpy().ravel()


def main() -> None:
    keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()
    X, y = features(load_clean())
    X_dev, X_test, y_dev, y_test = split(X, y)
    X_train, X_val, y_train, y_val = split_validation(X_dev, y_dev)
    x_train, x_val = (d.to_numpy(dtype=np.float32) for d in (X_train, X_val))

    model = build_model(x_train)
    history = fit(model, x_train, y_train.to_numpy(), x_val, y_val.to_numpy())
    probability = predict(model, X_test)
    predicted = probability >= THRESHOLD
    metrics = {
        "auc": roc_auc_score(y_test, probability),
        "average_precision": average_precision_score(y_test, probability),
        "precision@0.5": precision_score(y_test, predicted, zero_division=0),
        "recall@0.5": recall_score(y_test, predicted, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predicted, labels=[0, 1]).tolist(),
        "n_train": len(X_train), "n_validation": len(X_val), "n_test": len(X_test),
        "seed": SEED, "threshold": THRESHOLD,
        "epochs_run": len(history["val_loss"]),
        "best_epoch": int(np.argmin(history["val_loss"])) + 1,
        "feature_columns": X.columns.tolist(),
    }
    paths.MODELS.mkdir(parents=True, exist_ok=True)
    model.save(paths.NEURAL_MODEL)
    paths.NEURAL_META.write_text(json.dumps({"feature_columns": X.columns.tolist()}, indent=2) + "\n")
    paths.metrics("metrics_neural.json").write_text(json.dumps(metrics, indent=2) + "\n")
    epochs = range(1, len(history["loss"]) + 1)
    pd.DataFrame(history, index=epochs).to_csv(paths.table("neural_training_history.csv"), index_label="epoch")
    print(f"Test AUC {metrics['auc']:.3f} · mejor época {metrics['best_epoch']} de {metrics['epochs_run']}")
    print(f"Modelo: {paths.NEURAL_MODEL.relative_to(paths.ROOT)}")


if __name__ == "__main__":
    main()

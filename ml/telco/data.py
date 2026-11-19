"""Carga de datos y la partición train/test única que comparten todos los modelos."""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from telco.paths import CLEAN, RAW

SEED = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.2           # fracción de train que la red neuronal reserva para early stopping
EXCLUDE = ["customer_id", "gender_male"]   # identificador y variable sin asociación (ver notebook 02)
NUMERIC = ["tenure", "monthly_charges", "total_charges"]
FALSE_NEGATIVE_COST = 120       # cliente que abandona sin ser detectado (USD)
FALSE_POSITIVE_COST = 15        # contacto innecesario (USD)


def load_raw(numeric_total: bool = True) -> pd.DataFrame:
    """CSV original. Con numeric_total, TotalCharges pasa a número (los espacios en blanco -> NaN)."""
    df = pd.read_csv(RAW)
    if numeric_total:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


def load_clean() -> pd.DataFrame:
    return pd.read_csv(CLEAN)


def features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Las 25 variables de entrada de los modelos y la etiqueta churn."""
    return df.drop(columns=EXCLUDE + ["churn"]), df["churn"]


def split(X: pd.DataFrame, y: pd.Series):
    """80/20 estratificado con semilla fija: el mismo test para todos los modelos."""
    return train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)


def split_validation(X_train: pd.DataFrame, y_train: pd.Series):
    """Separa validación (early stopping de la red) dentro de train."""
    return train_test_split(X_train, y_train, test_size=VALIDATION_SIZE, stratify=y_train, random_state=SEED)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianza de Wilson para una proporción k/n."""
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half

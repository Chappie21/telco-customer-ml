"""Todas las rutas del proyecto en un solo lugar."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ML = ROOT / "ml"

RAW = ROOT / "data" / "raw" / "telco-customer-churn.csv"
CLEAN = ROOT / "data" / "clean" / "telco_churn_clean.csv"

MODELS = ML / "models"
LOGISTIC_MODEL = MODELS / "churn_logistic.joblib"
NEURAL_MODEL = MODELS / "churn_neural.keras"
NEURAL_META = MODELS / "churn_neural.json"        # columnas de entrada (la API las valida)
KMEANS_MODEL = MODELS / "churn_kmeans.joblib"
KMEANS_META = MODELS / "kmeans_segments.json"

REPORTS = ML / "reports"
TABLES = REPORTS / "tables"
METRICS = REPORTS / "metrics"
FIGURES = REPORTS / "figures"


def figure(section: str, name: str) -> Path:
    """reports/figures/<section>/<name>, creando la carpeta. Secciones: exploracion, perfil,
    patrones, segmentacion, modelos."""
    folder = FIGURES / section
    folder.mkdir(parents=True, exist_ok=True)
    return folder / name


def table(name: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    return TABLES / name


def metrics(name: str) -> Path:
    METRICS.mkdir(parents=True, exist_ok=True)
    return METRICS / name

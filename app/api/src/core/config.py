import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
LOGISTIC_MODEL = Path(os.getenv("LOGISTIC_MODEL", REPO_ROOT / "ml" / "models" / "churn_logistic.joblib"))
NEURAL_MODEL = Path(os.getenv("NEURAL_MODEL", REPO_ROOT / "ml" / "models" / "churn_neural.keras"))
# Orígenes permitidos para el frontend (coma-separados)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
KMEANS_MODEL = Path(os.getenv("KMEANS_MODEL", REPO_ROOT / "ml" / "models" / "churn_kmeans.joblib"))
# Nombre y cifras de cada segmento + muestra del mapa 2D; lo genera ml/pipeline/train_kmeans.py junto al modelo
KMEANS_SEGMENTS = Path(os.getenv("KMEANS_SEGMENTS", REPO_ROOT / "ml" / "models" / "kmeans_segments.json"))

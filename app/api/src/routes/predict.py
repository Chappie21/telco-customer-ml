from fastapi import APIRouter, Request

from src.schemas.customer import Customer
from src.schemas.explanation import Explanation
from src.schemas.prediction import ModelPrediction, Prediction
from src.utils.features import to_features

router = APIRouter()


@router.post("/predict")
def predict(customer: Customer, request: Request) -> Prediction:
    models = request.app.state.models
    probs = models.predict(to_features(customer, models.columns))
    return Prediction(**{name: ModelPrediction(churn_probability=round(float(p[0]), 4)) for name, p in probs.items()})


@router.post("/explain")
def explain(customer: Customer, request: Request) -> Explanation:
    """Por qué la regresión logística estima esa probabilidad: aportes por variable y acciones que la bajarían."""
    return Explanation(**request.app.state.models.explainer.explain(customer))

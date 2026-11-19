from pydantic import BaseModel, Field


class ModelPrediction(BaseModel):
    churn_probability: float = Field(ge=0, le=1)


class Prediction(BaseModel):
    logistic_regression: ModelPrediction
    neural_network: ModelPrediction

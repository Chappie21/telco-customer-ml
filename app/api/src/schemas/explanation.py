from pydantic import BaseModel, Field


class Factor(BaseModel):
    factor: str = Field(description="Variable de negocio (tenure incluye cargo acumulado; internet_service incluye cargo mensual)")
    log_odds: float = Field(description="Aporte exacto frente al perfil promedio; la suma reconstruye la probabilidad")
    points: float = Field(description="Puntos porcentuales que bajaría la probabilidad si este factor fuera el del perfil promedio")


class Action(BaseModel):
    field: str
    value: str | bool
    churn_probability: float = Field(ge=0, le=1, description="Probabilidad si solo cambia este dato")


class Explanation(BaseModel):
    """Solo regresión logística: la red neuronal no tiene una descomposición exacta por variable."""

    reference_probability: float = Field(ge=0, le=1, description="Probabilidad del perfil promedio de entrenamiento")
    churn_probability: float = Field(ge=0, le=1)
    factors: list[Factor]
    actions: list[Action]

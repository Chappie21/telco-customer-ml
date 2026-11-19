from pydantic import BaseModel, Field


class Segment(BaseModel):
    id: int
    name: str
    clients: int
    client_share: float = Field(ge=0, le=1)
    churn_rate: float = Field(ge=0, le=1, description="% del segmento que abandonó (histórico)")
    median_tenure: float
    median_monthly_charges: float
    revenue_at_risk: float = Field(description="USD/mes: suma de probabilidad logística × cargo mensual")
    revenue_at_risk_share: float = Field(ge=0, le=1)
    traits: list[str]


class Segments(BaseModel):
    segments: list[Segment]
    map: list[tuple[float, float, int]] = Field(description="Muestra de clientes históricos: [x, y, id de segmento]")
    explained_variance: list[float]
    silhouette: float
    total_clients: int
    total_revenue_at_risk: float


class Position(BaseModel):
    x: float
    y: float


class SegmentAssignment(BaseModel):
    segment: Segment
    position: Position

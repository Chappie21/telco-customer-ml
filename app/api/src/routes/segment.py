from fastapi import APIRouter, Request

from src.schemas.customer import Customer
from src.schemas.segment import Position, SegmentAssignment, Segments
from src.utils.features import to_features

router = APIRouter()


@router.get("/segments")
def segments(request: Request) -> Segments:
    """Segmentos encontrados por K-Means y el mapa de clientes históricos (estático)."""
    return Segments(**request.app.state.segments.meta)


@router.post("/segment")
def segment(customer: Customer, request: Request) -> SegmentAssignment:
    """Segmento al que pertenece el cliente y su posición en el mapa."""
    seg = request.app.state.segments
    ids, pos = seg.classify(to_features(customer, seg.meta["feature_columns"]))
    return SegmentAssignment(segment=seg.by_id[int(ids[0])],
                             position=Position(x=round(float(pos[0, 0]), 3), y=round(float(pos[0, 1]), 3)))

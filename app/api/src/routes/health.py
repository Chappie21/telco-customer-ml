from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    return {"status": "ok", "models": ["logistic_regression", "neural_network"],
            "segments": len(request.app.state.segments.meta["segments"]),
            "n_features": len(request.app.state.models.columns)}

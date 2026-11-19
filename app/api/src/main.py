"""API de predicción de abandono (churn).

Ejecutar desde app/api:
  .venv/bin/uvicorn src.main:app --reload      -> http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import CORS_ORIGINS
from src.routes import health, predict, segment
from src.services.models import ChurnModels
from src.services.segments import CustomerSegments


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models = ChurnModels()
    app.state.segments = CustomerSegments(app.state.models.columns)
    yield


app = FastAPI(title="Telco Churn API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(segment.router)

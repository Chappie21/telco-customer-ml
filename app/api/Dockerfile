# Contexto de build: raíz del repo (ver app/docker-compose.yml), para poder copiar los modelos de ml/.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TF_CPP_MIN_LOG_LEVEL=3
# Misma disposición que el repo: config.py resuelve los modelos relativos a /srv
WORKDIR /srv/app/api

COPY app/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/models/ /srv/ml/models/
COPY app/api/src ./src

RUN useradd --create-home api && chown -R api /srv
USER api

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=40s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

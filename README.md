# telco-customer-ml

Monorepo: análisis + modelo de churn (`ml/`), API FastAPI (`app/api/`) y frontend Next.js (`app/frontend/`).

```
data/raw/            CSV original (inmutable)
data/clean/          dataset limpio (lo genera ml/pipeline/clean.py; no se versiona)
ml/                  ciencia de datos (venv propio: ml/.venv)
  Makefile           make all = pipeline + notebooks (reproduce todo desde data/raw)
  telco/             código compartido: rutas, carga de datos + split único, estilo de gráficos
  pipeline/          scripts que PRODUCEN artefactos: limpieza y entrenamiento
  notebooks/         análisis que EXPLICA decisiones, con resultados guardados (01 → 05)
  models/            pesos entrenados (los copia la API)
  reports/
    figures/<sección>/  exploracion · perfil · patrones · segmentacion · modelos
    tables/             CSV de resultados
    metrics/            métricas de cada modelo (JSON)
    *.md / *.pdf        reportes de análisis
app/
  api/               FastAPI: sirve los 2 modelos + K-Means (venv propio: app/api/.venv)
    src/             main · core/config · routes · schemas · services · utils
    tests/
  frontend/          Next.js: demo que compara los 2 modelos y muestra el segmento K-Means
    src/             app · components · lib · types · utils
```

## Setup

```bash
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
```

## Reproducir todo

```bash
cd ml
make all          # = make pipeline + make notebooks (~3 min)
```

### 1. Pipeline (artefactos)

Se ejecuta en este orden desde `ml/` (`make pipeline`):

| Comando | Qué hace | Salidas |
|---|---|---|
| `.venv/bin/python -m pipeline.clean` | Limpieza + validaciones de consistencia (aborta si falla alguna) | `data/clean/telco_churn_clean.csv` |
| `.venv/bin/python -m pipeline.train_logistic` | Regresión logística, split 80/20 estratificado (seed 42) | `models/churn_logistic.joblib`, `reports/metrics/metrics_logistic.json` |
| `.venv/bin/python -m pipeline.train_neural` | Red 32-16 con el mismo test + early stopping | `models/churn_neural.keras` + `.json`, `reports/metrics/metrics_neural.json` |
| `.venv/bin/python -m pipeline.train_kmeans` | K-Means (k por silueta + estabilidad) | `models/churn_kmeans.joblib`, `models/kmeans_segments.json`, `reports/tables/clusters_*.csv` |

Los modelos devuelven solo la probabilidad de abandono; el umbral de contacto es una decisión de negocio (notebook 05).

### 2. Notebooks (análisis)

`make notebooks` los ejecuta y guarda sus resultados; también se pueden abrir con Jupyter (`.venv/bin/jupyter lab`).

| Notebook | Contenido |
|---|---|
| `01_calidad_y_exploracion` | Estructura, calidad, distribuciones y relación de cada variable con el abandono |
| `02_perfil_de_abandono` | Pruebas estadísticas, riesgo relativo, antigüedad, paradoja de Simpson del teléfono, verificación del género |
| `03_patrones` | Combinaciones frecuentes de quien se va / se queda y segmentos de un árbol de decisión |
| `04_segmentacion_kmeans` | Elección de k, segmentos, ingreso en riesgo, mapa y perfil (usa el modelo de `pipeline/train_kmeans.py`) |
| `05_comparacion_modelos` | AUC y sobreajuste, umbral por costo (FN = USD 120, FP = USD 15), bootstrap, arquitecturas 32-16 vs 64-32-16, interacciones |

Reportes: `ml/reports/reporte_exploratorio_churn.md` (y `.pdf`), `ml/reports/reporte_patrones.md`.

## Demo con un solo comando (Docker)

```bash
cd app
docker compose up --build        # web http://localhost:3000 · API http://localhost:8000/docs
docker compose down              # detener
```

- La imagen de la API copia `ml/models/` al construirse: si se reentrenan, volver a ejecutar con `--build`.
- La web espera a que la API esté sana (healthcheck) antes de arrancar.

## API (desarrollo local)

```bash
cd app/api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn src.main:app --reload       # http://127.0.0.1:8000/docs
.venv/bin/python -m tests.test_predict        # coincide con los modelos + rechaza datos inválidos + CORS
```

- `GET /health`
- `POST /predict` → `{"logistic_regression": {...}, "neural_network": {...}}`, cada uno con `churn_probability`
- `GET /segments` → segmentos K-Means (nombre, clientes, abandono, ingreso en riesgo) y muestra del mapa 2D
- `POST /segment` → mismo cuerpo que `/predict`; devuelve el segmento del cliente y su posición en el mapa
- Variables de entorno: `LOGISTIC_MODEL`, `NEURAL_MODEL`, `KMEANS_MODEL`, `KMEANS_SEGMENTS` (rutas de modelos), `CORS_ORIGINS` (por defecto `http://localhost:3000`).

## Frontend (desarrollo local)

```bash
cd app/frontend && npm install && npm run dev   # http://localhost:3000 (con la API corriendo en :8000)
```

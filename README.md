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

## Requisitos

| Para | Necesitas |
|---|---|
| Ver la demo | Docker con Docker Compose |
| Notebooks y entrenamiento | Python 3.12 |
| API y web sin Docker | Python 3.12 y Node.js 22 o superior |

```bash
git clone https://github.com/andreschaparro-melt/telco-customer-ml.git
cd telco-customer-ml
```

## 1. Demo rápida (Docker)

Los modelos entrenados vienen incluidos en `ml/models/`, así que no hace falta entrenar nada:

```bash
cd app
docker compose up --build        # primera vez: unos minutos (instala TensorFlow)
```

- Web: http://localhost:3000. Se ingresan los datos de un cliente y se obtiene la probabilidad de abandono de ambos modelos, o su segmento K-Means.
- API: http://localhost:8000/docs (documentación interactiva).
- Detener: `docker compose down`.
- Si se reentrenan los modelos, volver a ejecutar con `--build`: la imagen de la API copia `ml/models/`.

## 2. Entorno de ciencia de datos (`ml/`)

```bash
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
cd ml
make pipeline     # genera data/clean (no se versiona) y reentrena los modelos
```

`make pipeline` es obligatorio antes de ejecutar notebooks o la prueba de la API, porque genera
`data/clean/telco_churn_clean.csv`. Reentrenar da exactamente los mismos modelos (semillas fijas).

En Windows (sin `make`), usar `ml\.venv\Scripts\python` y ejecutar los comandos de la tabla en orden desde `ml/`:

| Comando | Qué hace | Salidas |
|---|---|---|
| `.venv/bin/python -m pipeline.clean` | Limpieza + validaciones de consistencia (aborta si falla alguna) | `data/clean/telco_churn_clean.csv` |
| `.venv/bin/python -m pipeline.train_logistic` | Regresión logística, split 80/20 estratificado (seed 42) | `models/churn_logistic.joblib`, `reports/metrics/metrics_logistic.json` |
| `.venv/bin/python -m pipeline.train_neural` | Red 32-16 con el mismo test + early stopping | `models/churn_neural.keras` + `.json`, `reports/metrics/metrics_neural.json` |
| `.venv/bin/python -m pipeline.train_kmeans` | K-Means (k por silueta + estabilidad) | `models/churn_kmeans.joblib`, `models/kmeans_segments.json`, `reports/tables/clusters_*.csv` |

Los modelos devuelven solo la probabilidad de abandono; el umbral de contacto es una decisión de negocio (notebook 05).

## 3. Notebooks (análisis)

**Solo leerlos:** se guardaron ya ejecutados, así que en GitHub (o en cualquier editor) se ven
con sus tablas y gráficos sin ejecutar nada.

**Ejecutarlos** (requiere el paso 2):

- **VS Code:** abrir la carpeta del repo, abrir un notebook de `ml/notebooks/`, pulsar *Select Kernel*
  → *Python Environments* → `ml/.venv/bin/python` (instalar la extensión *Jupyter* si la pide) y luego *Run All*.
- **JupyterLab en el navegador:**
  ```bash
  ml/.venv/bin/pip install jupyterlab
  ml/.venv/bin/jupyter lab ml/notebooks
  ```
- **Todos de una vez, sin abrirlos:** `cd ml && make notebooks` (los ejecuta en orden y guarda los resultados, ~2 min).

Se leen en orden. Cada uno guarda sus figuras en `ml/reports/figures/<sección>/` y sus tablas en `ml/reports/tables/`:

| Notebook | Contenido |
|---|---|
| `01_calidad_y_exploracion` | Estructura, calidad, distribuciones y relación de cada variable con el abandono |
| `02_perfil_de_abandono` | Pruebas estadísticas, riesgo relativo, antigüedad, paradoja de Simpson del teléfono, verificación del género |
| `03_patrones` | Combinaciones frecuentes de quien se va / se queda y segmentos de un árbol de decisión |
| `04_segmentacion_kmeans` | Elección de k, segmentos, ingreso en riesgo, mapa y perfil (usa el modelo de `pipeline/train_kmeans.py`) |
| `05_comparacion_modelos` | AUC y sobreajuste, umbral por costo (FN = USD 120, FP = USD 15), bootstrap, arquitecturas 32-16 vs 64-32-16, interacciones |

Reportes: `ml/reports/reporte_exploratorio_churn.md` (y `.pdf`), `ml/reports/reporte_patrones.md`.

`make all` reproduce todo desde `data/raw` (pipeline + notebooks, ~3 min).

## 4. Demo local sin Docker (API + web)

Terminal 1, la API:

```bash
cd app/api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn src.main:app --reload       # http://127.0.0.1:8000/docs
```

Terminal 2, la web:

```bash
cd app/frontend
cp .env.example .env.local                    # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev                                   # http://localhost:3000
```

Prueba de la API (requiere `data/clean`, ver paso 2): `cd app/api && .venv/bin/python -m tests.test_predict`.
Comprueba que la API da las mismas probabilidades y segmentos que los modelos para 50 clientes reales, que
rechaza datos inválidos y que CORS funciona.

### Endpoints

- `GET /health`
- `POST /predict` → `{"logistic_regression": {...}, "neural_network": {...}}`, cada uno con `churn_probability`
- `GET /segments` → segmentos K-Means (nombre, clientes, abandono, ingreso en riesgo) y muestra del mapa 2D
- `POST /segment` → mismo cuerpo que `/predict`; devuelve el segmento del cliente y su posición en el mapa
- Variables de entorno: `LOGISTIC_MODEL`, `NEURAL_MODEL`, `KMEANS_MODEL`, `KMEANS_SEGMENTS` (rutas de modelos), `CORS_ORIGINS` (por defecto `http://localhost:3000`).

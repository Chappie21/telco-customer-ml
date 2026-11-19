# Reproduce todo desde data/raw: make all (desde ml/)
PY := .venv/bin/python
NB := .venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200

all: pipeline notebooks

# Artefactos: datos limpios, modelos (los usa la API) y métricas
pipeline:
	$(PY) -m pipeline.clean
	$(PY) -m pipeline.train_logistic
	$(PY) -m pipeline.train_neural
	$(PY) -m pipeline.train_kmeans

# Análisis con resultados guardados: tablas y figuras de reports/
notebooks:
	TF_CPP_MIN_LOG_LEVEL=3 $(NB) notebooks/*.ipynb

.PHONY: all pipeline notebooks

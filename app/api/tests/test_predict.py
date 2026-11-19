"""Ejecutar desde app/api:  .venv/bin/python -m tests.test_predict

La API debe codificar igual que el entrenamiento: para clientes reales de data/clean,
la probabilidad de /predict debe coincidir con la del modelo usado directamente.
"""
import pandas as pd
from fastapi.testclient import TestClient
from scipy.special import expit, logit

from src.core.config import REPO_ROOT
from src.main import app
from src.schemas.customer import CATEGORICAL, Customer


def row_to_request(row: pd.Series) -> dict:
    req = {}
    for k in Customer.model_fields:
        if k in CATEGORICAL:
            req[k] = next(c[len(k) + 1:] for c in row.index if c.startswith(k + "_") and row[c] == 1)
        elif k == "tenure":
            req[k] = int(row[k])
        elif k in ("monthly_charges", "total_charges"):
            req[k] = float(row[k])
        else:
            req[k] = bool(row[k])
    return req


with TestClient(app) as client:
    assert client.get("/health").json()["status"] == "ok"

    df = pd.read_csv(REPO_ROOT / "data" / "clean" / "telco_churn_clean.csv").sample(50, random_state=0)
    expected = app.state.models.predict(df.drop(columns=["customer_id", "gender_male", "churn"]))
    for i, (_, row) in enumerate(df.iterrows()):
        r = client.post("/predict", json=row_to_request(row))
        assert r.status_code == 200, r.text
        assert set(r.json()) == set(expected), r.json()
        for name, probs in expected.items():
            assert abs(r.json()[name]["churn_probability"] - probs[i]) < 1e-4, name

    ok = row_to_request(df.iloc[0])
    bad = [
        {**ok, "internet_service": "no", "streaming_tv": True},      # servicio de internet sin internet
        {**ok, "phone_service": False, "multiple_lines": True},     # líneas sin teléfono
        {**ok, "tenure": 0, "total_charges": 100.0},                # facturado sin antigüedad
        {**ok, "contract": "weekly"},                               # categoría desconocida
        {**ok, "tenure": -1},                                       # fuera de rango
        {k: v for k, v in ok.items() if k != "tenure"},             # campo faltante
    ]
    for b in bad:
        assert client.post("/predict", json=b).status_code == 422, b

    # K-Means: reasignar todo el histórico reproduce el tamaño de cada segmento del script
    seg = app.state.segments
    full = pd.read_csv(REPO_ROOT / "data" / "clean" / "telco_churn_clean.csv")[seg.meta["feature_columns"]]
    ids, _ = seg.classify(full)
    assert {s["id"]: s["clients"] for s in seg.meta["segments"]} == pd.Series(ids).value_counts().to_dict(), "tamaños"
    meta = client.get("/segments").json()
    assert len(meta["segments"]) == len(seg.meta["segments"]) and len(meta["map"]) > 0
    ids, pos = seg.classify(df[seg.meta["feature_columns"]])
    for i, (_, row) in enumerate(df.iterrows()):
        r = client.post("/segment", json=row_to_request(row)).json()
        assert r["segment"]["id"] == ids[i] and abs(r["position"]["x"] - pos[i, 0]) < 1e-3, r
    assert client.post("/segment", json=bad[0]).status_code == 422

    # /explain: los aportes reconstruyen exactamente la probabilidad de la logística, y cada acción
    # es la probabilidad del modelo con ese único dato cambiado
    lr = expected["logistic_regression"]
    for i, (_, row) in enumerate(df.iterrows()):
        req = row_to_request(row)
        e = client.post("/explain", json=req).json()
        assert abs(e["churn_probability"] - lr[i]) < 1e-4, e
        total = logit(e["reference_probability"]) + sum(f["log_odds"] for f in e["factors"])
        assert abs(expit(total) - lr[i]) < 1e-3, (total, lr[i])
        for a in e["actions"]:
            assert a["churn_probability"] < e["churn_probability"]
            q = client.post("/predict", json={**req, a["field"]: a["value"]}).json()["logistic_regression"]["churn_probability"]
            assert abs(q - a["churn_probability"]) < 1e-4, a
    assert client.post("/explain", json=bad[0]).status_code == 422

    pre = client.options("/predict", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert pre.headers.get("access-control-allow-origin") == "http://localhost:3000", "CORS"

print("OK: 50 clientes reales coinciden con los 2 modelos y K-Means; /explain suma exacta; 6 entradas inválidas rechazadas; CORS ok")

"""Segmentación de clientes con K-Means (no supervisado: el algoritmo no ve churn).

Uso (desde ml/, después de train_logistic): .venv/bin/python -m pipeline.train_kmeans

1. Variables: las 25 del modelo logístico, escaladas a 0-1 (MinMax): las binarias quedan 0/1 y
   antigüedad/cargos pesan lo mismo que una binaria (K-Means usa distancias).
2. Elección de k (2-8): mayor silueta entre los k estables (ARI medio >= 0.95 entre 5 semillas).
3. Segmentos numerados de mayor a menor abandono (churn se usa solo DESPUÉS de agrupar).
4. Ingreso en riesgo = probabilidad de abandono fuera de pliegue (CV 5) × cargo mensual.
5. eta² = % de la varianza del riesgo de la logística que explica el segmento.

Salidas: ml/models/churn_kmeans.joblib (escalador + K-Means + PCA) y kmeans_segments.json (los usa la API),
ml/reports/tables/clusters_k.csv y clusters_segmentos.csv. Las figuras están en el notebook 04.
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import MinMaxScaler

from telco import paths
from telco.data import NUMERIC, SEED, load_clean, wilson

K_RANGE = range(2, 9)
MIN_STABILITY = 0.95
MAP_SAMPLE = 1500
# Nombres escritos a mano: los asserts de main() fallan si un reentrenamiento cambia qué es cada segmento.
NAMES = {1: "Fibra, mes a mes", 2: "DSL, mes a mes", 3: "Antiguos con contrato", 4: "Sin internet"}
TRAIT_LABELS = {
    "senior_citizen": "mayor de 65", "partner": "con pareja", "dependents": "con dependientes",
    "tenure": "antigüedad (meses)", "phone_service": "línea telefónica", "multiple_lines": "múltiples líneas",
    "online_security": "seguridad online", "online_backup": "respaldo online", "device_protection": "protección equipo",
    "tech_support": "soporte técnico", "streaming_tv": "streaming TV", "streaming_movies": "streaming películas",
    "paperless_billing": "factura sin papel", "monthly_charges": "cargo mensual ($)", "total_charges": "cargo total ($)",
    "internet_service_dsl": "DSL", "internet_service_fiber_optic": "fibra óptica", "internet_service_no": "sin internet",
    "contract_month_to_month": "mes a mes", "contract_one_year": "contrato 1 año", "contract_two_year": "contrato 2 años",
    "payment_method_bank_transfer_automatic": "transferencia autom.", "payment_method_credit_card_automatic": "tarjeta autom.",
    "payment_method_electronic_check": "cheque electrónico", "payment_method_mailed_check": "cheque por correo",
}


def traits(seg: pd.DataFrame, all_: pd.DataFrame, scaled_diff: pd.Series, n: int = 4) -> str:
    """Las n variables que más separan al segmento del total (en escala 0-1)."""
    out = []
    for col in scaled_diff.abs().sort_values(ascending=False).index[:n]:
        if col in NUMERIC:
            out.append(f"{TRAIT_LABELS[col]} {seg[col].median():.0f} (total {all_[col].median():.0f})")
        else:
            out.append(f"{TRAIT_LABELS[col]} {seg[col].mean():.0%} (total {all_[col].mean():.0%})")
    return "; ".join(out)


def choose_k(Z) -> tuple[pd.DataFrame, int]:
    rows = []
    for k in K_RANGE:
        labs = [KMeans(k, n_init=10, random_state=s).fit_predict(Z) for s in range(5)]
        rows.append({"k": k,
                     "silueta": silhouette_score(Z, labs[0], sample_size=3000, random_state=0),
                     "estabilidad_ari": np.mean([adjusted_rand_score(labs[0], l) for l in labs[1:]])})
    ksel = pd.DataFrame(rows)
    stable = ksel[ksel.estabilidad_ari >= MIN_STABILITY]
    return ksel, int(stable.loc[stable.silueta.idxmax(), "k"])


def assign(bundle: dict, X: pd.DataFrame) -> np.ndarray:
    """Segmento (1 = mayor abandono) de cada fila de X con un bundle ya entrenado."""
    raw = bundle["kmeans"].predict(bundle["scaler"].transform(X))
    return pd.Series(raw).map(bundle["segment_of_cluster"]).values


def main() -> None:
    df = load_clean()
    y = df["churn"]
    logit = joblib.load(paths.LOGISTIC_MODEL)
    X = df[list(logit.feature_names_in_)]
    scaler = MinMaxScaler().fit(X)
    Z = scaler.transform(X)

    ksel, K = choose_k(Z)
    ksel.round(3).to_csv(paths.table("clusters_k.csv"), index=False)
    print("Selección de k:\n", ksel.round(3).to_string(index=False), f"\n-> k = {K}\n")

    kmeans = KMeans(K, n_init=20, random_state=SEED).fit(Z)
    order = pd.Series(y.values).groupby(kmeans.labels_).mean().sort_values(ascending=False).index
    segment_of_cluster = {int(old): new for new, old in enumerate(order, start=1)}
    seg = pd.Series(kmeans.labels_).map(segment_of_cluster).values

    risk = cross_val_predict(clone(logit), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                             method="predict_proba")[:, 1]
    at_risk = risk * X["monthly_charges"].values
    eta2 = pd.Series(risk).groupby(seg).transform("mean").var() / pd.Series(risk).var()

    Zdf = pd.DataFrame(Z, columns=X.columns)
    table = []
    for s in range(1, K + 1):
        m = seg == s
        n, k_churn = int(m.sum()), int(y[m].sum())
        lo, hi = wilson(k_churn, n)
        table.append({
            "segmento": s, "clientes": n, "pct_clientes": n / len(df) * 100,
            "tasa_abandono": k_churn / n * 100, "ic95_bajo": lo * 100, "ic95_alto": hi * 100,
            "riesgo_medio": risk[m].mean() * 100, "riesgo_p10": np.quantile(risk[m], .1) * 100,
            "riesgo_p90": np.quantile(risk[m], .9) * 100,
            "antiguedad_mediana": X.tenure[m].median(), "cargo_mensual_mediano": X.monthly_charges[m].median(),
            "ingreso_mensual": X.monthly_charges[m].sum(), "ingreso_en_riesgo": at_risk[m].sum(),
            "rasgos": traits(X[m], X, Zdf[m].mean() - Zdf.mean()),
        })
    table = pd.DataFrame(table)
    table["pct_ingreso_en_riesgo"] = table.ingreso_en_riesgo / table.ingreso_en_riesgo.sum() * 100
    assert table.clientes.sum() == len(df)
    assert np.isclose(table.ingreso_en_riesgo.sum(), at_risk.sum())
    table.round(2).to_csv(paths.table("clusters_segmentos.csv"), index=False)
    print(table.drop(columns="rasgos").round(1).to_string(index=False))
    print(f"\nIngreso en riesgo total: ${at_risk.sum():,.0f}/mes · eta² riesgo~segmento: {eta2:.2f}")

    if K == 4:
        p = lambda s, c: X[seg == s][c].mean()
        assert p(1, "internet_service_fiber_optic") > .9 and p(1, "contract_month_to_month") > .9
        assert p(2, "internet_service_dsl") > .9 and p(2, "contract_month_to_month") > .5
        assert p(3, "contract_month_to_month") < .1 and X[seg == 3].tenure.median() > 48
        assert p(4, "internet_service_no") > .9
        names = NAMES
    else:
        names = {s: f"Segmento {s}" for s in range(1, K + 1)}

    pca = PCA(2, random_state=SEED).fit(Z)
    P = pca.transform(Z)
    paths.MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump({"scaler": scaler, "kmeans": kmeans, "pca": pca, "segment_of_cluster": segment_of_cluster},
                paths.KMEANS_MODEL)
    sample = np.random.default_rng(SEED).choice(len(df), MAP_SAMPLE, replace=False)
    meta = {
        "feature_columns": list(X.columns),
        "explained_variance": [round(float(v), 3) for v in pca.explained_variance_ratio_],
        "silhouette": round(float(ksel.set_index("k").loc[K, "silueta"]), 3),
        "risk_eta2": round(float(eta2), 3),
        "total_clients": len(df),
        "total_revenue_at_risk": round(float(at_risk.sum()), 2),
        "segments": [{
            "id": int(r.segmento), "name": names[r.segmento], "clients": int(r.clientes),
            "client_share": round(r.pct_clientes / 100, 4), "churn_rate": round(r.tasa_abandono / 100, 4),
            "median_tenure": float(r.antiguedad_mediana), "median_monthly_charges": round(float(r.cargo_mensual_mediano), 2),
            "revenue_at_risk": round(float(r.ingreso_en_riesgo), 2), "revenue_at_risk_share": round(r.pct_ingreso_en_riesgo / 100, 4),
            "traits": r.rasgos.split("; "),
        } for r in table.itertuples()],
        "map": [[round(float(P[i, 0]), 3), round(float(P[i, 1]), 3), int(seg[i])] for i in sample],
    }
    paths.KMEANS_META.write_text(json.dumps(meta, ensure_ascii=False))
    print(f"Modelo: {paths.KMEANS_MODEL.relative_to(paths.ROOT)} + {paths.KMEANS_META.name}")


if __name__ == "__main__":
    main()

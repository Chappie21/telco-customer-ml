"""Limpieza y estandarización: data/raw/telco-customer-churn.csv -> data/clean/telco_churn_clean.csv

Uso (desde ml/): .venv/bin/python -m pipeline.clean

Reglas:
- Columnas en snake_case.
- Textos sin espacios sobrantes; categorías en minúsculas snake_case (ej. "Fiber optic" -> "fiber_optic").
- "No internet service" / "No phone service" -> "no": ya está en internet_service / phone_service.
- Toda columna binaria (Yes/No, 0/1) -> int 0/1, incluido el target churn.
- total_charges vacío (solo clientes con tenure=0, sin facturar aún) -> 0.0.
- Montos redondeados a 2 decimales.
- Categóricas a one-hot 0/1: internet_service_*, contract_*, payment_method_*. gender (binaria) -> gender_male.
- Validaciones de consistencia: si falla alguna, el script aborta y no escribe nada.
"""
import re

import pandas as pd

from telco.paths import CLEAN as OUT
from telco.paths import RAW, ROOT

INTERNET_ADDONS = ["online_security", "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies"]
MONEY = ["monthly_charges", "total_charges"]
CATEGORICAL = ["internet_service", "contract", "payment_method"]


def snake(s: str) -> str:
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", s.strip())  # camelCase -> camel_Case
    s = s.replace("ID", "_id") if s.endswith("ID") else s
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns=snake)
    text = df.select_dtypes(exclude="number").columns.drop("customer_id")
    df["customer_id"] = df["customer_id"].str.strip()

    # Montos
    df["total_charges"] = pd.to_numeric(df["total_charges"].str.strip(), errors="coerce")
    df.loc[df["total_charges"].isna() & (df["tenure"] == 0), "total_charges"] = 0.0
    df[MONEY] = df[MONEY].round(2)

    # Categorías
    text = text.drop("total_charges")
    df[text] = df[text].apply(lambda s: s.map(snake))
    df[INTERNET_ADDONS] = df[INTERNET_ADDONS].replace("no_internet_service", "no")
    df["multiple_lines"] = df["multiple_lines"].replace("no_phone_service", "no")

    # Binarias -> 0/1
    binary = [c for c in df.columns if set(df[c].unique()) <= {"yes", "no"}]
    df[binary] = (df[binary] == "yes").astype(int)

    # Categóricas -> one-hot 0/1 (todas las categorías, legible para la API)
    df["gender"] = (df["gender"] == "male").astype(int)
    df = df.rename(columns={"gender": "gender_male"})
    df = pd.get_dummies(df, columns=CATEGORICAL, dtype=int)
    return df.drop(columns="churn").assign(churn=df["churn"])  # target al final


def validate(df: pd.DataFrame) -> None:
    assert df.notna().all().all(), "quedan nulos"
    assert not df["customer_id"].duplicated().any(), "customer_id duplicado"
    assert df["tenure"].between(0, 72).all(), "tenure fuera de rango"
    assert (df["monthly_charges"] > 0).all(), "monthly_charges <= 0"
    assert ((df["tenure"] == 0) == (df["total_charges"] == 0)).all(), "total_charges=0 debe coincidir con tenure=0"
    assert (df["total_charges"] >= df["monthly_charges"]).where(df["tenure"] > 0, True).all(), "total < mensual"
    for c in CATEGORICAL:
        assert (df.filter(like=f"{c}_").sum(axis=1) == 1).all(), f"one-hot de {c} no suma 1"
    assert df.drop(columns="customer_id").select_dtypes(exclude="number").empty, "quedan columnas no numéricas"
    no_net = df["internet_service_no"] == 1
    assert (df.loc[no_net, INTERNET_ADDONS] == 0).all().all(), "servicios de internet activos sin internet"
    assert (df.loc[df["phone_service"] == 0, "multiple_lines"] == 0).all(), "multiple_lines sin servicio telefónico"
    assert set(df["churn"].unique()) == {0, 1}, "churn no binario"
    print("Validación OK")


if __name__ == "__main__":
    raw = pd.read_csv(RAW)
    df = clean(raw)
    validate(df)
    assert len(df) == len(raw), "se perdieron filas"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, float_format="%.2f")

    pd.set_option("display.width", 200)
    print(f"\nGuardado: {OUT.relative_to(ROOT)}  ({len(df)} filas x {df.shape[1]} columnas)\n")
    print("Esquema:")
    print(pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "valores": [sorted(df[c].unique().tolist()) if df[c].nunique() <= 4 else f"{df[c].min()} .. {df[c].max()}" for c in df],
    }).to_string())

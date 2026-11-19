import pandas as pd

from src.schemas.customer import CATEGORICAL, Customer


def to_features(customer: Customer, columns: list[str]) -> pd.DataFrame:
    """Customer -> 1 fila con las columnas del entrenamiento (binarias 0/1 + one-hot), en su orden."""
    raw = customer.model_dump()
    row = {k: int(v) if isinstance(v, bool) else v for k, v in raw.items() if k not in CATEGORICAL}
    for field in CATEGORICAL:
        row[f"{field}_{raw[field]}"] = 1
    return pd.DataFrame([row]).reindex(columns=columns, fill_value=0)

"""Explicación de la regresión logística para un cliente.

La logística es aditiva en log-odds, así que la explicación es exacta (sin SHAP ni aproximaciones):
  aporte_j = coef_j · (z_j − z_ref_j)      z = variable escalada, z_ref = perfil promedio de entrenamiento
  logit(p) = logit(p_ref) + Σ aportes

Las columnas se agrupan por variable de negocio. Antigüedad + cargo acumulado e internet + cargo
mensual van juntos: están muy correlacionados y por separado el modelo reparte el efecto con signos
opuestos (un cargo mensual alto "bajaría" el riesgo), lo que confundiría al lector.

Las acciones cambian un solo dato accionable y vuelven a evaluar el modelo: es la asociación que
aprendió el modelo, no un efecto causal.
"""
import pandas as pd
from scipy.special import expit
from sklearn.pipeline import Pipeline

from src.schemas.customer import INTERNET_ADDONS, Customer
from src.utils.features import to_features

GROUPED = {
    "tenure": ["tenure", "total_charges"],
    "internet_service": ["monthly_charges", "internet_service_"],
    "contract": ["contract_"],
    "payment_method": ["payment_method_"],
}
# Datos que una oferta de retención puede cambiar (no la antigüedad, la edad ni el hogar)
ACTIONS: list[tuple[str, object]] = [
    ("contract", "one_year"), ("contract", "two_year"),
    ("payment_method", "bank_transfer_automatic"), ("payment_method", "credit_card_automatic"),
    ("online_security", True), ("online_backup", True), ("device_protection", True), ("tech_support", True),
]


def group_of(column: str) -> str:
    for group, members in GROUPED.items():
        if any(column == m or (m.endswith("_") and column.startswith(m)) for m in members):
            return group
    return column


class LogisticExplainer:
    def __init__(self, model: Pipeline, reference: dict[str, float]) -> None:
        self.model = model
        self.columns: list[str] = list(model.feature_names_in_)
        self.scale = model.named_steps["scale"]
        self.coef = model.named_steps["logreg"].coef_[0]
        self.groups = [group_of(c) for c in self.scale.get_feature_names_out()]  # orden tras escalar
        # El escalado es lineal: escalar la media = media de lo escalado
        self.z_ref = self.scale.transform(pd.DataFrame([reference])[self.columns])[0]
        self.base_logit = float(model.named_steps["logreg"].intercept_[0] + self.coef @ self.z_ref)

    def explain(self, customer: Customer) -> dict:
        x = to_features(customer, self.columns)
        contrib = self.coef * (self.scale.transform(x)[0] - self.z_ref)
        logit = self.base_logit + contrib.sum()
        p = float(expit(logit))

        by_group: dict[str, float] = {}
        for group, v in zip(self.groups, contrib):
            by_group[group] = by_group.get(group, 0.0) + float(v)
        factors = [
            # Puntos: cuánto bajaría la probabilidad si este factor fuera el del perfil promedio
            {"factor": g, "log_odds": round(v, 4), "points": round(100 * (p - float(expit(logit - v))), 2)}
            for g, v in sorted(by_group.items(), key=lambda kv: -kv[1])
        ]

        best: dict[str, dict] = {}
        for field, value in ACTIONS:
            if getattr(customer, field) == value or (field in INTERNET_ADDONS and customer.internet_service == "no"):
                continue
            q = float(self.model.predict_proba(to_features(customer.model_copy(update={field: value}), self.columns))[0, 1])
            if q < p and (field not in best or q < best[field]["churn_probability"]):
                best[field] = {"field": field, "value": value, "churn_probability": round(q, 4)}

        return {
            "reference_probability": round(float(expit(self.base_logit)), 4),
            "churn_probability": round(p, 4),
            "factors": factors,
            "actions": sorted(best.values(), key=lambda a: a["churn_probability"]),
        }


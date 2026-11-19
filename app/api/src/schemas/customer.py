from typing import Literal

from pydantic import BaseModel, Field, model_validator

InternetService = Literal["dsl", "fiber_optic", "no"]
Contract = Literal["month_to_month", "one_year", "two_year"]
PaymentMethod = Literal["bank_transfer_automatic", "credit_card_automatic", "electronic_check", "mailed_check"]
INTERNET_ADDONS = ["online_security", "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies"]
CATEGORICAL = ("internet_service", "contract", "payment_method")


class Customer(BaseModel):
    """Datos de un cliente, en el mismo formato que data/clean (antes del one-hot)."""

    senior_citizen: bool
    partner: bool
    dependents: bool
    tenure: int = Field(ge=0, le=120, description="Meses como cliente (entrenado con 0-72)")
    phone_service: bool
    multiple_lines: bool
    internet_service: InternetService
    online_security: bool
    online_backup: bool
    device_protection: bool
    tech_support: bool
    streaming_tv: bool
    streaming_movies: bool
    contract: Contract
    paperless_billing: bool
    payment_method: PaymentMethod
    monthly_charges: float = Field(gt=0, le=1000)
    total_charges: float = Field(ge=0, le=100_000)

    model_config = {"json_schema_extra": {"example": {
        "senior_citizen": False, "partner": False, "dependents": False, "tenure": 3,
        "phone_service": True, "multiple_lines": False, "internet_service": "fiber_optic",
        "online_security": False, "online_backup": False, "device_protection": False, "tech_support": False,
        "streaming_tv": True, "streaming_movies": False, "contract": "month_to_month",
        "paperless_billing": True, "payment_method": "electronic_check",
        "monthly_charges": 85.5, "total_charges": 256.5,
    }}}

    @model_validator(mode="after")
    def coherent(self):
        # Mismas reglas que validate() en ml/clean.py
        if self.internet_service == "no" and (on := [a for a in INTERNET_ADDONS if getattr(self, a)]):
            raise ValueError(f"sin internet no puede tener servicios de internet activos: {on}")
        if not self.phone_service and self.multiple_lines:
            raise ValueError("multiple_lines requiere phone_service")
        if (self.tenure == 0) != (self.total_charges == 0):
            raise ValueError("total_charges debe ser 0 si y solo si tenure es 0")
        return self

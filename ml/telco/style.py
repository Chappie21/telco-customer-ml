"""Paleta, etiquetas en español y estilo común de los gráficos."""
import matplotlib.pyplot as plt

STAY, CHURN = "#2a78d6", "#eb6834"         # azul = se queda, naranja = abandona (seguros para daltonismo)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MODEL_COLORS = {"logistic": STAY, "neural": CHURN}
# Mismos colores que la web (validados para daltonismo); segmento 1 = mayor abandono
SEG_COLORS = ["#b8336a", "#c98500", "#2a78d6", "#0b6e63", "#8a5cd1", "#d23f8f", "#5a6b7d", "#7fa31a"]

LABELS = {
    "gender_male": "Género masculino", "senior_citizen": "Cliente sénior", "partner": "Tiene pareja",
    "dependents": "Tiene dependientes", "tenure": "Antigüedad (meses)", "phone_service": "Servicio telefónico",
    "multiple_lines": "Múltiples líneas", "online_security": "Seguridad en línea", "online_backup": "Respaldo en línea",
    "device_protection": "Protección de dispositivos", "tech_support": "Soporte técnico",
    "streaming_tv": "Streaming de TV", "streaming_movies": "Streaming de películas",
    "paperless_billing": "Factura electrónica", "monthly_charges": "Cargo mensual (USD)",
    "total_charges": "Cargo acumulado (USD)", "internet_service_dsl": "Internet DSL",
    "internet_service_fiber_optic": "Internet fibra óptica", "internet_service_no": "Sin internet",
    "contract_month_to_month": "Contrato mes a mes", "contract_one_year": "Contrato 1 año",
    "contract_two_year": "Contrato 2 años", "payment_method_bank_transfer_automatic": "Pago transferencia automática",
    "payment_method_credit_card_automatic": "Pago tarjeta automática",
    "payment_method_electronic_check": "Pago cheque electrónico", "payment_method_mailed_check": "Pago cheque por correo",
    "churn": "Abandono",
}
# Columnas del CSV original
RAW_LABELS = {
    "gender": "Género", "SeniorCitizen": "Cliente sénior", "Partner": "Tiene pareja", "Dependents": "Tiene dependientes",
    "tenure": "Antigüedad (meses)", "PhoneService": "Servicio telefónico", "MultipleLines": "Múltiples líneas",
    "InternetService": "Tipo de internet", "OnlineSecurity": "Seguridad en línea", "OnlineBackup": "Respaldo en línea",
    "DeviceProtection": "Protección de dispositivos", "TechSupport": "Soporte técnico", "StreamingTV": "Streaming de TV",
    "StreamingMovies": "Streaming de películas", "Contract": "Contrato", "PaperlessBilling": "Factura electrónica",
    "PaymentMethod": "Medio de pago", "MonthlyCharges": "Cargo mensual (USD)", "TotalCharges": "Cargo acumulado (USD)",
    "Churn": "Abandono",
}


def apply() -> None:
    plt.rcParams.update({
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
        "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "font.size": 10,
        "figure.dpi": 100, "savefig.dpi": 120, "savefig.bbox": "tight",
    })


def save(fig, path) -> None:
    """Guarda la figura. No la cierra: en un notebook se sigue mostrando debajo de la celda."""
    fig.savefig(path)

# Valores de las categorías del CSV original
VALUE_LABELS = {
    "Yes": "Sí", "No": "No", "Female": "Mujer", "Male": "Hombre", "0": "No", "1": "Sí",
    "No internet service": "Sin internet", "No phone service": "Sin teléfono", "Fiber optic": "Fibra óptica",
    "Month-to-month": "Mes a mes", "One year": "1 año", "Two year": "2 años",
    "Bank transfer (automatic)": "Transferencia autom.", "Credit card (automatic)": "Tarjeta autom.",
    "Electronic check": "Cheque electrónico", "Mailed check": "Cheque por correo",
}

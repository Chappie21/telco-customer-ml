import type { ModelKey } from "@/types/customer";

// Fuente (conjunto de prueba, seed 42): ml/reports/metrics/metrics_logistic.json,
// ml/reports/metrics/metrics_neural.json
export const HISTORIC_CUSTOMERS = 7043; // dataset completo (80% entrenamiento, 20% prueba)
export const TEST_CUSTOMERS = 1409;
export const BASE_CHURN_RATE = 0.265; // media histórica de abandono

// Corte de contacto de la regla recomendada (regresión logística): mínimo costo con USD 120 por baja
// no detectada y USD 15 por llamada innecesaria, elegido con validación cruzada en entrenamiento.
// ponytail: copiado a mano de ml/reports/tables/churn_threshold_comparison.csv (logistic, validation);
// servirlo desde la API si el umbral empieza a recalcularse.
export const CONTACT_THRESHOLD = 0.13409708628004705;

export interface ModelInfo {
  key: ModelKey;
  name: string;
  short: string;
  color: string;
  auc: number;
}

/** Orden de presentación en toda la página. */
export const MODELS: ModelInfo[] = [
  { key: "logistic_regression", name: "Regresión logística", short: "Logística", color: "var(--model-logistic)", auc: 0.842 },
  { key: "neural_network", name: "Red neuronal", short: "Red", color: "var(--model-neural)", auc: 0.836 },
];

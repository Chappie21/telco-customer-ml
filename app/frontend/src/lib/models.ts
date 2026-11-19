import type { ModelKey } from "@/types/customer";

// Fuente (conjunto de prueba, seed 42): ml/reports/metrics/metrics_logistic.json,
// ml/reports/metrics/metrics_neural.json
export const HISTORIC_CUSTOMERS = 7043; // dataset completo (80% entrenamiento, 20% prueba)
export const TEST_CUSTOMERS = 1409;
export const BASE_CHURN_RATE = 0.265; // media histórica de abandono

export interface ModelInfo {
  key: ModelKey;
  name: string;
  short: string;
  color: string;
  auc: number;
  precision: number;
  recall: number;
}

/** Orden de presentación en toda la página. */
export const MODELS: ModelInfo[] = [
  { key: "logistic_regression", name: "Regresión logística", short: "Logística", color: "var(--model-logistic)", auc: 0.842, precision: 0.652, recall: 0.551 },
  { key: "neural_network", name: "Red neuronal", short: "Red", color: "var(--model-neural)", auc: 0.836, precision: 0.65, recall: 0.497 },
];

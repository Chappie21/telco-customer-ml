// Mismo contrato que app/api/src/schemas/customer.py
export type InternetService = "dsl" | "fiber_optic" | "no";
export type Contract = "month_to_month" | "one_year" | "two_year";
export type PaymentMethod =
  | "bank_transfer_automatic"
  | "credit_card_automatic"
  | "electronic_check"
  | "mailed_check";

export interface Customer {
  senior_citizen: boolean;
  partner: boolean;
  dependents: boolean;
  tenure: number;
  phone_service: boolean;
  multiple_lines: boolean;
  internet_service: InternetService;
  online_security: boolean;
  online_backup: boolean;
  device_protection: boolean;
  tech_support: boolean;
  streaming_tv: boolean;
  streaming_movies: boolean;
  contract: Contract;
  paperless_billing: boolean;
  payment_method: PaymentMethod;
  monthly_charges: number;
  total_charges: number;
}

export type InternetAddon =
  | "online_security"
  | "online_backup"
  | "device_protection"
  | "tech_support"
  | "streaming_tv"
  | "streaming_movies";

export type ModelKey = "logistic_regression" | "neural_network";

export type Prediction = Record<ModelKey, { churn_probability: number }>;

// Mismo contrato que app/api/src/schemas/segment.py
export interface Segment {
  id: number;
  name: string;
  clients: number;
  client_share: number;
  churn_rate: number;
  median_tenure: number;
  median_monthly_charges: number;
  revenue_at_risk: number;
  revenue_at_risk_share: number;
  traits: string[];
}

export interface SegmentsInfo {
  segments: Segment[];
  /** Muestra de clientes históricos: [x, y, id de segmento] */
  map: [number, number, number][];
  explained_variance: number[];
  silhouette: number;
  total_clients: number;
  total_revenue_at_risk: number;
}

export interface SegmentAssignment {
  segment: Segment;
  position: { x: number; y: number };
}

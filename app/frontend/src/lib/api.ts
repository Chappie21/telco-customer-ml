import type { Customer, Explanation, Prediction, SegmentAssignment, SegmentsInfo } from "@/types/customer";
import { API_URL } from "./config";

export class ApiError extends Error {}

/** Llama a la API y lanza ApiError con un mensaje listo para mostrar. */
async function request<T>(path: string, signal?: AbortSignal, body?: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, body === undefined ? { signal } : {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    if (signal?.aborted) throw e;
    throw new ApiError(`No hay conexión con la API en ${API_URL}. Verifique que esté en ejecución.`);
  }
  if (res.status === 422) {
    const data = await res.json().catch(() => null);
    const msg = data?.detail?.[0]?.msg?.replace(/^Value error, /, "");
    throw new ApiError(msg ? `Datos inválidos: ${msg}.` : "Los datos del cliente no son válidos.");
  }
  if (!res.ok) throw new ApiError(`La API respondió con un error (${res.status}). Intente de nuevo.`);
  return res.json();
}

/** POST /predict: probabilidad de abandono de cada modelo. */
export const predict = (customer: Customer, signal?: AbortSignal) => request<Prediction>("/predict", signal, customer);

/** POST /explain: por qué la regresión logística estima esa probabilidad. */
export const explain = (customer: Customer, signal?: AbortSignal) => request<Explanation>("/explain", signal, customer);

/** POST /segment: segmento K-Means del cliente y su posición en el mapa. */
export const classify = (customer: Customer, signal?: AbortSignal) => request<SegmentAssignment>("/segment", signal, customer);

/** GET /segments: segmentos encontrados y mapa de clientes históricos (no cambia entre llamadas). */
export const getSegments = (signal?: AbortSignal) => request<SegmentsInfo>("/segments", signal);

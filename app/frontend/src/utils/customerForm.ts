import type { Customer, InternetAddon } from "@/types/customer";

export const INTERNET_ADDONS: InternetAddon[] = [
  "online_security", "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies",
];

/** Estado editable del formulario: los números se guardan como texto mientras se escriben. */
export type FormState = Omit<Customer, "tenure" | "monthly_charges" | "total_charges"> & {
  tenure: string;
  monthly_charges: string;
  total_charges: string;
};

export const toFormState = (c: Customer): FormState => ({
  ...c,
  tenure: String(c.tenure),
  monthly_charges: String(c.monthly_charges),
  total_charges: String(c.total_charges),
});

/** Aplica las reglas de coherencia al cambiar un campo (mismas que ml/clean.py y la API). */
export function applyRules(f: FormState): FormState {
  const next = { ...f };
  if (next.internet_service === "no") for (const a of INTERNET_ADDONS) next[a] = false;
  if (!next.phone_service) next.multiple_lines = false;
  if (next.tenure.trim() === "0") next.total_charges = "0";
  return next;
}

/** Valida y convierte. Devuelve el Customer o un mensaje de error para el usuario. */
export function parseForm(f: FormState): { customer: Customer } | { error: string } {
  const tenure = Number(f.tenure);
  const monthly = Number(f.monthly_charges);
  const total = Number(f.total_charges);
  if (f.tenure.trim() === "" || !Number.isInteger(tenure) || tenure < 0 || tenure > 120)
    return { error: "La antigüedad debe ser un número entero de meses entre 0 y 120." };
  if (f.monthly_charges.trim() === "" || !(monthly > 0) || monthly > 1000)
    return { error: "El cargo mensual debe ser mayor que 0 y como máximo 1,000." };
  if (f.total_charges.trim() === "" || !(total >= 0) || total > 100000)
    return { error: "El cargo total debe estar entre 0 y 100,000." };
  if (tenure > 0 && total === 0)
    return { error: "Con antigüedad mayor que 0, el cargo total debe ser mayor que 0." };
  return { customer: { ...f, tenure, monthly_charges: monthly, total_charges: total } };
}

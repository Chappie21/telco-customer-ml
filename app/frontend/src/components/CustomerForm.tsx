"use client";

import type { InternetAddon } from "@/types/customer";
import type { FormState } from "@/utils/customerForm";
import styles from "./CustomerForm.module.css";

interface Props {
  value: FormState;
  onChange: (next: FormState) => void;
  error: string | null;
}

const ADDON_LABELS: [InternetAddon, string][] = [
  ["online_security", "Seguridad online"],
  ["online_backup", "Respaldo online"],
  ["device_protection", "Protección de equipo"],
  ["tech_support", "Soporte técnico"],
  ["streaming_tv", "Streaming TV"],
  ["streaming_movies", "Streaming películas"],
];

export default function CustomerForm({ value: f, onChange, error }: Props) {
  const set = <K extends keyof FormState>(key: K, v: FormState[K]) => onChange({ ...f, [key]: v });
  const check = (key: keyof FormState, label: string, disabled = false) => (
    <label className={styles.check}>
      <input type="checkbox" checked={f[key] as boolean} disabled={disabled} onChange={(e) => set(key, e.target.checked as never)} />
      {label}
    </label>
  );
  const noInternet = f.internet_service === "no";

  return (
    <form className={styles.card} onSubmit={(e) => e.preventDefault()} noValidate>
      <h2 className={styles.title}>Datos del cliente</h2>

      <fieldset className={styles.group}>
        <legend className={styles.legend}>Perfil</legend>
        <div className={styles.checks}>
          {check("senior_citizen", "Mayor de 65 años")}
          {check("partner", "Tiene pareja")}
          {check("dependents", "Tiene dependientes")}
        </div>
        <label className={styles.field}>
          Antigüedad (meses)
          <input type="number" inputMode="numeric" min={0} max={120} step={1} value={f.tenure} onChange={(e) => set("tenure", e.target.value)} />
        </label>
      </fieldset>

      <fieldset className={styles.group}>
        <legend className={styles.legend}>Servicios</legend>
        <div className={styles.grid}>
          <label className={styles.field}>
            Internet
            <select value={f.internet_service} onChange={(e) => set("internet_service", e.target.value as FormState["internet_service"])}>
              <option value="fiber_optic">Fibra óptica</option>
              <option value="dsl">DSL</option>
              <option value="no">Sin internet</option>
            </select>
          </label>
          <div className={styles.stack}>
            {check("phone_service", "Línea telefónica")}
            {check("multiple_lines", "Múltiples líneas", !f.phone_service)}
          </div>
        </div>
        <div className={styles.checks}>
          {ADDON_LABELS.map(([key, label]) => <span key={key}>{check(key, label, noInternet)}</span>)}
        </div>
        {noInternet && <p className={styles.hint}>Sin internet no aplican los servicios de internet.</p>}
      </fieldset>

      <fieldset className={styles.group}>
        <legend className={styles.legend}>Contrato y facturación</legend>
        <div className={styles.grid}>
          <label className={styles.field}>
            Contrato
            <select value={f.contract} onChange={(e) => set("contract", e.target.value as FormState["contract"])}>
              <option value="month_to_month">Mes a mes</option>
              <option value="one_year">Un año</option>
              <option value="two_year">Dos años</option>
            </select>
          </label>
          <label className={styles.field}>
            Método de pago
            <select value={f.payment_method} onChange={(e) => set("payment_method", e.target.value as FormState["payment_method"])}>
              <option value="electronic_check">Cheque electrónico</option>
              <option value="mailed_check">Cheque por correo</option>
              <option value="bank_transfer_automatic">Transferencia automática</option>
              <option value="credit_card_automatic">Tarjeta automática</option>
            </select>
          </label>
          <label className={styles.field}>
            Cargo mensual ($)
            <input type="number" inputMode="decimal" min={0} step={0.01} value={f.monthly_charges} onChange={(e) => set("monthly_charges", e.target.value)} />
          </label>
          <label className={styles.field}>
            Cargo total ($)
            <input type="number" inputMode="decimal" min={0} step={0.01} value={f.total_charges} disabled={f.tenure.trim() === "0"} onChange={(e) => set("total_charges", e.target.value)} />
          </label>
        </div>
        {check("paperless_billing", "Factura sin papel")}
      </fieldset>

      {error && <p className={styles.error} role="alert">{error}</p>}
    </form>
  );
}

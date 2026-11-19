import type { Customer, Explanation } from "@/types/customer";
import { BASE_CHURN_RATE } from "@/lib/models";
import { pct } from "@/utils/format";
import styles from "./ExplanationPanel.module.css";

interface Props {
  explanation: Explanation;
  customer: Customer;
  loading: boolean;
}

const MAX_RISE = 4;
const MAX_SHOWN = 6;
const MIN_LOG_ODDS = 0.1; // por debajo, el factor apenas mueve la predicción
const MAX_ACTIONS = 3;

const INTERNET: Record<Customer["internet_service"], string> = { fiber_optic: "Fibra óptica", dsl: "DSL", no: "Sin internet" };
const CONTRACT: Record<Customer["contract"], string> = { month_to_month: "Mes a mes", one_year: "Un año", two_year: "Dos años" };
const PAYMENT: Record<Customer["payment_method"], string> = {
  electronic_check: "Cheque electrónico",
  mailed_check: "Cheque por correo",
  bank_transfer_automatic: "Transferencia automática",
  credit_card_automatic: "Tarjeta automática",
};
const BINARY: Record<string, string> = {
  senior_citizen: "Mayor de 65 años",
  partner: "Pareja",
  dependents: "Dependientes",
  phone_service: "Línea telefónica",
  multiple_lines: "Múltiples líneas",
  online_security: "Seguridad online",
  online_backup: "Respaldo online",
  device_protection: "Protección de equipo",
  tech_support: "Soporte técnico",
  streaming_tv: "Streaming TV",
  streaming_movies: "Streaming películas",
  paperless_billing: "Factura sin papel",
};

const money = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;

/** Nombre del factor y el valor de este cliente. */
function describe(factor: string, c: Customer): [string, string] {
  switch (factor) {
    case "tenure": return ["Antigüedad y cargo acumulado", `${c.tenure} meses · ${money(c.total_charges)}`];
    case "internet_service": return ["Internet y cargo mensual", `${INTERNET[c.internet_service]} · ${money(c.monthly_charges)}`];
    case "contract": return ["Contrato", CONTRACT[c.contract]];
    case "payment_method": return ["Medio de pago", PAYMENT[c.payment_method]];
    default: return [BINARY[factor] ?? factor, c[factor as keyof Customer] ? "Sí" : "No"];
  }
}

function actionLabel(field: string, value: string | boolean): string {
  if (field === "contract") return `Contrato de ${CONTRACT[value as Customer["contract"]].toLowerCase()}`;
  if (field === "payment_method") return `Pago con ${PAYMENT[value as Customer["payment_method"]].toLowerCase()}`;
  return `Agregar ${(BINARY[field] ?? field).toLowerCase()}`;
}

const pp = (v: number) => {
  const a = Math.abs(v);
  return `${v > 0 ? "+" : "−"}${a < 1 ? a.toFixed(1) : Math.round(a)} pp`;
};

export default function ExplanationPanel({ explanation: e, customer, loading }: Props) {
  const rise = e.factors.filter((f) => f.log_odds >= MIN_LOG_ODDS).slice(0, MAX_RISE);
  const lower = e.factors.filter((f) => f.log_odds <= -MIN_LOG_ODDS).reverse().slice(0, MAX_SHOWN - rise.length);
  const shown = [...rise, ...lower];
  const max = Math.max(...shown.map((f) => Math.abs(f.log_odds)));
  const actions = e.actions.slice(0, MAX_ACTIONS);

  return (
    <section className={`${styles.card} ${loading ? styles.dim : ""}`} aria-labelledby="explain-title" aria-busy={loading}>
      <div className={styles.head}>
        <h2 id="explain-title" className={styles.title}>Por qué la regresión logística estima {pct(e.churn_probability)}%</h2>
        <p className={styles.lead}>
          Frente al perfil promedio de la cartera, que tiene <strong>{pct(e.reference_probability)}%</strong>. Cada barra muestra cuánto
          aleja a este cliente de ese perfil, en <strong>puntos porcentuales (pp)</strong>: +10 pp significa que, si ese
          factor fuera el del perfil promedio, su probabilidad sería 10 puntos menor.
        </p>
      </div>

      {shown.length ? (
        <div>
          <div className={styles.axisHead} aria-hidden="true">
            <span />
            <span className={styles.axisLabels}><span>← Baja el riesgo</span><span>Sube el riesgo →</span></span>
            <span className={styles.axisUnit}>pp</span>
          </div>
          <ul className={styles.factors}>
            {shown.map((f) => {
              const [label, value] = describe(f.factor, customer);
              const up = f.log_odds > 0;
              const width = `${(Math.abs(f.log_odds) / max) * 100}%`;
              return (
                <li key={f.factor} className={styles.factor}>
                  <span className={styles.label}>{label}<span className={styles.value}>{value}</span></span>
                  <span className={styles.track} aria-hidden="true">
                    <span className={styles.half}>{!up && <span className={`${styles.bar} ${styles.down}`} style={{ width }} />}</span>
                    <span className={styles.half}>{up && <span className={`${styles.bar} ${styles.up}`} style={{ width }} />}</span>
                  </span>
                  <span className={`${styles.pp} ${up ? styles.ppUp : styles.ppDown}`}>
                    {pp(f.points)}<span className={styles.srOnly}> {up ? "sube" : "baja"} el riesgo</span>
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      ) : (
        <p className={styles.none}>Este cliente está muy cerca del perfil promedio: ningún dato mueve la predicción de forma apreciable.</p>
      )}
      <p className={styles.foot}>
        El perfil promedio toma el valor medio de cada dato. Su probabilidad es menor que la media histórica de abandono
        ({pct(BASE_CHURN_RATE)}%) porque las bajas se concentran en pocos clientes de riesgo alto.
      </p>

      <div className={styles.whatIf}>
        <h3 className={styles.subtitle}>Qué lo reduciría <span className={styles.subUnit}>(probabilidad y cambio en pp)</span></h3>
        {actions.length ? (
          <ul className={styles.actions}>
            {actions.map((a) => (
              <li key={a.field} className={styles.action}>
                <span>{actionLabel(a.field, a.value)}</span>
                <span className={styles.change}>
                  {pct(e.churn_probability)}% <span aria-label="pasa a">→</span> <strong>{pct(a.churn_probability)}%</strong>
                </span>
                <span className={styles.delta}>{pp((a.churn_probability - e.churn_probability) * 100)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.none}>Ningún cambio de oferta evaluado (contrato, pago automático, servicios de protección y soporte) baja su probabilidad.</p>
        )}
        <p className={styles.foot}>
          Cada fila cambia un solo dato y vuelve a calcular con el modelo. Es lo que el modelo asocia a ese cambio, no un efecto garantizado.
        </p>
      </div>
    </section>
  );
}

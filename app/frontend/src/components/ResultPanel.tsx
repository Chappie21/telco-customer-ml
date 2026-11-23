import type { Prediction } from "@/types/customer";
import { BASE_CHURN_RATE, CONTACT_THRESHOLD, MODELS, TEST_CUSTOMERS } from "@/lib/models";
import { integer, pct, spreadPoints } from "@/utils/format";
import RiskScale from "./RiskScale";
import styles from "./ResultPanel.module.css";

interface Props {
  prediction: Prediction | null;
  loading: boolean;
  stale: boolean;
}

export default function ResultPanel({ prediction, loading, stale }: Props) {
  if (!prediction) {
    return (
      <section className={styles.card} aria-label="Resultado" aria-busy={loading}>
        <div className={styles.empty}>
          <strong>{loading ? "Calculando…" : "Sin resultado todavía"}</strong>
          <p>Complete los datos del cliente. Cada modelo devolverá su probabilidad de abandono.</p>
        </div>
      </section>
    );
  }

  const probs = MODELS.map((m) => prediction[m.key].churn_probability);
  const risk = prediction.logistic_regression.churn_probability;
  const call = risk >= CONTACT_THRESHOLD;

  return (
    <section className={`${styles.card} ${loading ? styles.dim : ""}`} aria-label="Resultado" aria-busy={loading} aria-live="polite">
      <h2 className={styles.title}>Probabilidad estimada de abandono</h2>
      <div className={styles.pair}>
        {MODELS.map((m, i) => (
          <div key={m.key} className={styles.model}>
            <span className={styles.name}><span className={styles.swatch} style={{ background: m.color }} />{m.name}</span>
            <span className={styles.value}>{pct(probs[i])}<span className={styles.unit}>%</span></span>
          </div>
        ))}
      </div>
      <div className={`${styles.decision} ${call ? styles.call : ""}`}>
        <strong className={styles.verdict}>{call ? "Llamar a este cliente" : "No llamar por ahora"}</strong>
        <p>
          {call
            ? `Su riesgo (${pct(risk)}%) supera el corte de ${pct(CONTACT_THRESHOLD)}%: con los costos de Telco, llamar sale más barato que arriesgar la baja.`
            : `Su riesgo (${pct(risk)}%) está por debajo del corte de ${pct(CONTACT_THRESHOLD)}%: la llamada costaría más de lo que se espera perder.`}
        </p>
        <p className={styles.rule}>Regla recomendada: regresión logística · USD 120 por baja no detectada, USD 15 por llamada innecesaria.</p>
      </div>
      <RiskScale prediction={prediction} />
      <p className={styles.note}>
        Entre ambos modelos hay <strong>{spreadPoints(probs)} puntos</strong>. La media histórica de abandono es {pct(BASE_CHURN_RATE)}%.
      </p>
      <p className={styles.auc}>
        AUC en {integer(TEST_CUSTOMERS)} clientes no vistos al entrenar: {MODELS.map((m) => `${m.short} ${m.auc.toFixed(3)}`).join(" · ")} (1 = ordena perfecto, 0.5 = azar).
      </p>
      {stale && !loading && <p className={styles.stale}>Este resultado corresponde a los últimos datos válidos.</p>}
    </section>
  );
}

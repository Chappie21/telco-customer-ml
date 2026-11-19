import type { Prediction } from "@/types/customer";
import { BASE_CHURN_RATE, MODELS } from "@/lib/models";
import { pct } from "@/utils/format";
import styles from "./RiskScale.module.css";

/** Un carril por modelo sobre la misma escala 0–100%, con la media histórica como referencia. */
export default function RiskScale({ prediction }: { prediction: Prediction }) {
  const summary = MODELS.map((m) => `${m.name} ${pct(prediction[m.key].churn_probability)}%`).join(", ");
  return (
    <div className={styles.scale} role="img" aria-label={`Escala de 0 a 100%: ${summary}; media histórica ${pct(BASE_CHURN_RATE)}%`}>
      {MODELS.map((m) => (
        <div key={m.key} className={styles.lane} aria-hidden="true">
          <span className={styles.label}><span className={styles.swatch} style={{ background: m.color }} />{m.short}</span>
          <div className={styles.track}>
            <div className={styles.base} style={{ left: `${BASE_CHURN_RATE * 100}%` }} />
            <div className={styles.marker} style={{ left: `${prediction[m.key].churn_probability * 100}%`, background: m.color }} />
          </div>
        </div>
      ))}
      <div className={styles.axis} aria-hidden="true">
        <span />
        <div className={styles.ticks}>
          <span>0%</span>
          <span className={styles.baseLabel} style={{ left: `${BASE_CHURN_RATE * 100}%` }}>Media histórica {pct(BASE_CHURN_RATE)}%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}

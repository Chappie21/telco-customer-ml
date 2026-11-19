import { MODELS, TEST_CUSTOMERS } from "@/lib/models";
import { integer } from "@/utils/format";
import styles from "./ReliabilityTable.module.css";

const ROWS = [
  { key: "auc", metric: "AUC", explain: "Qué tan bien ordena a los clientes por riesgo (0.5 = azar, 1 = perfecto)." },
  { key: "precision", metric: "Precisión", explain: "De los clientes con probabilidad de 50% o más, cuántos se fueron." },
  { key: "recall", metric: "Recall", explain: "De los clientes que se fueron, cuántos tenían 50% o más." },
] as const;

export default function ReliabilityTable() {
  return (
    <section className={styles.card} aria-labelledby="reliability-title">
      <h2 id="reliability-title" className={styles.title}>¿Qué tan confiable es cada modelo?</h2>
      <p className={styles.lead}>Medido en {integer(TEST_CUSTOMERS)} clientes que ningún modelo vio al entrenar, comparando su predicción con lo que realmente pasó. En negrita, el mejor de cada fila.</p>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Métrica</th>
            {MODELS.map((m) => (
              <th key={m.key} scope="col" className={styles.num}>
                <span className={styles.long}>{m.name}</span><span className={styles.short}>{m.short}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ key, metric, explain }) => {
            const best = Math.max(...MODELS.map((m) => m[key]));
            return (
              <tr key={key}>
                <td><span className={styles.metric}>{metric}</span><span className={styles.explain}>{explain}</span></td>
                {MODELS.map((m) => (
                  <td key={m.key} className={`${styles.num} ${m[key] === best ? styles.best : ""}`}>{m[key].toFixed(3)}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className={styles.foot}>El corte de 50% solo se usa para medir; los modelos devuelven únicamente la probabilidad.</p>
    </section>
  );
}

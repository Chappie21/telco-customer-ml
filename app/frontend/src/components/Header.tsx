import { TEST_CUSTOMERS, HISTORIC_CUSTOMERS } from "@/lib/models";
import { integer } from "@/utils/format";
import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.bar}>
      <div className={styles.brand}>
        <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
          <rect width="28" height="28" rx="6" fill="var(--accent-soft)" />
          <path d="M7 19 L12 13 L16 16 L21 9" fill="none" stroke="var(--accent)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Predicción de abandono
      </div>
      <span className={styles.meta}>
        Histórico de {integer(HISTORIC_CUSTOMERS)} clientes · modelos evaluados en {integer(TEST_CUSTOMERS)}
      </span>
    </header>
  );
}

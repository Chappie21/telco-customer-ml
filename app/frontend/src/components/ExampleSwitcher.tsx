import { EXAMPLES } from "@/lib/examples";
import styles from "./ExampleSwitcher.module.css";

interface Props {
  activeId: string | null;
  onPick: (id: string) => void;
}

export default function ExampleSwitcher({ activeId, onPick }: Props) {
  return (
    <div className={styles.group} role="group" aria-label="Cargar cliente de ejemplo">
      {EXAMPLES.map((e) => (
        <button key={e.id} type="button" className={styles.option} aria-pressed={e.id === activeId} onClick={() => onPick(e.id)}>
          {e.label}
        </button>
      ))}
    </div>
  );
}

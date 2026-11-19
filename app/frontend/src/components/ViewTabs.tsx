import type { KeyboardEvent } from "react";
import styles from "./ViewTabs.module.css";

export type View = "models" | "segment";

const TABS: { id: View; label: string }[] = [
  { id: "models", label: "Probabilidad por modelo" },
  { id: "segment", label: "Segmento (K-Means)" },
];

interface Props {
  value: View;
  onChange: (view: View) => void;
}

export default function ViewTabs({ value, onChange }: Props) {
  // Flechas izquierda/derecha cambian de pestaña, como en un tablist nativo
  function onKey(e: KeyboardEvent<HTMLButtonElement>) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    const next = TABS[(TABS.findIndex((t) => t.id === value) + 1) % TABS.length];
    onChange(next.id);
    document.getElementById(`tab-${next.id}`)?.focus();
  }
  return (
    <div className={styles.tabs} role="tablist" aria-label="Qué mostrar">
      {TABS.map((t) => (
        <button
          key={t.id}
          id={`tab-${t.id}`}
          type="button"
          role="tab"
          aria-selected={t.id === value}
          aria-controls={`panel-${t.id}`}
          tabIndex={t.id === value ? 0 : -1}
          className={styles.tab}
          onClick={() => onChange(t.id)}
          onKeyDown={onKey}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

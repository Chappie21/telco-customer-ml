"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Customer, Explanation, Prediction, SegmentAssignment, SegmentsInfo } from "@/types/customer";
import { ApiError, classify, explain, getSegments, predict } from "@/lib/api";
import { EXAMPLES } from "@/lib/examples";
import { applyRules, parseForm, toFormState, type FormState } from "@/utils/customerForm";
import CustomerForm from "./CustomerForm";
import ExampleSwitcher from "./ExampleSwitcher";
import ExplanationPanel from "./ExplanationPanel";
import ResultPanel from "./ResultPanel";
import SegmentPanel from "./SegmentPanel";
import ViewTabs, { type View } from "./ViewTabs";
import styles from "./ChurnComparison.module.css";

const DEBOUNCE_MS = 350;
const UNEXPECTED = "Ocurrió un error inesperado. Intente de nuevo.";

export default function ChurnComparison() {
  const [form, setForm] = useState<FormState>(() => toFormState(EXAMPLES[0].customer));
  const [exampleId, setExampleId] = useState<string | null>(null);
  const [view, setView] = useState<View>("models");
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  // Se guarda con el cliente que la produjo: si el formulario queda inválido, sigue siendo coherente
  const [explained, setExplained] = useState<{ explanation: Explanation; customer: Customer } | null>(null);
  const [assignment, setAssignment] = useState<SegmentAssignment | null>(null);
  const [segmentsInfo, setSegmentsInfo] = useState<SegmentsInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const parsed = useMemo(() => parseForm(form), [form]);
  const invalid = "error" in parsed ? parsed.error : null;
  const error = invalid ?? apiError;

  // Recalcula la vista activa en cada cambio del formulario: espera una pausa al escribir
  // (no al cambiar de pestaña) y cancela la petición anterior.
  const lastView = useRef(view);
  useEffect(() => {
    if ("error" in parsed) return;
    const delay = lastView.current === view ? DEBOUNCE_MS : 0;
    lastView.current = view;
    const ctrl = new AbortController();
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        if (view === "models") {
          const [p, e] = await Promise.all([predict(parsed.customer, ctrl.signal), explain(parsed.customer, ctrl.signal)]);
          setPrediction(p);
          setExplained({ explanation: e, customer: parsed.customer });
        } else setAssignment(await classify(parsed.customer, ctrl.signal));
        setApiError(null);
      } catch (e) {
        if (ctrl.signal.aborted) return;
        setApiError(e instanceof ApiError ? e.message : UNEXPECTED);
      } finally {
        if (!ctrl.signal.aborted) setLoading(false);
      }
    }, delay);
    return () => {
      clearTimeout(timer);
      ctrl.abort();
    };
  }, [parsed, view]);

  // Segmentos y mapa: no cambian, se piden una vez al abrir la pestaña
  useEffect(() => {
    if (view !== "segment" || segmentsInfo) return;
    const ctrl = new AbortController();
    getSegments(ctrl.signal)
      .then(setSegmentsInfo)
      .catch((e) => { if (!ctrl.signal.aborted) setApiError(e instanceof ApiError ? e.message : UNEXPECTED); });
    return () => ctrl.abort();
  }, [view, segmentsInfo]);

  function edit(next: FormState) {
    setForm(applyRules(next));
    setExampleId(null);
  }

  function pickExample(id: string) {
    const ex = EXAMPLES.find((e) => e.id === id);
    if (!ex) return;
    setForm(toFormState(ex.customer));
    setExampleId(id);
  }

  return (
    <main className={styles.main}>
      <div className={styles.head}>
        <div className={styles.intro}>
          <h1 className={styles.h1}>Probabilidad de abandono por cliente</h1>
          <p className={styles.lead}>Ajuste los datos del cliente y vea al instante la probabilidad que estima cada modelo o el segmento de clientes al que pertenece.</p>
        </div>
        <ExampleSwitcher activeId={exampleId} onPick={pickExample} />
      </div>
      <div className={styles.body}>
        <div className={styles.form}>
          <CustomerForm value={form} onChange={edit} error={error} />
        </div>
        <div className={styles.results}>
          <ViewTabs value={view} onChange={setView} />
          {view === "models" ? (
            <div id="panel-models" role="tabpanel" aria-labelledby="tab-models" className={styles.panel}>
              <ResultPanel prediction={prediction} loading={loading && !invalid} stale={error !== null} />
              {explained && <ExplanationPanel {...explained} loading={loading && !invalid} />}
            </div>
          ) : (
            <div id="panel-segment" role="tabpanel" aria-labelledby="tab-segment" className={styles.panel}>
              <SegmentPanel info={segmentsInfo} assignment={assignment} loading={loading && !invalid} stale={error !== null} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

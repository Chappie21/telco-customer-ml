"use client";

import { useState } from "react";
import type { SegmentAssignment, SegmentsInfo } from "@/types/customer";
import { BASE_CHURN_RATE } from "@/lib/models";
import { integer, pct, usd } from "@/utils/format";
import SegmentMap, { segmentColor } from "./SegmentMap";
import styles from "./SegmentPanel.module.css";

interface Props {
  info: SegmentsInfo | null;
  assignment: SegmentAssignment | null;
  loading: boolean;
  stale: boolean;
}

export default function SegmentPanel({ info, assignment, loading, stale }: Props) {
  const [focus, setFocus] = useState<number | null>(null);

  if (!info || !assignment) {
    return (
      <section className={styles.card} aria-busy={loading}>
        <div className={styles.empty}>
          <strong>{loading ? "Buscando el segmento…" : "Sin resultado todavía"}</strong>
          <p>Complete los datos del cliente para ver a qué segmento pertenece.</p>
        </div>
      </section>
    );
  }

  const seg = assignment.segment;
  return (
    <section
      className={`${styles.card} ${loading ? styles.dim : ""}`} aria-busy={loading} aria-live="polite">
      <div className={styles.head}>
        <h2 className={styles.title}>Segmento del cliente</h2>
        <p className={styles.name}><span className={styles.swatch} style={{ background: segmentColor(seg.id) }} />{seg.name}</p>
        <p className={styles.fact}>
          En este segmento abandonó el <strong>{pct(seg.churn_rate)}%</strong> de los clientes (media histórica {pct(BASE_CHURN_RATE)}%).
          Concentra el <strong>{pct(seg.revenue_at_risk_share)}%</strong> del ingreso mensual en riesgo: {usd(seg.revenue_at_risk)} de {usd(info.total_revenue_at_risk)}.
        </p>
      </div>

      <figure className={styles.figure}>
        <SegmentMap info={info} assignment={assignment} focus={focus} />
        <figcaption className={styles.caption}>
          Cada punto es un cliente histórico ({integer(info.map.length)} de {integer(info.total_clients)}). El mapa resume las 25 características en 2 dimensiones ({pct(info.explained_variance[0] + info.explained_variance[1]).replace(/\.0$/, "")}% de la variación), por eso un cliente puede verse cerca de otro segmento: su segmento es el de la tabla.
        </figcaption>
      </figure>

      <table className={styles.legend}>
        <caption className={styles.legendTitle}>Segmentos encontrados</caption>
        <thead>
          <tr>
            <th scope="col">Segmento</th>
            <th scope="col" className={`${styles.num} ${styles.clients}`}>Clientes</th>
            <th scope="col" className={styles.num}>Abandono</th>
            <th scope="col" className={styles.num}>Ingreso en riesgo</th>
          </tr>
        </thead>
        <tbody onMouseLeave={() => setFocus(null)}>
          {info.segments.map((s) => (
            <tr key={s.id} tabIndex={0} aria-current={s.id === seg.id ? "true" : undefined}
              className={s.id === seg.id ? styles.current : undefined}
              onMouseEnter={() => setFocus(s.id)} onFocus={() => setFocus(s.id)} onBlur={() => setFocus(null)}>
              <th scope="row">
                <span className={styles.rowName}>
                  <span className={styles.swatch} style={{ background: segmentColor(s.id) }} />
                  {s.name}
                  {s.id === seg.id && <span className={styles.tag}>Este cliente</span>}
                </span>
                <span className={styles.detail}>~{s.median_tenure.toFixed(0)} meses de antigüedad · {usd(s.median_monthly_charges)}/mes</span>
              </th>
              <td className={`${styles.num} ${styles.clients}`}>{integer(s.clients)}</td>
              <td className={styles.num}>{pct(s.churn_rate)}%</td>
              <td className={styles.num}>{pct(s.revenue_at_risk_share)}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className={styles.foot}>
        K-Means agrupa a los clientes por su perfil, sin mirar si abandonaron. El segmento describe a quién se parece este cliente; no es una probabilidad. Ingreso en riesgo: probabilidad de la regresión logística × cargo mensual.
      </p>
      {stale && !loading && <p className={styles.stale}>Este resultado corresponde a los últimos datos válidos.</p>}
    </section>
  );
}

import type { SegmentAssignment, SegmentsInfo } from "@/types/customer";
import styles from "./SegmentMap.module.css";

const W = 640;
const H = 380;
const PAD = 16;

export const segmentColor = (id: number) => `var(--segment-${id})`;

interface Props {
  info: SegmentsInfo;
  assignment: SegmentAssignment;
  /** Segmento resaltado desde la leyenda (los demás se atenúan) */
  focus: number | null;
}

/** Mapa 2D (PCA) de clientes históricos coloreados por segmento, con el cliente actual marcado. */
export default function SegmentMap({ info, assignment, focus }: Props) {
  const { x, y } = assignment.position;
  const xs = [...info.map.map((p) => p[0]), x];
  const ys = [...info.map.map((p) => p[1]), y];
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const sx = (v: number) => PAD + ((v - x0) / (x1 - x0)) * (W - 2 * PAD);
  const sy = (v: number) => H - PAD - ((v - y0) / (y1 - y0)) * (H - 2 * PAD);
  const cx = sx(x);
  const cy = sy(y);
  const labelLeft = cx > W - 130; // etiqueta del lado con espacio

  return (
    <svg className={styles.map} viewBox={`0 0 ${W} ${H}`} role="img"
      aria-label={`Mapa de clientes por segmento. Este cliente cae en el segmento ${assignment.segment.name}.`}>
      <g aria-hidden="true">
        {info.map.map(([px, py, s], i) => (
          <circle key={i} cx={sx(px)} cy={sy(py)} r={2.6} fill={segmentColor(s)}
            className={focus !== null && focus !== s ? styles.faded : styles.point} />
        ))}
      </g>
      <g className={styles.customer} style={{ transform: `translate(${cx}px, ${cy}px)` }} aria-hidden="true">
        <circle r={11} fill="var(--surface)" />
        <circle r={8} fill={segmentColor(assignment.segment.id)} stroke="var(--text)" strokeWidth={2.5} />
        <text x={labelLeft ? -16 : 16} y={5} textAnchor={labelLeft ? "end" : "start"} className={styles.label}>Este cliente</text>
      </g>
    </svg>
  );
}

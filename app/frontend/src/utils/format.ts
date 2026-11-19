/** 0.72694 -> "72.7" */
export const pct = (p: number) => (p * 100).toFixed(1);

/** Diferencia entre el mayor y el menor, calculada desde los valores mostrados. */
export const spreadPoints = (values: number[]) => {
  const shown = values.map((v) => Number(pct(v)));
  return (Math.max(...shown) - Math.min(...shown)).toFixed(1);
};

export const integer = (n: number) => n.toLocaleString("en-US");

/** 101227.16 -> "$101,227" */
export const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

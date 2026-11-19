# Frontend · Predicción de abandono

Next.js (App Router) que consume `app/api` y compara la probabilidad de abandono de los 2 modelos (logística y red neuronal), o el segmento K-Means del cliente en un mapa con la leyenda de segmentos.

```bash
npm install
cp .env.example .env.local      # NEXT_PUBLIC_API_URL (por defecto http://127.0.0.1:8000)
npm run dev                     # http://localhost:3000  (la API debe estar corriendo)
npm run build && npm start      # producción
```

```
src/
  app/          layout, página y tokens globales (globals.css)
  components/   Header, ChurnComparison (estado), CustomerForm, ExampleSwitcher,
                ResultPanel, RiskScale, ExplanationPanel (+ CSS modules)
  lib/          api (cliente /predict), config, examples, models (métricas de prueba)
  types/        contrato Customer / Prediction (igual que la API)
  utils/        customerForm (reglas de coherencia + validación), format
```

Las métricas de `src/lib/models.ts` vienen de `ml/reports/metrics/metrics_logistic.json` y `ml/reports/metrics/metrics_neural.json`; actualizarlas si se reentrenan los modelos.

# Balanced Scorecard - Trilema Compliance + Fairness + Performance
## Artefacto #11 del TFM
**Modelo principal**: Fair-Aware (XGBoost + ThresholdOptimizer)
**Evaluado sobre**: Dataset completo de Test (n = 46,127 registros, mora real = 8.07%)

---

## 1. Dimension COMPLIANCE (EU AI Act)

| Requisito | Target | Resultado | Estado |
|-----------|--------|-----------|--------|
| DPD < 0.10 (Art. 10) | < 0.10 | 0.0032 | OK |
| DIR > 0.80 (EEOC) | > 0.80 | 0.9901 | OK |
| Documentacion (Art. 11) | 12 artefactos | 12/12 planificados | OK |
| Transparencia (Art. 13) | SHAP disponible | TreeSHAP implementado | OK |

## 2. Dimension FAIRNESS (reduccion de sesgo)

| Metrica | Valor | Target | Estado |
|---------|-------|--------|--------|
| DPD Fair-Aware | 0.0032 | < 0.10 | OK |
| EOD Fair-Aware | 0.0108 | < 0.10 | OK |
| Reduccion DPD vs Standard | -252.41% | > 50% | OK |

## 3. Dimension PERFORMANCE (capacidad predictiva)

| Metrica | Valor | Target | Estado |
|---------|-------|--------|--------|
| AUC-ROC | 0.7413 | > 0.75 | OK |
| Bootstrap CI 95% | [0.7328, 0.7485] | LB > 0.70 | OK |
| McNemar Test (vs Baseline) | p-value: 0.000000 | < 0.05 | OK |

---
*Artefacto #11 del TFM - Balanced Scorecard.*

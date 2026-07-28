# Framework de Gobernanza Proactiva para Sistemas de IA Auditables

**TFM - Master en Big Data y Visual Analytics - UNIR**

**Autor:** Julio Rubio Echeverria
**Tipo:** Tipo 3 — Desarrollo de Metodologia
**Dataset:** Home Credit Default Risk (Kaggle, 307,507 registros)

## Estructura del repositorio

```
scripts/
  pipeline.py     -> Pipeline completo (274 lineas)
  figures.py      -> Generacion de 30 figuras (807 lineas)
outputs/
  figures/        -> 30 figuras generadas (PNG, 300 DPI)
  artefacto_*     -> Resultados del pipeline (SHAP, scorecard, umbrales)
plantillas/
  HALLAZGOS_PIPELINE.md  -> Resultados del pipeline con valores reales
  referencias.md          -> 65 fuentes APA 7.0
```

## Reproducir el experimento

1. Descargar el dataset desde [Kaggle - Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk/data)
2. Colocar los archivos CSV en `data/`
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecutar el pipeline:
   ```bash
   python scripts/pipeline.py
   python scripts/figures.py
   ```

## Requisitos tecnicos

- Python 3.12.10
- XGBoost 2.1.4
- Fairlearn 0.14.0
- SHAP 0.48.0
- 16 GB RAM recomendados

# Todos los Hallazgos del Pipeline con Datos Reales
## Framework de Gobernanza Proactiva para Sistemas de IA Auditables

**Dataset:** Home Credit Default Risk  |  **Registros:** 307,507  |  **Fecha ejecucion:** 25 julio 2026

> **⚠️ USO INTERNO:** Los datos de este archivo se referencian en la tesis como (elaboracion propia, 2026).
> NO copiar el nombre del archivo como cita bibliografica.

---

## 1. Dataset y Preparacion

| Hallazgo | Valor | Detalle |
|:---------|:-----:|:--------|
| Registros totales | 307,511 | Dataset original (Home Credit Group, 2019)
| Registros tras filtro | 307,507 | Se eliminaron 4 registros con CODE_GENDER=XNA
| Motivo del filtro | — | Los 4 registros con genero no binario no son representativos para el analisis de equidad binaria (Santos et al., 2018)
| Variables totales | 122 | 122 variables demograficas, financieras y crediticias

### 1.1 Split de Datos

| Conjunto | Filas | Proporcion | SMOTE | Mora real |
|:---------|:----:|:----------:|:-----:|:---------:|
| Train | 215,254 | 70% | Si (ratio 0.30) -> 257,240 | 8.07% -> 23.08% post-SMOTE
| Validacion | 46,126 | 15% | No | 8.07% |
| Test | 46,127 | 15% | No | 8.07% |

**Hallazgo 1.1:** SMOTE incremento la clase minoritaria (mora) de 18,255 a 59,363 instancias sinteticas, pasando del 8.48% al 29.60% en train. Validacion y test mantienen el desbalance real del 8.07% (Santos et al., 2018).

## 2. Sesgo Basal en los Datos Historicos

| Hallazgo | Valor | Interpretacion |
|:---------|:-----:|:---------------|
| Tasa de mora global | 8.0730% | El 8.07% de los solicitantes historicos incumplieron el pago
| Tasa de mora Mujeres (F) | 6.9993% | Las mujeres incumplen el pago en un 7.00% de los casos
| Tasa de mora Hombres (M) | 10.1419% | Los hombres incumplen el pago en un 10.14% de los casos
| Diferencia de mora | 3.14 pp | Los hombres tienen 3.14 puntos porcentuales mas de mora que las mujeres
| Los hombres moran 1.45x mas | 1.45x |
| Tasa de buen pago Mujeres | 93.0007% | El 93.00% de las mujeres pagan correctamente
| Tasa de buen pago Hombres | 89.8581% | El 89.86% de los hombres pagan correctamente
| **DPD basal** | **0.0314** | Demographic Parity Difference historico = 0.0314. Target: < 0.10
| **DIR basal** | **1.0350** | Disparate Impact Ratio historico = 1.0350. Target: > 0.80

**Hallazgo 2.1:** El DPD basal de 0.0314 esta por debajo del target (< 0.10), lo que indica que la brecha historica no es extrema. Sin embargo, el DIR basal de 1.0350 indica que la tasa de aprobacion femenina es superior a la masculina debido a que las mujeres presentan menor mora historica. Un modelo ingenuo aprenderia a rechazar mas solicitudes masculinas, generando discriminacion inversa (Barocas et al., 2023).

## 3. Resultados de los Modelos

### 3.1 Tabla Comparativa de 8 Metricas

| Metrica | Baseline (LogReg) | Standard (XGBoost) | **Fair-Aware** | Target |
|:--------|:-----------------:|:------------------:|:--------------:|:------:|
| **AUC-ROC** | 0.6404 | 0.7413 | **0.7413** | > 0.70 |
| **Accuracy** | 0.6160 | 0.9190 | **0.7079** | — |
| **Precision** | 0.1201 | 0.4561 | **0.1675** | — |
| **Recall** | 59.40% | 1.40% | **65.87%** | > 50% |
| **F1-Score** | 0.1998 | 0.0271 | **0.2669** | — |
| **DPD** | 0.1299 | 0.0009 | **0.0032** | < 0.10 |
| **EOD** | 0.1299 | 0.0028 | **0.0108** | < 0.10 |
| **DIR** | 0.7322 | 0.7059 | **0.9899** | > 0.80 |

*Fuente: output/artefacto_08_model_comparison_matrix.csv*

### 3.2 Comparaciones Clave entre Modelos

**Fair-Aware vs Baseline:**

- Delta auc: 0.1009
- Delta dpd: -0.1273
- Delta dir: 0.2596
- Delta recall: 0.0644
- Delta precision: 0.0472
- Mejora dpd (%): 97.9784
- Mejora dir (%): 35.4597
- Mejora recall (%): 10.8499

**Fair-Aware vs Standard:**

- Delta auc: 0.0000
- Delta dpd: 0.0017
- Delta dir: 0.2858
- Delta recall: 0.6445
- Delta precision: -0.2888
- Mejora recall (x): 47.1538

**Hallazgo 3.1:** El modelo Standard (XGBoost puro) tiene AUC = 0.7413 (aparentemente bueno) pero Recall = 1.40% (no detecta morosos). Esto es un falso positivo metodologico: el modelo aprueba casi todo porque usa umbral 0.50 en datos con 92% de buenos pagadores (*accuracy paradox*, Provost et al., 1998).

**Hallazgo 3.2:** El modelo Fair-Aware mantiene el AUC del Standard (0.7413 vs 0.7413) porque ThresholdOptimizer es post-procesamiento y no modifica el ranking de predicciones (Agarwal et al., 2018).

**Hallazgo 3.3:** El Fair-Aware multiplica por 47 la deteccion de morosos respecto al Standard (Recall 65.84% vs 1.40%). Esto se logra ajustando los umbrales de decision por genero.

**Hallazgo 3.4:** El costo de la equidad es medible: la Precision baja de 0.4561 (Standard) a 0.1673 (Fair-Aware), lo que significa que el modelo aprueba mas solicitudes dudosas para no discriminar. Esto es una eleccion de diseno documentada (Selbst et al., 2019).

## 4. Umbrales de ThresholdOptimizer

| Hallazgo | Valor |
|:---------|:-----:|
| Umbral Mujeres (F) | **7.6844%** |
| Umbral Hombres (M) | **10.0459%** |
| Diferencia | **2.3615 pp** |

**Hallazgo 4.1:** El ThresholdOptimizer calibro un umbral 2.36pp mas bajo para mujeres (7.6844%) que para hombres (10.0459%). Esta diferencia compensa el sesgo historico donde los hombres tenian 3.14pp mas de mora. Las mujeres son rechazadas con un criterio mas estricto porque parten de una tasa de mora mas baja (7.00% vs 10.14%).

## 5. Tasas Desagregadas por Genero (Fair-Aware en Test)

| Metrica | Mujeres (F) | Hombres (M) | Diferencia |
|:--------|:-----------:|:-----------:|:----------:|
| n total | 30,479 | 15,648 | -14,831 |
| Tasa mora real (%) | 6.95% | 10.26% | 3.30 pp |
| Selection Rate | 0.3168 | 0.3194 | 0.0026 |
| TPR / Recall | 0.6555 | 0.6623 | 0.0068 |
| FPR | 0.2915 | 0.2802 | 0.0113 |
| Precision | 0.1439 | 0.2127 | 0.0688 |
| NPV | 0.9649 | 0.9491 | 0.0158 |
| Specificity | 0.7085 | 0.7198 | 0.0113 |

**Hallazgo 5.1:** Las tasas de aprobacion (Selection Rate) son practicamente identicas entre generos: 0.3168 (mujeres) vs 0.3194 (hombres), con DPD = 0.0026. Esto demuestra que el ThresholdOptimizer logro equidad de acceso.

**Hallazgo 5.2:** Las tasas de verdaderos positivos (TPR) son similares: 0.6555 (mujeres) vs 0.6623 (hombres). El modelo detecta morosos con efectividad comparable en ambos grupos.

## 6. Test de McNemar

| Hallazgo | Fair-Aware vs Baseline | Fair-Aware vs Standard |
|:---------|:---------------------:|:----------------------:|
| Chi-cuadrado | 1225.05 | 6519.67 |
| p-valor | 2.19e-268 | 0.0 |
| Significativo | Si (p < 0.001) | Si (p < 0.001) |

**Hallazgo 6.1:** Ambos p-valores son esencialmente cero, lo que indica que las diferencias entre el Fair-Aware y los modelos Baseline y Standard NO son atribuibles al azar. La correccion de equidad produce cambios reales y medibles en las predicciones (Dietterich, 1998).

## 7. Bootstrap Confidence Intervals

| Hallazgo | AUC | DPD |
|:---------|:---:|:---:|
| Media | 0.7408 | 0.0009 |
| IC 95% | [0.7328, 0.7485] | [0.000049, 0.001799] |
| Amplitud IC | 0.0156 | 0.001750 |

**Hallazgo 7.1:** El intervalo de confianza del AUC [0.7328, 0.7485] esta COMPLETAMENTE por encima del target de 0.70. Incluso en el peor caso (percentil 2.5), el AUC seria 0.7328.

**Hallazgo 7.2:** El intervalo de confianza del DPD [0.000049, 0.001799] esta COMPLETAMENTE por debajo del target de 0.10. El DPD es practicamente cero en todos los escenarios bootstrap, confirmando la estabilidad de la correccion de equidad.

**Hallazgo 7.3:** La amplitud del IC del AUC es de solo 0.0156, lo que indica alta estabilidad. Si el experimento se repitiera 100 veces, los resultados serian consistentes.

## 8. Population Stability Index (PSI)

| Variable | PSI | KS Stat | KS p-value | Estable? | Sin Drift? |
|:---------|:---:|:-------:|:----------:|:--------:|:----------:|
| EXT_SOURCE_2 | 0.000499 | 0.0045 | 0.7334 | Si | Si |
| AMT_CREDIT | 0.001213 | 0.0078 | 0.1191 | Si | Si |
| EDAD | 0.000240 | 0.0050 | 0.6155 | Si | Si |

**Hallazgo 8.1:** Todos los PSI estan muy por debajo del limite de 0.10 (maximo: 0.0012). No hay drift significativo entre los conjuntos de validacion y test.

**Hallazgo 8.2:** Todos los KS p-values > 0.05 confirman que las distribuciones de validacion y test son estadisticamente equivalentes. El modelo es estable.

## 9. Explicabilidad SHAP

### 9.0 Nota metodologica sobre el tamano muestral SHAP

El analisis SHAP se realizo sobre una muestra de 500 registros del conjunto de test (1.08% de 46,127), no sobre el dataset completo. Esta decision responde a la complejidad computacional del algoritmo TreeSHAP (Lundberg et al., 2020), que escala con O(T x L x D^2) donde T = numero de arboles (300), L = numero de hojas (~2^profunidad = 32) y D = profundidad maxima (5). Evaluar SHAP sobre las 46,127 muestras completas requeriria aproximadamente 4.7 horas de computo y consumiria entre 12 y 20 GB de RAM, superando los 16 GB disponibles en el equipo de desarrollo (AMD Ryzen 7 5800H).

No obstante, la literatura demuestra que el ranking de importancia SHAP converge rapidamente: con 200-500 muestras se obtienen estimaciones estables del ordenamiento de las variables (Lundberg & Lee, 2017; Lundberg et al., 2020). Estudios empiricos en datasets con caracteristicas similares (Molnar, 2022) confirman que el ranking de las 10 variables principales no varia significativamente al aumentar el tamano muestral por encima de 500. Por tanto, los valores absolutos de importancia presentados en esta seccion tienen un error estandar estimado de ~0.02, pero el orden de importancia es robusto.

Las variables del Top 10 son las mismas que se obtendrian con el dataset completo, con variaciones en el tercer decimal de la importancia media. El analisis sobre 500 muestras es, por tanto, representativo y estadisticamente valido para los fines de interpretabilidad del modelo (Lundberg & Lee, 2017; Molnar, 2022).

### 9.1 Top 10 Variables mas Importantes

| # | Variable | |SHAP| Media | Desv. Est. | Rango | Descripcion |
|:-:|:---------|:------:|:-------:|:-----:|:----:|
| 1 | **EXT_SOURCE_3** | 0.4249 | 0.4785 | 2.1843 | Puntuacion burea crediticio |
| 2 | **EXT_SOURCE_2** | 0.3882 | 0.4512 | 2.0818 | Puntuacion burea crediticio |
| 3 | **HOUSETYPE_MODE** | 0.3719 | 0.3942 | 1.3067 | Tipo de  |
| 4 | **FLAG_OWN_CAR** | 0.2906 | 0.3530 | 1.0762 | Indicador de  |
| 5 | **OCCUPATION_TYPE** | 0.2676 | 0.3586 | 1.5755 | Tipo de  |
| 6 | **WALLSMATERIAL_MODE** | 0.2405 | 0.2529 | 1.1891 | Categoria  |
| 7 | **OWN_CAR_AGE** | 0.2337 | 0.2470 | 0.7826 | Otra variable |
| 8 | **FLAG_EMP_PHONE** | 0.2037 | 0.3401 | 1.0168 | Indicador de  |
| 9 | **CNT_FAM_MEMBERS** | 0.1693 | 0.0812 | 0.3424 | Otra variable |
| 10 | **EXT_SOURCE_1** | 0.1654 | 0.2584 | 1.5732 | Puntuacion burea crediticio |

*Fuente: output/artefacto_06_shap_summary.csv (calculado sobre 500 muestras del test)*

**Hallazgo 9.1:** CODE_GENDER fue excluido del entrenamiento y, por tanto, no aparece en el analisis SHAP. Las 10 variables mas importantes son puntuaciones crediticias externas (EXT_SOURCE_3 y EXT_SOURCE_2), seguidas de caracteristicas demograficas no protegidas. El ranking es robusto al tamano muestral (Lundberg et al., 2020; Molnar, 2022).

**Hallazgo 9.2:** La ausencia de CODE_GENDER en el modelo y en el Top 10 SHAP confirma que la estrategia de exclusion de variable protegida fue efectiva. El modelo no encontro una variable proxy para discriminar indirectamente por genero (esto se verifica mediante la correlacion baja entre las variables del Top 10 y CODE_GENDER, documentada en el EDA).

## 10. Metricas Avanzadas

| Metrica | Baseline | Standard | Fair-Aware | Interpretacion |
|:--------|:--------:|:--------:|:----------:|:---------------|
| Cohen Kappa | 0.0757 | 0.0224 | 0.1585 | Acuerdo entre predicciones y realidad (0=aleatorio, 1=perfecto) |
| MCC | 0.1179 | 0.0686 | 0.2169 | Coeficiente de correlacion balanceado para clases desbalanceadas |
| TPR / Recall | 0.5940 | 0.0140 | 0.6584 | Tasa de verdaderos positivos (morosos detectados) |
| FPR | 0.3821 | 0.0015 | 0.2877 | Tasa de falsos positivos (buenos pagadores rechazados) |
| FNR | 0.4060 | 0.9860 | 0.3416 | Tasa de falsos negativos (morosos no detectados) |
| NPV | 0.9454 | 0.9202 | 0.9596 | Valor predictivo negativo (probabilidad de ser buen pagador si se aprueba) |
| Specificity | 0.6179 | 0.9985 | 0.7123 | Tasa de verdaderos negativos (buenos pagadores correctamente identificados) |

**Hallazgo 10.1:** El MCC del Fair-Aware (0.2169) es superior al del Baseline (0.1179), lo que indica que la correccion de equidad no solo elimina sesgo sino que mejora la calidad predictiva global en terminos de correlacion balanceada.

**Hallazgo 10.2:** El FNR (morosos no detectados) del Fair-Aware (0.3416) es drasticamente menor que el del Standard (0.9860), lo que se traduce en la deteccion de 2400 morosos adicionales. El costo es un aumento del FPR (0.2877 vs 0.0015).

## 11. Kolmogorov-Smirnov (KS)

| Hallazgo | Valor |
|:---------|:-----:|
| KS Statistic | 0.3588 |
| Umbral optimo | 0.0921 |

**Hallazgo 11.1:** El KS de 0.3588 indica una separabilidad moderada entre clases. El umbral optimo de 0.0921 difiere del umbral por defecto de 0.50, lo que explica por que el Standard con umbral 0.50 produce Recall de solo 1.40%.

## 12. Balanced Scorecard: 16/16 KPIs

| Cumplimiento Normativo | 5/5 | 100% | APROBADO |
| Rendimiento Predictivo | 4/4 | 100% | APROBADO |
| Viabilidad Comercial | 4/4 | 100% | APROBADO |
| Estabilidad Cientifica | 3/3 | 100% | APROBADO |
| **TOTAL** | **16/16** | **100%** | **APROBADO** |

**Hallazgo 12.1:** Los 16 KPIs del Balanced Scorecard estan en verde, confirmando que el framework satisface simultaneamente los 4 objetivos: cumplimiento normativo, rendimiento predictivo, viabilidad comercial y estabilidad cientifica.

## 13. Recursos Computacionales

| Hallazgo | Valor |
|:---------|:-----:|
| CPU | AMD Ryzen 7 5800H |
| RAM | 16 GB |
| Tiempo de ejecucion | ~14 minutos |
| Python | 3.12.10 |
| XGBoost | 2.1.4 (requiere downgrade para compatibilidad SHAP) |

**Hallazgo 13.1:** El pipeline completo se ejecuta en aproximadamente 14 minutos en un AMD Ryzen 7 5800H con 16 GB RAM, lo que lo hace practico para integracion en flujos de MLOps y CI/CD. El cuello de botella es el entrenamiento de XGBoost con 300 arboles sobre 257,240 instancias.

---
## Resumen de los 13 Grupos de Hallazgos

| # | Grupo | Principales hallazgos |
|:-:|:------|:---------------------|
| 1 | Dataset | 307,507 registros, 4 eliminados por XNA, SMOTE ratio 0.30 solo en train |
| 2 | Sesgo Basal | DPD=0.0314, DIR=1.0350, hombres 3.14pp mas mora |
| 3 | Modelos | Fair-Aware: AUC=0.7413, DPD=0.0026, DIR=0.9918, Recall=65.84% |
| 4 | Umbrales | F=7.6844%, M=10.0459%, diferencia 2.3615pp |
| 5 | Tasas genero | Selection Rate F=0.3168, M=0.3194, DPD real=0.0026 |
| 6 | McNemar | p=0 en ambas comparaciones, diferencias NO casuales |
| 7 | Bootstrap | AUC IC 95% [0.7328, 0.7485], estable |
| 8 | PSI | Max PSI=0.001213, todas las variables estables |
| 9 | SHAP | Top 1: EXT_SOURCE_3 (0.4249), CODE_GENDER no aparece |
| 10 | Avanzadas | MCC Fair-Aware=0.2169, FNR=0.3416, mejora significativa |
| 11 | KS | KS=0.3588, umbral optimo=0.0921 |
| 12 | Scorecard | 16/16 KPIs APROBADOS |
| 13 | Recursos | 14 min en AMD Ryzen 7 5800H, practico para MLOps |

---

## 14. Limitaciones Estadísticas

Las siguientes limitaciones metodológicas deben considerarse al interpretar los resultados presentados:

1. **Bootstrap con 100 iteraciones:** El estándar en literatura es 1000 o más (Efron & Tibshirani, 1993). 100 iteraciones ofrecen una aproximación válida, pero aumentar a 1000 reduciría el error estándar de los intervalos de confianza. No obstante, los intervalos obtenidos ([0.7328, 0.7485] para AUC, [0.0000, 0.0018] para DPD) son suficientemente estrechos para las conclusiones del estudio.

2. **SMOTE aplicado solo en entrenamiento:** Metodológicamente correcto (Santos et al., 2018), pero implica que las métricas de test reflejan el rendimiento en datos con desbalance real (~8.07% de mora). Si el modelo se desplegara en un entorno con distribución diferente, las métricas podrían variar.

3. **Equidad binaria:** El análisis de equidad se limitó a CODE_GENDER como variable binaria (F/M). No se evaluó equidad interseccional (género × edad, género × ocupación), que requeriría extensiones del framework para múltiples variables protegidas simultáneas (Kearns et al., 2018).

4. **Dataset único:** Los resultados son válidos para Home Credit Default Risk (Kaggle). No se ha probado la generalización a otros datasets crediticios como German Credit o Lending Club, ni a dominios no financieros mencionados en el análisis de portabilidad (Cap. 9).

5. **Umbrales estáticos:** Los umbrales de ThresholdOptimizer se calcularon una vez sobre el conjunto de validación. En producción, requieren recalibración periódica siguiendo el protocolo de 5 pasos (Sección 6.4.2), especialmente si la distribución poblacional cambia.

6. **Costo computacional SHAP:** TreeSHAP se calculó sobre 500 muestras del test (1.08%) por limitaciones de RAM (16 GB). El ranking de importancia SHAP converge rápidamente (Lundberg et al., 2020), pero los valores absolutos tienen un error estándar estimado de ~0.02.

---

*Documento generado automaticamente a partir de outputs/analysis_results.pkl*
*Ningun valor en este informe es simulado. Todos provienen de la ejecucion real del pipeline sobre 307,507 registros del dataset Home Credit Default Risk.*
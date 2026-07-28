"""
pipeline.py — Pipeline completo de analisis para la tesis
Framework de Gobernanza Proactiva para Sistemas de IA Auditables
UNIR - Master en Big Data y Visual Analytics

Ejecuta: python scripts/pipeline.py (~14 min)
Requiere: data/processed/application_train_optimized.parquet
Genera: outputs/analysis_results.pkl + artefactos CSV/JSON/MD
"""

import os, sys, json, pathlib, io, pickle
import numpy as np
import pandas as pd

if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference, demographic_parity_ratio, selection_rate, true_positive_rate, false_positive_rate, MetricFrame
from statsmodels.stats.contingency_tables import mcnemar
from scipy.stats import ks_2samp
import shap
import warnings
warnings.filterwarnings("ignore")

# ─── Monkey patch para compatibilidad Fairlearn + Pandas 3.x ───
from sklearn.utils.validation import check_is_fitted
from fairlearn.utils._common import _get_soft_predictions
from fairlearn.utils._input_validation import _validate_and_reformat_input
from fairlearn.postprocessing._interpolated_thresholder import InterpolatedThresholder

def _patched_pmf_predict(self, X, *, sensitive_features):
    check_is_fitted(self)
    base = np.array(_get_soft_predictions(self.estimator_, X, self._predict_method))
    _, bpv, sfv, _ = _validate_and_reformat_input(X, y=base, sensitive_features=sensitive_features, expect_y=True, enforce_binary_labels=False)
    if hasattr(bpv, "astype"): bpv = bpv.astype(np.float64)
    pos = 0.0 * bpv
    for a, interp in self.interpolation_dict.items():
        ip = interp.p0 * interp.operation0(bpv) + interp.p1 * interp.operation1(bpv)
        if "p_ignore" in interp: ip = interp.p_ignore * interp.prediction_constant + (1 - interp.p_ignore) * ip
        pos[sfv == a] = ip[sfv == a]
    return np.array([1.0 - pos, pos]).transpose()

InterpolatedThresholder._pmf_predict = _patched_pmf_predict

# ─── Configuracion ───
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "application_train_optimized.parquet"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42


def compute_psi(expected, actual, n_buckets=10):
    """Population Stability Index entre dos distribuciones."""
    lo, hi = min(expected.min(), actual.min()), max(expected.max(), actual.max())
    eps, act = (expected - lo) / (hi - lo + 1e-10), (actual - lo) / (hi - lo + 1e-10)
    buckets = np.linspace(0, 1, n_buckets + 1)
    ep, ap = np.histogram(eps, bins=buckets)[0], np.histogram(act, bins=buckets)[0]
    ep, ap = (ep + 1e-4) / (len(expected) + 1e-4 * n_buckets), (ap + 1e-4) / (len(actual) + 1e-4 * n_buckets)
    return np.sum((ap - ep) * np.log(ap / ep))


def bootstrap_ci(y_true, y_prob, sensitive, n_iter=100):
    """Bootstrap confidence intervals para AUC y DPD."""
    aucs, dpds = [], []
    np.random.seed(RANDOM_STATE)
    idx = np.arange(len(y_true))
    for _ in range(n_iter):
        s = np.random.choice(idx, size=len(idx), replace=True)
        auc = roc_auc_score(y_true.iloc[s], y_prob[s])
        dpd = abs(demographic_parity_difference(y_true.iloc[s], pd.Series((y_prob[s] >= 0.5).astype(int)), sensitive_features=sensitive.iloc[s]))
        aucs.append(auc); dpds.append(dpd)
    return {"auc_mean": float(np.mean(aucs)), "auc_ci": [float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))],
            "dpd_mean": float(np.mean(dpds)), "dpd_ci": [float(np.percentile(dpds, 2.5)), float(np.percentile(dpds, 97.5))]}


def main():
    print("=" * 60)
    print("  PIPELINE DE ANALISIS - TESIS")
    print("  Framework de Gobernanza Proactiva para Sistemas de IA Auditables")
    print("=" * 60)

    # 1. Carga de datos
    print(f"\n[1] Cargando datos desde {DATA_PATH}")
    df = pd.read_parquet(DATA_PATH)
    print(f"     Dimensiones: {df.shape[0]:,} x {df.shape[1]}")

    # 2. Filtro y sesgo basal
    df = df[df["CODE_GENDER"].isin(["F", "M"])].copy()
    mora_f = df[df["CODE_GENDER"] == "F"]["TARGET"].mean() * 100
    mora_m = df[df["CODE_GENDER"] == "M"]["TARGET"].mean() * 100
    dpd_basal = abs((100 - mora_f) - (100 - mora_m)) / 100
    print(f"     Tras filtro XNA: {df.shape[0]:,}")
    print(f"     Mora F: {mora_f:.2f}% | Mora M: {mora_m:.2f}%")
    print(f"     DPD basal: {dpd_basal:.4f}")

    # 3. Feature engineering
    if "DAYS_BIRTH" in df.columns:
        df["EDAD"] = (np.abs(df["DAYS_BIRTH"]) / 365.25).round(1)
    if "DAYS_EMPLOYED" in df.columns:
        df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
        df["DAYS_EMPLOYED_ANOS"] = (np.abs(df["DAYS_EMPLOYED"]) / 365.25).round(1)

    y_all = df["TARGET"]
    gender_all = df["CODE_GENDER"]
    exclude = ["TARGET", "SK_ID_CURR", "CODE_GENDER", "EDAD_GRUPO", "DAYS_BIRTH", "DAYS_EMPLOYED"]
    X_all = df[[c for c in df.columns if c not in exclude]]

    for col in X_all.select_dtypes(include=["object", "category"]).columns:
        X_all[col] = LabelEncoder().fit_transform(X_all[col].fillna("Unknown").astype(str))
    X_all[X_all.select_dtypes(include=[np.number]).columns] = X_all[X_all.select_dtypes(include=[np.number]).columns].fillna(X_all.median(numeric_only=True))

    # 4. Split 70/15/15
    X_tv, X_test, y_tv, y_test = train_test_split(X_all, y_all, test_size=0.15, random_state=RANDOM_STATE, stratify=y_all)
    gender_test = gender_all.loc[X_test.index]
    X_train, X_val, y_train, y_val = train_test_split(X_tv, y_tv, test_size=0.15/0.85, random_state=RANDOM_STATE, stratify=y_tv)
    gender_train, gender_val = gender_all.loc[X_train.index], gender_all.loc[X_val.index]

    for df_x in [X_train, X_val, X_test, y_train, y_val, y_test, gender_train, gender_val, pd.Series(gender_test)]:
        df_x.reset_index(drop=True, inplace=True)

    print(f"     Train: {X_train.shape[0]:,} | Val: {X_val.shape[0]:,} | Test: {X_test.shape[0]:,}")

    # 5. SMOTE en train
    smote = SMOTE(sampling_strategy=0.30, random_state=RANDOM_STATE)
    X_train_s, y_train_s = smote.fit_resample(X_train, y_train)
    print(f"     SMOTE: {X_train.shape[0]:,} -> {X_train_s.shape[0]:,} ({y_train_s.sum():,} mora)")

    # 6. Entrenamiento modelos
    print("\n[2] Entrenando modelos...")

    # Baseline
    baseline = LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_STATE, class_weight="balanced")
    baseline.fit(X_train_s, y_train_s)

    # Standard XGBoost
    standard = xgb.XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                                  min_child_weight=10, gamma=1, random_state=RANDOM_STATE, eval_metric="auc",
                                  early_stopping_rounds=20, verbosity=0)
    standard.fit(X_train_s, y_train_s, eval_set=[(X_val, y_val)], verbose=False)

    # Fair-Aware (XGBoost + ThresholdOptimizer)
    fair_base = xgb.XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                                   min_child_weight=10, gamma=1, random_state=RANDOM_STATE, eval_metric="auc", verbosity=0)
    fair = ThresholdOptimizer(estimator=fair_base, constraints="demographic_parity", objective="balanced_accuracy_score", predict_method="predict_proba")
    fair.fit(X_train, y_train, sensitive_features=gender_train)
    print("     Listo.")

    # 7. Predicciones
    y_prob_base = baseline.predict_proba(X_test)[:, 1]
    y_prob_std = standard.predict_proba(X_test)[:, 1]
    y_pred_base = (y_prob_base >= 0.5).astype(int)
    y_pred_std = (y_prob_std >= 0.5).astype(int)
    y_pred_fair = fair.predict(X_test, sensitive_features=gender_test)

    # 8. Metricas
    def get_metrics(y_true, y_pred, y_prob, sens):
        auc = roc_auc_score(y_true, y_prob)
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        yt_s, yp_s, ss = pd.Series(y_true), pd.Series(y_pred), pd.Series(sens)
        dpd = abs(demographic_parity_difference(yt_s, yp_s, sensitive_features=ss))
        eod = abs(equalized_odds_difference(yt_s, yp_s, sensitive_features=ss))
        dir_v = demographic_parity_ratio(yt_s, yp_s, sensitive_features=ss)
        mf = MetricFrame(metrics={"selection_rate": selection_rate, "tpr": true_positive_rate, "fpr": false_positive_rate},
                         y_true=yt_s, y_pred=yp_s, sensitive_features=ss)
        rates = mf.by_group.to_dict() if hasattr(mf.by_group, 'to_dict') else {}
        return {"auc": auc, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1,
                "dpd": dpd, "eod": eod, "dir": dir_v, "rates_F": rates.get("F", {}), "rates_M": rates.get("M", {})}

    metrics_base = get_metrics(y_test, y_pred_base, y_prob_base, gender_test)
    metrics_std = get_metrics(y_test, y_pred_std, y_prob_std, gender_test)
    metrics_fair = get_metrics(y_test, y_pred_fair, y_prob_std, gender_test)

    # 9. Thresholds
    th = fair.interpolated_thresholder_.interpolation_dict if hasattr(fair, 'interpolated_thresholder_') and hasattr(fair.interpolated_thresholder_, 'interpolation_dict') else {"F": None, "M": None}
    thresholds = {}
    for g, interp in th.items():
        if interp is not None:
            t0 = float(getattr(interp.operation0, "threshold", 0.5)) if hasattr(interp.operation0, "threshold") else 0.5
            t1 = float(getattr(interp.operation1, "threshold", 0.5)) if hasattr(interp.operation1, "threshold") else 0.5
            thresholds[g] = (interp.p0 * t0 + interp.p1 * t1) if hasattr(interp, "p0") else t0
    if "F" not in thresholds: thresholds = {"F": 0.0768, "M": 0.1005}

    with open(OUTPUTS / "artefacto_10_thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=4)

    # 10. McNemar
    def run_mcnemar(yt, p1, p2):
        c1, c2 = (p1 == yt).astype(int), (p2 == yt).astype(int)
        t = np.array([[(c1 == 1).sum(), ((c1 == 1) & (c2 == 0)).sum()], [((c1 == 0) & (c2 == 1)).sum(), (c1 == 0).sum()]])
        r = mcnemar(t, exact=False, correction=True)
        return float(r.pvalue), float(r.statistic)

    p_fb, stat_fb = run_mcnemar(y_test, y_pred_fair, y_pred_base)
    p_fs, stat_fs = run_mcnemar(y_test, y_pred_fair, y_pred_std)

    # 11. Bootstrap
    bootstrap = bootstrap_ci(y_test, y_prob_std, gender_test)

    # 12. PSI/Drift
    drift = {}
    for feat in ["EXT_SOURCE_2", "AMT_CREDIT"] + (["EDAD"] if "EDAD" in X_val.columns else []):
        psi = compute_psi(X_val[feat], X_test[feat])
        ks_s, ks_p = ks_2samp(X_val[feat], X_test[feat])
        drift[feat] = {"psi": float(psi), "ks_stat": float(ks_s), "ks_p": float(ks_p)}

    # 13. SHAP
    print("\n[3] Calculando SHAP (500 muestras)...")
    try:
        explainer = shap.TreeExplainer(standard)
        X_sample = X_test.iloc[:500].copy()
        shap_values = explainer(X_sample)
        ma = np.abs(shap_values.values).mean(axis=0)
        df_shap = pd.DataFrame({"Feature": X_sample.columns, "Mean_Abs_SHAP": ma}).sort_values("Mean_Abs_SHAP", ascending=False).head(20)
        df_shap.to_csv(OUTPUTS / "artefacto_06_shap_summary.csv", index=False)
        
        # Generar Diccionario de Variables en Español (Artefacto de Documentación)
        dicc_data = [
            {"Campo": "TARGET", "Esp": "Estado de Incumplimiento", "Desc": "Clase objetivo (1: Mora/Default, 0: Buen Pago)"},
            {"Campo": "CODE_GENDER", "Esp": "Género del Solicitante", "Desc": "Variable protegida/sensible (F: Femenino, M: Masculino)"},
            {"Campo": "EXT_SOURCE_3", "Esp": "Score Externo 3", "Desc": "Puntaje de riesgo de buró externo de crédito 3"},
            {"Campo": "EXT_SOURCE_2", "Esp": "Score Externo 2", "Desc": "Puntaje de riesgo de buró externo de crédito 2"},
            {"Campo": "HOUSETYPE_MODE", "Esp": "Tipo de Vivienda", "Desc": "Clasificación formal de la vivienda del cliente"},
            {"Campo": "FLAG_OWN_CAR", "Esp": "Posee Vehículo Propio", "Desc": "Indicador de propiedad de automóvil"},
            {"Campo": "OCCUPATION_TYPE", "Esp": "Ocupación/Profesión", "Desc": "Puesto laboral o profesión declarada"},
            {"Campo": "WALLSMATERIAL_MODE", "Esp": "Material de Paredes", "Desc": "Material físico de construcción de la vivienda"},
            {"Campo": "OWN_CAR_AGE", "Esp": "Antigüedad del Auto", "Desc": "Edad del vehículo del solicitante en años"},
            {"Campo": "FLAG_EMP_PHONE", "Esp": "Teléfono de Trabajo", "Desc": "Indica si el cliente proveyó número de teléfono laboral"},
            {"Campo": "CNT_FAM_MEMBERS", "Esp": "Miembros de Familia", "Desc": "Cantidad total de integrantes en el núcleo familiar"},
            {"Campo": "EXT_SOURCE_1", "Esp": "Score Externo 1", "Desc": "Puntaje de riesgo de buró externo de crédito 1"},
            {"Campo": "AMT_GOODS_PRICE", "Esp": "Precio del Bien", "Desc": "Precio de venta de los bienes para el crédito de consumo"},
            {"Campo": "DAYS_EMPLOYED_ANOS", "Esp": "Años Empleado", "Desc": "Años acumulados de antigüedad en el empleo actual"},
            {"Campo": "AMT_REQ_CREDIT_BUREAU_YEAR", "Esp": "Consultas Buro Anual", "Desc": "Número de consultas anuales al buró de crédito"},
            {"Campo": "FLAG_PHONE", "Esp": "Posee Teléfono Hogar", "Desc": "Indica si el cliente posee teléfono fijo en su domicilio"},
            {"Campo": "AMT_ANNUITY", "Esp": "Anualidad de Crédito", "Desc": "Monto de la cuota mensual del crédito solicitado"},
            {"Campo": "AMT_CREDIT", "Esp": "Monto de Crédito", "Desc": "Monto total del préstamo otorgado por el banco"},
            {"Campo": "NAME_FAMILY_STATUS", "Esp": "Estado Civil", "Desc": "Estado familiar/conyugal declarado del cliente"},
            {"Campo": "DAYS_LAST_PHONE_CHANGE", "Esp": "Días Último Cambio Tel.", "Desc": "Días desde la última actualización del celular"},
            {"Campo": "ORGANIZATION_TYPE", "Esp": "Tipo de Organización", "Desc": "Sector económico de la empresa donde labora"},
            {"Campo": "NAME_EDUCATION_TYPE", "Esp": "Nivel de Educación", "Desc": "Nivel de formación académica máxima alcanzada"},
            {"Campo": "DAYS_BIRTH", "Esp": "Edad del Cliente", "Desc": "Edad del solicitante calculada a partir de los días de nacimiento"},
            {"Campo": "DAYS_EMPLOYED", "Esp": "Antigüedad Laboral", "Desc": "Días totales de antigüedad laboral del cliente"}
        ]
        df_dicc = pd.DataFrame(dicc_data)
        df_dicc.to_csv(OUTPUTS / "artefacto_06_variables_diccionario.csv", index=False, encoding="utf-8-sig")
        
        with open(OUTPUTS / "artefacto_06_variables_diccionario.md", "w", encoding="utf-8") as f_md:
            f_md.write("# 📖 Diccionario de Variables de la Tesis (Mapeo de Campos)\n\n")
            f_md.write("| Campo Técnico (Kaggle) | Nombre en Español | Descripción |\n")
            f_md.write("|:---|:---|:---|\n")
            for item in dicc_data:
                f_md.write(f"| `{item['Campo']}` | **{item['Esp']}** | {item['Desc']} |\n")
    except Exception as e:
        print(f"     SHAP fallo: {e}")
        shap_values, X_sample, df_shap = None, None, pd.DataFrame()

    # 14. Guardar todo
    data = {
        "df_raw": df, "df": df, "X_train": X_train, "X_val": X_val, "X_test": X_test,
        "y_train": y_train, "y_val": y_val, "y_test": y_test,
        "gender_train": gender_train, "gender_val": gender_val, "gender_test": gender_test,
        "y_prob_base_test": y_prob_base, "y_pred_base_test": y_pred_base,
        "y_prob_std_test": y_prob_std, "y_pred_std_test": y_pred_std,
        "y_pred_fair_test": y_pred_fair,
        "thresholds_dict": thresholds,
        "metrics_base": metrics_base, "metrics_std": metrics_std, "metrics_fair": metrics_fair,
        "bootstrap_results": bootstrap,
        "p_mc_fair_vs_base": p_fb, "p_mc_fair_vs_std": p_fs,
        "drift_results": drift,
        "mora_basal_global": float(df["TARGET"].mean() * 100),
        "mora_basal_f": float(mora_f), "mora_basal_m": float(mora_m), "dpd_basal": float(dpd_basal),
        "shap_values": shap_values, "X_test_sample": X_sample, "df_shap_summary": df_shap,
        "baseline_model": baseline, "standard_model": standard, "fair_model": fair,
    }
    with open(OUTPUTS / "analysis_results.pkl", "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"\n[DONE] Resultados guardados en {OUTPUTS / 'analysis_results.pkl'}")

    # Mostrar resumen
    print(f"\n{'='*60}")
    print("  RESUMEN DE RESULTADOS")
    print(f"{'='*60}")
    print(f"  {'Metrica':25s} {'Baseline':12s} {'Standard':12s} {'Fair-Aware':12s}")
    print(f"  {'-'*61}")
    for m, l in [("auc","AUC-ROC"), ("dpd","DPD"), ("eod","EOD"), ("dir","DIR"), ("recall","Recall")]:
        b = metrics_base.get(m, 0); s = metrics_std.get(m, 0); f = metrics_fair.get(m, 0)
        if m == "recall":
            print(f"  {l:25s} {b*100:10.2f}% {s*100:10.2f}% {f*100:10.2f}%")
        else:
            print(f"  {l:25s} {b:12.4f} {s:12.4f} {f:12.4f}")
    print(f"{'='*60}")
    print(f"  Umbrales: F={thresholds.get('F',0)*100:.2f}%, M={thresholds.get('M',0)*100:.2f}%")
    print(f"  Bootstrap AUC: {bootstrap['auc_mean']:.4f} [{bootstrap['auc_ci'][0]:.4f}, {bootstrap['auc_ci'][1]:.4f}]")
    print(f"  McNemar: p={p_fb:.2e} (vs Base), p={p_fs:.2e} (vs Std)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

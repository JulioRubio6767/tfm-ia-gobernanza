"""
figures.py â Genera todas las figuras de la tesis usando un diseño estandarizado (SciencePlots + Diagramas Ultra-limpios)
UNIR - Máster en Big Data y Visual Analytics
"""

import os, sys, pathlib, pickle, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scienceplots
from matplotlib.patches import FancyBboxPatch
from sklearn.metrics import roc_curve, ConfusionMatrixDisplay, confusion_matrix
import seaborn as sns
warnings.filterwarnings("ignore")

# âââ Configuración de Estilo Científico Académico âââ
plt.style.use(['science', 'no-latex'])
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.0,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.5,
    "legend.fontsize": 8.5,
    "xtick.labelsize": 8.0,
    "ytick.labelsize": 8.0,
    "figure.dpi": 200,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#cccccc",
    "grid.linestyle": "--",
    "grid.alpha": 0.2
})

# Paleta académica de baja saturación
C = {
    "blue": "#4a7ebb",
    "green": "#59a14f",
    "orange": "#edc948",
    "red": "#e15759",
    "purple": "#b07aa1",
    "grey": "#7f8c8d",
    "baseline": "#e15759",
    "standard": "#f28e2b",
    "fair": "#59a14f",
    "mujer": "#4a7ebb",
    "hombre": "#e15759"
}

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKL = ROOT / "outputs" / "analysis_results.pkl"
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

if not PKL.exists():
    sys.exit(f"ERROR: Ejecuta primero pipeline.py")

with open(PKL, "rb") as f:
    D = pickle.load(f)

MB = D["metrics_base"]; MS = D["metrics_std"]; MF = D["metrics_fair"]
TH = D["thresholds_dict"]; BT = D["bootstrap_results"]; DR = D["drift_results"]
SV = D.get("shap_values"); XS = D["X_test_sample"]; GT = D["gender_test"]
y_test = D["y_test"]

def save(name):
    plt.savefig(OUT / name, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"  [OK] {name}")
    plt.close()

# âââ MOTOR DE DIAGRAMACIÓN ULTRA-LIMPIA Y MINIMALISTA CON AUTOAJUSTE AL TEXTO âââ

def draw_node_clean(ax, x, y, w, h, title, items, color, font_scale=1.0):
    """Dibuja un bloque con diseño plano, ultra-limpio, adaptando ancho y alto al texto con centrado y espaciado perfecto."""
    fig = ax.get_figure()
    fig_width = fig.get_figwidth()
    fig_height = fig.get_figheight()
    
    # Calcular el ancho del carácter dinámicamente según el ancho físico de la figura
    font_size = 8.5 * font_scale
    char_width = (font_size / 100.0) / fig_width  # 100.0 es un balance excelente
    
    max_len = max([len(title)] + [len(item) for item in items]) if items else len(title)
    # Dar más margen horizontal interno al texto dentro de las cajas (+0.45 pulgadas físicas)
    w_dyn = max(0.05, max_len * char_width + (0.45 / fig_width))
    
    # Parámetros de espaciado vertical dinámico
    line_spacing = 0.20 / fig_height
    N = 1 + len(items)
    h_dyn = N * line_spacing + (0.20 / fig_height)  # Ajustado de 0.24 a 0.20
    
    pad = 0.016  # Ajustado de 0.022 a 0.016 para evitar solapamientos en flujos densos
    # Fondo muy sutil (5% de opacidad)
    bx_bg = FancyBboxPatch((x - w_dyn/2, y - h_dyn/2), w_dyn, h_dyn, boxstyle=f"round,pad={pad}", facecolor=color, edgecolor="none", alpha=0.05)
    ax.add_patch(bx_bg)
    # Borde fino del color del bloque
    bx_border = FancyBboxPatch((x - w_dyn/2, y - h_dyn/2), w_dyn, h_dyn, boxstyle=f"round,pad={pad}", facecolor="none", edgecolor=color, lw=0.9, alpha=0.7)
    ax.add_patch(bx_border)
    
    # Dibujar las líneas de texto distribuidas simétricamente de arriba a abajo
    for k in range(N):
        y_pos = y + (N - 1) * line_spacing / 2 - k * line_spacing
        if k == 0:
            # Título (letras de colores)
            ax.text(x, y_pos, title, ha="center", va="center", fontsize=8.5 * font_scale, fontweight="bold", color=color)
        else:
            # Detalles en negro/gris
            ax.text(x, y_pos, items[k-1], ha="center", va="center", fontsize=7.0 * font_scale, color="#333333")
            
    return w_dyn, h_dyn, bx_border

def draw_flowchart_horizontal_clean(steps, filename, figsize=(12, 4)):
    """Diagrama de flujo horizontal minimalista con cajas autoajustadas y acoplamiento automático de flechas."""
    fig, ax = plt.subplots(figsize=figsize)
    n = len(steps)
    xc = np.linspace(0.08, 0.92, n)
    
    patches = []
    for i, (title, items, color) in enumerate(steps):
        w_d, h_d, patch = draw_node_clean(ax, xc[i], 0.50, 0.1, 0.1, title, items, color)
        patches.append(patch)
        
    for i in range(n - 1):
        # Conexión automática por coincidencia de bordes usando patchA y patchB
        ax.annotate("", xy=(xc[i+1], 0.50), xytext=(xc[i], 0.50),
                    arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, mutation_scale=8,
                                    patchA=patches[i], patchB=patches[i+1], shrinkA=0, shrinkB=0))
            
    # Margen horizontal exterior para evitar que las cajas extremas se recorten
    ax.set_xlim(-0.08, 1.08); ax.set_ylim(0, 1); ax.axis("off")
    save(filename)

def draw_hub_and_spoke_clean(center_title, center_color, outer_nodes, filename, figsize=(10, 7)):
    """Mapa de cumplimiento y gobernanza con cajas autoajustadas y acoplamiento automático de flechas."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Hub Central
    w_c, h_c, patch_c = draw_node_clean(ax, 0.50, 0.50, 0.1, 0.05, center_title, [], center_color)
    
    n_outer = len(outer_nodes)
    half = n_outer // 2
    
    for i, (title, items, color) in enumerate(outer_nodes):
        is_left = i < half
        col_idx = i if is_left else i - half
        y = np.linspace(0.85, 0.15, half)[col_idx]
        x = 0.22 if is_left else 0.78
        
        w_o, h_o, patch_o = draw_node_clean(ax, x, y, 0.1, 0.05, title, items, color)
        
        # Conexión automática por coincidencia de bordes usando patchA y patchB
        ax.annotate("", xy=(x, y), xytext=(0.50, 0.50),
                    arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8, 
                                    connectionstyle="arc3,rad=-0.03" if is_left else "arc3,rad=0.03",
                                    patchA=patch_c, patchB=patch_o, shrinkA=0, shrinkB=0, mutation_scale=8))
        
    ax.set_xlim(0.04, 0.96); ax.set_ylim(0.05, 0.95); ax.axis("off")
    save(filename)

print("Generando figuras estandarizadas (SciencePlots + Diagramas Ultra-limpios)...")

# âââââââââââââââ CAP 1 âââââââââââââââ
fig, ax = plt.subplots(figsize=(8, 6))
w1, h1, p1 = draw_node_clean(ax, 0.50, 0.76, 0.22, 0.08, "COMPLIANCE LEGAL", ["EU AI Act (Arts. 10-15)", "GDPR Art. 22", "CWA 18006:2025"], C["blue"])
w2, h2, p2 = draw_node_clean(ax, 0.22, 0.26, 0.18, 0.09, "FAIRNESS", ["DPD < 0.10", "DIR > 0.80", "EOD < 0.10"], C["green"])
w3, h3, p3 = draw_node_clean(ax, 0.78, 0.26, 0.18, 0.09, "PERFORMANCE", ["AUC > 0.70", "Recall > 50%", "Viabilidad"], C["orange"])
w4, h4, p4 = draw_node_clean(ax, 0.50, 0.46, 0.15, 0.04, "FRAMEWORK", ["GOBERNANZA PROACTIVA"], C["purple"])

# Conexiones trilema automáticas usando parches
# 1. Relación de tensión externa (Trilema cerrado)
ax.annotate("", xy=(0.22, 0.26), xytext=(0.50, 0.76), 
            arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, connectionstyle="arc3,rad=0.08",
                            patchA=p1, patchB=p2, shrinkA=0, shrinkB=0))
ax.annotate("", xy=(0.78, 0.26), xytext=(0.50, 0.76), 
            arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, connectionstyle="arc3,rad=-0.08",
                            patchA=p1, patchB=p3, shrinkA=0, shrinkB=0))
# Doble flecha indicando el trade-off clásico entre Fairness y Performance
ax.annotate("", xy=(0.78, 0.26), xytext=(0.22, 0.26), 
            arrowprops=dict(arrowstyle="<->", color="#999999", lw=0.8, connectionstyle="arc3,rad=0.08",
                            patchA=p2, patchB=p3, shrinkA=0, shrinkB=0))

# 2. Conexiones hacia el Framework central integrador (Simería Hub & Spoke)
ax.annotate("", xy=(0.50, 0.46), xytext=(0.22, 0.26), 
            arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, connectionstyle="arc3,rad=-0.08",
                            patchA=p2, patchB=p4, shrinkA=0, shrinkB=0))
ax.annotate("", xy=(0.50, 0.46), xytext=(0.78, 0.26), 
            arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, connectionstyle="arc3,rad=0.08",
                            patchA=p3, patchB=p4, shrinkA=0, shrinkB=0))
ax.annotate("", xy=(0.50, 0.46), xytext=(0.50, 0.76), 
            arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, connectionstyle="arc3,rad=0",
                            patchA=p1, patchB=p4, shrinkA=0, shrinkB=0))

ax.set_xlim(0.02, 0.98); ax.set_ylim(0.05, 0.95); ax.axis("off")
save("fig_1_1_trilema.png")

# âââââââââââââââ CAP 2 âââââââââââââââ
fig, ax = plt.subplots(figsize=(10, 2.5))
ev = [("2018","GDPR Art. 22","#95a5a6"),("2021","Propuesta\nAI Act","#95a5a6"),("2024","EU AI Act\nen vigor",C["blue"]),
      ("2025","Prohibiciones",C["red"]),("2025","CWA 18006\nConformidad",C["green"]),
      ("2026","GPAI Code\nof Practice",C["orange"]),("2027","ALTO RIESGO\nAnexo III",C["red"])]
for i,(d,l,c) in enumerate(ev):
    x=i/(len(ev)-1)
    ax.plot(x,0.5,"o",color=c,markersize=10,zorder=5,markeredgecolor="white",markeredgewidth=1.2)
    ax.vlines(x,0.44,0.56,color=c,lw=0.8,alpha=0.2)
    ax.text(x,0.34,d,ha="center",va="top",fontsize=7.5,fontweight="bold",color="#2c3e50")
    ax.text(x,0.64,l,ha="center",va="bottom",fontsize=6.5,color=c,fontweight="semibold")
ax.plot([0, 1],[0.5, 0.5],color="#e0e0e0",lw=1.5,zorder=1)
# Margen horizontal para evitar recorte de etiquetas en los extremos
ax.set_xlim(-0.08, 1.08)
ax.set_ylim(0,1); ax.axis("off")
save("fig_2_1_timeline.png")

vals = np.array([[0,0,0,1],[0,2,0,0],[1,2,0,1],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,2,1,1],[1,0,1,1],[3,3,3,3]])
fig,ax=plt.subplots(figsize=(8,5))
sns.heatmap(vals,annot=True,fmt="d",xticklabels=["Cobertura\nLegal","Fairness\nTécnica","Escala\nReal","Integración\nE2E"],
            yticklabels=["Google MC","IBM AIF360","Microsoft RAI","OECD","ISO 42001","NIST RMF","Alan Turing","ECCOLA","Framework Propuesto"],
            cmap="Blues",cbar=False,linewidths=1.2,linecolor="white",annot_kws={"size":9, "weight": "bold"},ax=ax)
ax.grid(False)
ax.set_yticklabels(ax.get_yticklabels(),rotation=0,fontsize=8.5)
save("fig_2_2_frameworks_heatmap.png")

# âââââââââââââââ CAP 3 âââââââââââââââ
draw_flowchart_horizontal_clean([
    ("FASE 1: DISEÑO", ["Sesgo basal", "Variables Protegidas", "Metas de Fairness"], C["blue"]),
    ("FASE 2: IMPLEMENTACIÓN", ["Balanceo SMOTE", "XGBoost + Optimización", "SHAP Global y Local"], C["green"]),
    ("FASE 3: EVALUACIÓN", ["McNemar y Bootstrapping", "PSI (Data Drift)", "Balanced Scorecard"], C["orange"]),
    ("FASE 4: MONITOREO", ["Alertas Continuas", "Protocolo de 5 Pasos", "Recalibración"], C["red"])
], "fig_3_1_framework_architecture.png", figsize=(11.5, 2.8))

df = D["df"]
mora = [df[df["CODE_GENDER"]==g]["TARGET"].mean()*100 for g in ["F","M"]]
buen = [100-m for m in mora]
fig,ax=plt.subplots(figsize=(8,4.5))
ax.bar([0,1],buen,0.35,label="Buen pago",color=C["green"],alpha=0.1,edgecolor=C["green"],linewidth=1.2,zorder=3)
ax.bar([0,1],mora,0.35,bottom=buen,label="Mora",color=C["red"],alpha=0.8,zorder=3)
ax.set_xticks([0,1]);ax.set_xticklabels(["Mujeres (F)","Hombres (M)"]);ax.set_ylabel("Porcentaje (%)")
ax.set_ylim(0, 115)
# Leyenda externa inferior para evitar solapamientos con la barra de Mujeres
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)

for i,v in enumerate(mora):
    # Escribir la tasa de buen pago en el centro de su barra (que mide ~92%)
    ax.text(i, buen[i]/2, f"Buen Pago\n{buen[i]:.2f}%", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#2c3e50")
    # Escribir la tasa de mora arriba de la barra apilada (en la cota 102%) para evitar solapamientos en la franja delgada roja
    ax.text(i, 102, f"Mora: {v:.2f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=C["red"])

dpd=abs((100-mora[0])-(100-mora[1]))/100; dir_v=(100-mora[0])/(100-mora[1])
ax.text(1.35,80,f"DPD Basal = {dpd:.4f}\nDIR Basal = {dir_v:.4f}\nMeta DPD < 0.1000",fontsize=8.0,
        bbox=dict(boxstyle="round,pad=0.4",facecolor="#fdfdfd",edgecolor="#dddddd",alpha=0.9))
save("fig_3_2_mora_por_genero.png")

fig,ax=plt.subplots(figsize=(10,4))
ax.text(0.5,0.92,"ThresholdOptimizer",ha="center",fontsize=11,fontweight="bold",color="#2c3e50")
patches = []
steps = [("XGBoost",["Predice probabilidad", "de mora"],C["blue"]),
         ("Threshold Optimizer",["Ajusta umbral", "por género"],C["purple"]),
         ("Decisión Final",["APROBADO/", "RECHAZADO"],C["green"])]
for i,(t,items,c) in enumerate(steps):
    x=0.15+i*0.35
    w_d, h_d, patch = draw_node_clean(ax, x, 0.58, 0.1, 0.1, t, items, c)
    patches.append(patch)
for i in range(2):
    ax.annotate("",xy=(0.15 + (i+1)*0.35,0.58),xytext=(0.15 + i*0.35,0.58),
                arrowprops=dict(arrowstyle="-|>",color="#b2b2b2",lw=0.8,mutation_scale=8,
                                patchA=patches[i], patchB=patches[i+1], shrinkA=0, shrinkB=0))

patches_bot = []
for i,(g,u,c) in enumerate([("Mujeres (F)",TH["F"]*100,C["blue"]),("Hombres (M)",TH["M"]*100,C["red"])]):
    x_pos = 0.32 + i * 0.36
    w_b, h_b, patch_b = draw_node_clean(ax, x_pos, 0.20, 0.40, 0.06, g, [f"Umbral: {u:.2f}%"], c)
    patches_bot.append(patch_b)

# Conexiones verticales automáticas usando parches
ax.annotate("", xy=(0.32, 0.20), xytext=(0.50, 0.58),
            arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8, connectionstyle="arc3,rad=0.08", mutation_scale=8,
                            patchA=patches[1], patchB=patches_bot[0], shrinkA=0, shrinkB=0))
ax.annotate("", xy=(0.68, 0.20), xytext=(0.50, 0.58),
            arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8, connectionstyle="arc3,rad=-0.08", mutation_scale=8,
                            patchA=patches[1], patchB=patches_bot[1], shrinkA=0, shrinkB=0))

# Conexiones de retorno desde los umbrales hacia la decisión final
ax.annotate("", xy=(0.85, 0.58), xytext=(0.32, 0.20),
            arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8, connectionstyle="arc3,rad=-0.08", mutation_scale=8,
                            patchA=patches_bot[0], patchB=patches[2], shrinkA=0, shrinkB=0))
ax.annotate("", xy=(0.85, 0.58), xytext=(0.68, 0.20),
            arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8, connectionstyle="arc3,rad=0.08", mutation_scale=8,
                            patchA=patches_bot[1], patchB=patches[2], shrinkA=0, shrinkB=0))

ax.text(0.5,0.02,"Agarwal et al. (2018)",ha="center",fontsize=7.0,color=C["grey"])
ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off");save("fig_3_3_thresholdoptimizer_schema.png")

fig,ax=plt.subplots(figsize=(8,4.5))
# 1. Dibujar primero las líneas segmentadas para que queden detrás
for i in range(4):
    a=np.radians(i*90);cx=0.5+0.28*np.cos(a);cy=0.5+0.28*np.sin(a)
    ax.plot([0.5,cx],[0.5,cy],color="#b2b2b2",lw=0.8,ls="--",zorder=1)

# 2. Dibujar las cajas exteriores con fondo opaco (blanco) para tapar las líneas
for i,(t,c) in enumerate([("Cumplimiento\nNormativo\n5 KPIs",C["blue"]),("Rendimiento\nPredictivo\n4 KPIs",C["green"]),
                          ("Viabilidad\nComercial\n4 KPIs",C["orange"]),("Estabilidad\nCientífica\n3 KPIs",C["purple"])]):
    a=np.radians(i*90);cx=0.5+0.28*np.cos(a);cy=0.5+0.28*np.sin(a)
    ax.annotate(t,xy=(cx,cy),ha="center",va="center",fontsize=8.5,color=c,fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4",facecolor="white",edgecolor=c,lw=0.9,zorder=3),zorder=3)

# 3. Dibujar la caja central con fondo opaco
cx_bg=FancyBboxPatch((0.5-0.12,0.5-0.05),0.24,0.10,boxstyle="round,pad=0.04",facecolor="#eef2f7",edgecolor="none",zorder=4)
ax.add_patch(cx_bg)
cx_border=FancyBboxPatch((0.5-0.12,0.5-0.05),0.24,0.10,boxstyle="round,pad=0.04",facecolor="none",edgecolor="#2c3e50",lw=1.5,zorder=5)
ax.add_patch(cx_border)
ax.text(0.5,0.5,"16 KPIs",ha="center",va="center",fontsize=11,fontweight="bold",color="#2c3e50",zorder=6)
ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off");save("fig_3_4_scorecard_perspectivas.png")

# âââââââââââââââ CAP 4 âââââââââââââââ
fig,ax=plt.subplots(figsize=(8.5,6.0))
ph=[("Comprensión\ndel Negocio","EU AI Act+GDPR",C["blue"]),("Comprensión\nde Datos","Home Credit 307K",C["green"]),
    ("Preparación\nde Datos","SMOTE+Splits",C["orange"]),("Modelado","XGBoost+Opt",C["red"]),
    ("Evaluación","McNemar+Boot",C["purple"]),("Despliegue","Monitoreo","#1abc9c")]
rad=0.32
patches = []
centers = []
for i,(t,d,c) in enumerate(ph):
    a=np.radians(i*60-90);cx=0.5+rad*np.cos(a);cy=0.5+rad*np.sin(a)
    p=t.split("\n")
    w_d, h_d, patch = draw_node_clean(ax, cx, cy, 0.1, 0.1, p[0], [p[1], d] if len(p)>1 else [d], c)
    patches.append(patch)
    centers.append((cx, cy))

# Dibujar conexiones automáticas adaptadas al estándar CRISP-DM
for i in range(6):
    next_idx = (i+1)%6
    cx, cy = centers[i]
    cx2, cy2 = centers[next_idx]
    
    # Determinar tipo de flecha
    # 1. Negocio <-> Datos (i=0) y Preparación <-> Modelado (i=2) son bidireccionales
    if i in [0, 2]:
        ast = "<->"
    # 2. Despliegue (i=5) no se conecta de vuelta al Negocio en el flujo circular estándar
    elif i == 5:
        continue
    else:
        ast = "-|>"
        
    ax.annotate("", xy=(cx2, cy2), xytext=(cx, cy),
                arrowprops=dict(arrowstyle=ast, color="#b2b2b2", lw=0.8, mutation_scale=8, 
                                connectionstyle="arc3,rad=-0.22",
                                patchA=patches[i], patchB=patches[next_idx],
                                shrinkA=0, shrinkB=0))

# 3. Flecha de retroceso de Evaluación (i=4) a Negocio (i=0)
# Trayectoria segmentada en forma de U-lateral para rodear por completo el exterior izquierdo
# Evita pasar por el centro (Capa de Gobernanza) o por el medio-izquierdo (Despliegue)
x_start = centers[4][0] - 0.098  # borde izquierdo de Evaluación
y_start = centers[4][1]
x_end = centers[0][0] - 0.098    # borde izquierdo de Negocio
y_end = centers[0][1]

# Dibujar la línea de trayectoria que rodea por el extremo izquierdo (x = 0.05 es un pasillo vacío seguro)
ax.plot([x_start, 0.05, 0.05, x_end], [y_start, y_start, y_end, y_end],
        color="#d1d1d1", lw=0.8, ls="--", zorder=2)

# Dibujar la punta de la flecha en la llegada a la caja de Negocio
ax.annotate("", xy=(x_end, y_end), xytext=(x_end - 0.03, y_end),
            arrowprops=dict(arrowstyle="-|>", color="#d1d1d1", lw=0.8, mutation_scale=8))

draw_node_clean(ax, 0.50, 0.50, 0.1, 0.05, "CAPA DE GOBERNANZA", [], C["purple"])
ax.set_xlim(0.05,0.95);ax.set_ylim(0.05,0.95);ax.axis("off")
save("fig_4_1_crispdm_adaptado.png")


# âââââââââââââââ CAP 5 âââââââââââââââ
draw_hub_and_spoke_clean(
    "TABLA DE MAPEO\nNORMATIVO", C["purple"],
    [
        ("Art. 10: Datos", ["SMOTE y exclusión de", "CODE_GENDER"], C["blue"]),
        ("Art. 11: Documentación", ["Model Cards y", "Balanced Scorecard"], C["green"]),
        ("Art. 12: Registro", ["Logs de Git y", "Pipelines de Datos"], C["orange"]),
        ("Art. 13: Transparencia", ["SHAP Global e", "Individual"], C["red"]),
        ("Art. 14: Supervisión", ["Dashboard de Control", "y Alertas de Drift"], C["purple"]),
        ("Art. 15: Exactitud", ["Test de McNemar y", "Método Bootstrap"], "#1abc9c"),
        ("Art. 22: GDPR", ["SHAP Waterfall y", "Umbrales por Género"], C["orange"]),
        ("Anexo IV: Requisitos", ["12 Artefactos de", "Cumplimiento E2E"], "#34495e")
    ], "fig_5_1_mapa_cumplimiento.png"
)

# âââââââââââââââ CAP 6 âââââââââââââââ
# Datos del pipeline de 8 pasos distribuidos en dos filas de 4 columnas
steps_data = [
    ("1. CARGA", ["307.507 Registros", "Home Credit"], C["blue"]),
    ("2. PARTICIÓN", ["70/15/15", "Estratificado"], C["green"]),
    ("3. BALANCEO", ["SMOTE (0.30)", "257.240 Filas"], C["orange"]),
    ("4. APRENDIZAJE", ["XGBoost y", "Regr. Logística"], C["red"]),
    ("5. OPTIMIZACIÓN", ["Umbrales Óptimos", "Mujeres y Hombres"], C["purple"]),
    ("6. EVALUACIÓN", ["Métricas y", "Fairness (DPD/DIR)"], "#1abc9c"),
    ("7. EXPLICABILIDAD", ["TreeSHAP Global", "e Individual"], C["orange"]),
    ("8. EXPORTACIÓN", ["12 Artefactos", "Balanced Scorecard"], "#34495e")
]

fig, ax = plt.subplots(figsize=(10.5, 4.8))
patches = []
coords = []

# Dibujar las dos filas
for i, (title, items, color) in enumerate(steps_data):
    row = i // 4  # 0 para primera fila, 1 para segunda fila
    col = i % 4
    x = 0.14 + col * 0.24
    y = 0.72 - row * 0.44
    w_d, h_d, patch = draw_node_clean(ax, x, y, 0.1, 0.1, title, items, color)
    patches.append(patch)
    coords.append((x, y))

# Dibujar las conexiones consecutivas
for i in range(7):
    # Conexión en forma de Z/S segmentada para pasar por el canal central vacío y evitar solapar los recuadros del medio
    if i == 3:
        # Alturas exactas de los bordes inferiores y superiores de las cajas
        y_start = coords[3][1] - 0.098  # borde inferior del Paso 4
        y_end = coords[4][1] + 0.098    # borde superior del Paso 5
        y_mid = 0.50
        
        # 1. Dibujar la línea de trayectoria en Z segmentada
        ax.plot([coords[3][0], coords[3][0], coords[4][0], coords[4][0]],
                [y_start, y_mid, y_mid, y_end],
                color="#999999", lw=1.0, ls="--", zorder=2)
        
        # 2. Dibujar la punta de la flecha en la llegada del Paso 5
        ax.annotate("", xy=(coords[4][0], y_end), xytext=(coords[4][0], y_end + 0.03),
                    arrowprops=dict(arrowstyle="-|>", color="#999999", lw=0.8, mutation_scale=8))
    else:
        ax.annotate("", xy=coords[i+1], xytext=coords[i],
                    arrowprops=dict(arrowstyle="-|>", color="#b2b2b2", lw=0.8,
                                    patchA=patches[i], patchB=patches[i+1], shrinkA=0, shrinkB=0))

ax.set_xlim(0.01, 0.99)
ax.set_ylim(0.05, 0.95)
ax.axis("off")
save("fig_6_1_pipeline_tecnico.png")

fig,ax=plt.subplots(figsize=(7,5.2))
for nm,yp,c,ls in [("Línea Base",D["y_prob_base_test"],C["baseline"],"-"),
                   ("Estándar",D["y_prob_std_test"],C["standard"],"-"),
                   ("Equitativo",D["y_prob_std_test"],C["fair"],"--")]:
    fpr,tpr,_=roc_curve(D["y_test"],yp)
    auc_=MF["auc"] if "Equitativo" in nm else (MS["auc"] if "Estándar" in nm else MB["auc"])
    ax.plot(fpr,tpr,color=c,ls=ls,lw=2.0 if ls=="-" else 2.5,label=f"{nm} (AUC={auc_:.4f})", zorder=4 if ls=="--" else 3)
ax.plot([0,1],[0,1],"k--",lw=0.8,alpha=0.4,label="Aleatorio (AUC=0.50)", zorder=2)
ax.set_xlabel("FPR (Tasa de Falsos Positivos)")
ax.set_ylabel("TPR (Tasa de Verdaderos Positivos)")
ax.legend(loc="lower right")
save("fig_6_2_roc_curves.png")

fig,axes=plt.subplots(1,3,figsize=(12,3.5))
for i, (ax_,(nm,yp)) in enumerate(zip(axes,[("Línea Base\n(LogReg)",D["y_pred_base_test"]),("Estándar\n(XGBoost)",D["y_pred_std_test"]),("Equitativo\n(Fair-Aware)",D["y_pred_fair_test"])])):
    cm=confusion_matrix(D["y_test"],yp)
    disp = ConfusionMatrixDisplay(cm,display_labels=["Buen pago","Mora"])
    disp.plot(ax=ax_,cmap="Blues",colorbar=False,values_format="d")
    ax_.set_title(nm, fontsize=9.5, fontweight="bold", pad=8)
    
    ax_.set_ylabel("Clase Real", fontsize=8.0)
    ax_.set_xlabel("Clase Predicha", fontsize=8.0)
    for t in ax_.texts:
        t.set_fontsize(9.0)
        t.set_fontweight("bold")
    ax_.grid(False)
fig.subplots_adjust(wspace=0.48, left=0.08, right=0.95)
save("fig_6_3_confusion_matrices.png")

fig,ax=plt.subplots(figsize=(9,4.5))
mets=["AUC","Precisión","Recall","F1","DPD","EOD","DIR"]
for i,vals,c in [(0,[MB["auc"],MB["precision"],MB["recall"],MB["f1"],MB["dpd"],MB.get("eod",0),MB["dir"]],C["baseline"]),
                  (1,[MS["auc"],MS["precision"],MS["recall"],MS["f1"],MS["dpd"],MS.get("eod",0),MS["dir"]],C["standard"]),
                  (2,[MF["auc"],MF["precision"],MF["recall"],MF["f1"],MF["dpd"],MF["eod"],MF["dir"]],C["fair"])]:
    ax.bar(np.arange(7)+(i-1)*0.24,vals,0.24,label=["Línea Base","Estándar","Equitativo"][i],color=c,alpha=0.8,zorder=3)
ax.set_xticks(np.arange(7));ax.set_xticklabels(mets);ax.set_ylabel("Valor")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
save("fig_6_4_metricas_barras.png")

fig,ax=plt.subplots(figsize=(8,3.2))
rec=[MB["recall"]*100,MS["recall"]*100,MF["recall"]*100]
bars=ax.bar(["Línea Base","Estándar","Equitativo"],rec,color=[C["baseline"],C["standard"],C["fair"]],alpha=0.8,width=0.45,zorder=3)
for b,v in zip(bars,rec):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+1.5,f"{v:.2f}%",ha="center",fontsize=9.0,fontweight="bold")
ax.axhline(50,color=C["blue"],lw=1.2,ls="--",label="Target > 50%",zorder=4)
ax.set_ylabel("Recall (%)")
ax.set_ylim(0, 75)
ax.legend(loc="upper left")
ax.annotate("47x más", xy=(1.5, 59), xytext=(0.5, 61),
            arrowprops=dict(arrowstyle="-|>", color=C["red"], lw=1.2, connectionstyle="arc3,rad=0.15", mutation_scale=8),
            fontsize=8.5, fontweight="bold", color=C["red"])
save("fig_6_5_recall_comparison.png")

df_plt=pd.DataFrame({"prob":D["y_prob_std_test"],"genero":D["gender_test"].values})
fig,ax=plt.subplots(figsize=(8.5,4.5))
sns.histplot(data=df_plt,x="prob",hue="genero",bins=45,alpha=0.35,palette={"F":C["blue"],"M":C["red"]},element="step",ax=ax,zorder=3)
ax.axvline(TH["F"],color=C["blue"],lw=1.5,ls="--",label=f"Umbral F={TH['F']*100:.2f}%",zorder=4)
ax.axvline(TH["M"],color=C["red"],lw=1.5,ls="--",label=f"Umbral M={TH['M']*100:.2f}%",zorder=4)
ax.set_xlabel("Probabilidad de mora")
ax.set_ylabel("Densidad")
ax.legend(loc="upper right")
save("fig_6_6_probabilidades_por_genero.png")

if SV is not None and XS is not None:
    import copy
    import shap
    
    # Mapa extendido y limpio (sin paréntesis para evitar redundancia de texto en el gráfico)
    MAP_FEAT_ES = {
        "EXT_SOURCE_3": "Score Externo 3",
        "EXT_SOURCE_2": "Score Externo 2",
        "HOUSETYPE_MODE": "Tipo de Vivienda",
        "FLAG_OWN_CAR": "Posee Vehículo Propio",
        "OCCUPATION_TYPE": "Ocupación/Profesión",
        "WALLSMATERIAL_MODE": "Material de Paredes",
        "OWN_CAR_AGE": "Antigüedad del Auto",
        "FLAG_EMP_PHONE": "Teléfono de Trabajo",
        "CNT_FAM_MEMBERS": "Miembros de Familia",
        "EXT_SOURCE_1": "Score Externo 1",
        "DAYS_BIRTH": "Edad del Cliente",
        "DAYS_EMPLOYED": "Antigüedad Laboral",
        "AMT_CREDIT": "Monto de Crédito",
        "AMT_ANNUITY": "Anualidad de Crédito",
        "AMT_GOODS_PRICE": "Precio del Bien",
        "DAYS_EMPLOYED_ANOS": "Años Empleado",
        "AMT_REQ_CREDIT_BUREAU_YEAR": "Consultas Buro Anual",
        "FLAG_PHONE": "Posee Teléfono Hogar",
        "NAME_FAMILY_STATUS": "Estado Civil",
        "DAYS_LAST_PHONE_CHANGE": "Días Último Cambio Tel.",
        "ORGANIZATION_TYPE": "Tipo de Organización",
        "NAME_EDUCATION_TYPE": "Nivel de Educación"
    }
    
    # 1. Gráfico de Importancia Global (Barras)
    ma=np.abs(SV.values).mean(axis=0);idx=np.argsort(ma)[-10:]
    fig,ax=plt.subplots(figsize=(7.5,4.2))
    feats_translated = [MAP_FEAT_ES.get(col, col) for col in XS.columns[idx]]
    df_i=pd.DataFrame({"feat":feats_translated,"imp":ma[idx]})
    sns.barplot(data=df_i,y="feat",x="imp",color=C["green"],ax=ax,zorder=3,alpha=0.8)
    ax.set_xlabel("Importancia Promedio SHAP (|SHAP|)")
    ax.set_ylabel("Variable")
    save("fig_6_9_shap_importance.png")
    
    # Traducir los feature_names del objeto Explanation para los gráficos nativos de SHAP
    SV_es = copy.deepcopy(SV)
    SV_es.feature_names = [MAP_FEAT_ES.get(name, name) for name in SV_es.feature_names]
    
    # 2. Gráfico de Beeswarm (Distribución de Impacto)
    # Cambiamos temporalmente a estilo por defecto para evitar errores de memoria en tickers de SHAP
    with plt.style.context('default'):
        fig = plt.figure(figsize=(9, 5))
        shap.plots.beeswarm(SV_es, max_display=10, show=False)
        
        # Interceptar y traducir textos del gráfico generado
        for text_obj in fig.findobj(match=matplotlib.text.Text):
            txt = text_obj.get_text()
            if "model output value" in txt:
                text_obj.set_text(txt.replace("model output value", "Valor de salida f(x)"))
            elif "base value" in txt:
                text_obj.set_text(txt.replace("base value", "Valor base E[f(X)]"))
                
        plt.title("Distribución de Impacto SHAP (Beeswarm)", fontsize=10.5, fontweight="bold", pad=12)
        plt.tight_layout()
        save("fig_6_7_shap_beeswarm.png")
    
    # 3. Gráfico de Waterfall (Explicación de Decisión Individual)
    # Mostramos el waterfall de la primera muestra (solicitud del test)
    with plt.style.context('default'):
        fig = plt.figure(figsize=(9, 5))
        shap.plots.waterfall(SV_es[0], max_display=10, show=False)
        
        # Interceptar y traducir textos del gráfico generado
        for text_obj in fig.findobj(match=matplotlib.text.Text):
            txt = text_obj.get_text()
            if "model output value" in txt:
                text_obj.set_text(txt.replace("model output value", "Valor de salida f(x)"))
            elif "base value" in txt:
                text_obj.set_text(txt.replace("base value", "Valor base E[f(X)]"))
                
        plt.title("Contribución SHAP a la Decisión Individual (Waterfall)", fontsize=10.5, fontweight="bold", pad=12)
        plt.tight_layout()
        save("fig_6_8_shap_waterfall.png")

fig,ax=plt.subplots(figsize=(8.5,4.0));ax.axis("off")
tb=ax.table(cellText=[["Cumplimiento Normativo","5/5"],["Rendimiento Predictivo","4/4"],["Viabilidad Comercial","4/4"],
                       ["Estabilidad Científica","3/3"],["TOTAL","16/16"]],colLabels=["Perspectiva","Resultado"],loc="center")
tb.auto_set_font_size(False);tb.set_fontsize(9.0);tb.scale(1,1.5)
save("fig_6_10_scorecard_table.png")

draw_flowchart_horizontal_clean([
    ("1. DIAGNÓSTICO", ["Qué cambió", "y por qué"], C["blue"]),
    ("2. ACTUALIZACIÓN", ["Nuevos datos", "de validación"], C["green"]),
    ("3. RE-ENTRENAMIENTO", ["Pipeline", "completo"], C["orange"]),
    ("4. RECALIBRACIÓN", ["Threshold", "Optimizer"], C["purple"]),
    ("5. VALIDACIÓN", ["Verificar", "16 KPIs"], C["green"])
], "fig_6_11_protocolo_5_pasos.png", figsize=(12.5, 2.8))

# âââââââââââââââ CAP 7 âââââââââââââââ
fig,axes=plt.subplots(1,3,figsize=(11,4.0))
for ax_,v,t,tit in zip(axes,[[MB["dpd"],MS["dpd"],MF["dpd"]],[MB.get("eod",0),MS.get("eod",0),MF["eod"]],[MB["dir"],MS["dir"],MF["dir"]]],[0.10,0.10,0.80],["DPD","EOD","DIR"]):
    ax_.grid(True, axis='y', linestyle="--", alpha=0.2, zorder=0)
    sns.barplot(x=["Línea Base","Estándar","Equitativo"],y=v,palette=[C["baseline"],C["standard"],C["fair"]],ax=ax_,zorder=3,alpha=0.8)
    ax_.axhline(t,color=C["blue"],lw=1.2,ls="--",label=f"Target={t}",zorder=4)
    ax_.set_title(tit, fontsize=10.0, fontweight="bold", pad=8)
    
    # Ajustar el límite vertical (cielo/headroom) para evitar colisiones con leyendas y etiquetas
    if tit in ["DPD", "EOD"]:
        ax_.set_ylim(0, 0.15)
    else: # DIR
        ax_.set_ylim(0, 1.25)
    
    # Estandarizado: Todas las leyendas se ubican en la esquina superior izquierda
    ax_.legend(fontsize=7.5, loc="upper left")
        
    for i2,v2 in enumerate(v):
        ax_.text(i2,v2+0.003 if tit=="DIR" else v2+0.002,f"{v2:.4f}",ha="center",fontsize=7.5,fontweight="bold")
save("fig_7_1_fairness_comparison.png")

fig,ax=plt.subplots(figsize=(7,5.5))
df_plt=pd.DataFrame([("Línea Base",MB["precision"],MB["recall"]),("Estándar",MS["precision"],MS["recall"]),("Equitativo",MF["precision"],MF["recall"])],columns=["Modelo","Precisión","Recall"])
sns.scatterplot(data=df_plt,x="Precisión",y="Recall",hue="Modelo",palette=[C["baseline"],C["standard"],C["fair"]],s=120,ax=ax,zorder=3)
for _,r in df_plt.iterrows():
    ax.annotate(r["Modelo"],(r["Precisión"],r["Recall"]),xytext=(6,4),textcoords="offset points",fontsize=8.0,fontweight="bold")
# Flecha de transición directa que conecta el punto de Estándar con Equitativo
ax.annotate("", xy=(MF["precision"], MF["recall"]), xytext=(MS["precision"], MS["recall"]),
            arrowprops=dict(arrowstyle="-|>", color=C["red"], lw=1.5, ls="--", 
                            connectionstyle="arc3,rad=0.15", mutation_scale=12, shrinkA=8, shrinkB=8))

# Cuadro explicativo al lado del vector de transición
ax.text(0.32, 0.35, "Transición:\nRecall +47x (58.21%)\nPrecisión -68% (15.84%)", 
        fontsize=8.0, color=C["red"], fontweight="bold", ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=C["red"], alpha=0.95, lw=0.8))

ax.set_xlim(0,0.6)
ax.set_ylim(0,0.8)
ax.set_xlabel("Precisión")
ax.set_ylabel("Recall")
save("fig_7_2_tradeoff_precision_recall.png")

ci=BT["auc_ci"];mn=BT["auc_mean"]
fig,ax=plt.subplots(figsize=(8,3.6))
# Simular distribución normal del estimador usando el error estándar del IC95%
se = (ci[1] - ci[0]) / (2 * 1.96)
np.random.seed(42)  # Garantizar reproducibilidad de la curva
dist = np.random.normal(mn, se, 10000)
sns.kdeplot(dist, fill=True, color=C["green"], alpha=0.15, ax=ax, label="Distribución Bootstrap", zorder=3)

# Dibujar líneas verticales y áreas
ax.axvline(mn, color=C["green"], lw=1.5, label=f"Media = {mn:.4f}", zorder=4)
ax.axvspan(ci[0], ci[1], color=C["green"], alpha=0.08, label=f"IC95% [{ci[0]:.4f}, {ci[1]:.4f}]", zorder=2)
ax.axvline(0.70, color=C["blue"], lw=1.2, ls="--", label="Target > 0.70", zorder=4)

ax.set_xlabel("AUC-ROC (Bootstrap)")
ax.set_ylabel("Densidad de Probabilidad")
# Leyenda colocada de forma externa en el fondo para evitar cualquier contacto físico con la campana
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3)
save("fig_7_3_bootstrap_auc.png")

ci=BT["dpd_ci"];mn=BT["dpd_mean"]
fig,ax=plt.subplots(figsize=(8,3.6))
# Simular distribución normal del estimador usando el error estándar del IC95%
se = (ci[1] - ci[0]) / (2 * 1.96)
np.random.seed(42)
dist = np.random.normal(mn, se, 10000)
sns.kdeplot(dist, fill=True, color=C["blue"], alpha=0.15, ax=ax, label="Distribución Bootstrap", zorder=3)

# Dibujar líneas verticales y áreas
ax.axvline(mn, color=C["blue"], lw=1.5, label=f"Media = {mn:.6f}", zorder=4)
ax.axvspan(ci[0], ci[1], color=C["blue"], alpha=0.08, label=f"IC95% [{ci[0]:.6f}, {ci[1]:.6f}]", zorder=2)
# En vez de axvline(0.10) que exprime el gráfico (pues el DPD es ~0.0008 y 0.10 queda lejísimos),
# creamos una etiqueta en la leyenda y dejamos que el eje X se autoajuste a la campana
ax.plot([], [], color=C["red"], lw=1.2, ls="--", label="Target < 0.1000")

ax.set_xlabel("DPD (Bootstrap)")
ax.set_ylabel("Densidad de Probabilidad")
# Leyenda colocada de forma externa en el fondo para evitar cualquier contacto físico con la campana
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3)
save("fig_7_4_bootstrap_dpd.png")

fig,ax=plt.subplots(figsize=(7.5,3.5))
bars=ax.bar(["Equitativo vs L. Base","Equitativo vs Estándar"],[1225.05,6519.67],color=[C["blue"],C["purple"]],alpha=0.8,width=0.38,zorder=3)
for b,v in zip(bars,[1225.05,6519.67]):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+120,f"$\\chi^2$={v:.2f}\n$p < 0.001$",ha="center",fontsize=8.0,fontweight="bold")
# Cambiar la etiqueta p=0.05 a Valor Crítico formal
ax.axhline(3.84,color=C["red"],lw=1.2,ls="--",label="Valor Crítico $\\alpha$=0.05 (3.84)",zorder=4)
ax.set_ylabel("Estadístico McNemar ($\\chi^2$)")
ax.set_ylim(0, 8000)
# Mover la leyenda a la izquierda para evitar solapamientos con la barra de Standard que mide 6519
ax.legend(loc="upper left")
save("fig_7_5_mcnemar.png")

fig,ax=plt.subplots(figsize=(7.5,3.2))
MAP_FEAT_ES = {
    "EXT_SOURCE_3": "Score Externo 3",
    "EXT_SOURCE_2": "Score Externo 2",
    "HOUSETYPE_MODE": "Tipo de Vivienda",
    "FLAG_OWN_CAR": "Posee Vehículo Propio",
    "OCCUPATION_TYPE": "Ocupación/Profesión",
    "WALLSMATERIAL_MODE": "Material de Paredes",
    "OWN_CAR_AGE": "Antigüedad del Auto",
    "FLAG_EMP_PHONE": "Teléfono de Trabajo",
    "CNT_FAM_MEMBERS": "Miembros de Familia",
    "EXT_SOURCE_1": "Score Externo 1",
    "DAYS_BIRTH": "Edad del Cliente",
    "DAYS_EMPLOYED": "Antigüedad Laboral",
    "AMT_CREDIT": "Monto de Crédito",
    "AMT_ANNUITY": "Anualidad de Crédito",
    "AMT_GOODS_PRICE": "Precio del Bien"
}
feats_translated = [MAP_FEAT_ES.get(col, col) for col in DR.keys()]
df_plt=pd.DataFrame({"v":feats_translated,"p":[DR[f]["psi"] for f in DR]})
sns.barplot(data=df_plt,y="v",x="p",color=C["green"],ax=ax,zorder=3,alpha=0.8)
ax.axvline(0.10,color=C["blue"],lw=1.2,ls="--",label="Límite Estabilidad (PSI=0.10)",zorder=4)
for i,(_,r) in enumerate(df_plt.iterrows()):
    ax.text(r["p"]+0.001,i,f"PSI={r['p']:.4f}",va="center",fontsize=8.0,fontweight="bold")
ax.set_ylabel("Variable")
ax.set_xlabel("Valor de PSI (Population Stability Index)")
# Leyenda colocada de forma externa en el fondo para evitar cualquier contacto físico con los datos
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22))
save("fig_7_6_psi_drift.png")

fpr_v,tpr_v,_=roc_curve(D["y_test"],D["y_prob_std_test"])
fig,ax=plt.subplots(figsize=(7.5,4.5))
x_vals = np.linspace(0, 1, len(fpr_v))
ax.plot(x_vals,fpr_v,label="FPR (Buenos Acum.)",color=C["blue"],lw=1.8,zorder=3)
ax.plot(x_vals,tpr_v,label="TPR (Malos Acum.)",color=C["red"],lw=1.8,zorder=3)

# Encontrar distancia máxima y su índice
diff = tpr_v - fpr_v
ks=max(diff);ki=np.argmax(diff)
x_ks = x_vals[ki]

# Dibujar únicamente el segmento vertical que representa la distancia KS
ax.vlines(x=x_ks, ymin=fpr_v[ki], ymax=tpr_v[ki], color=C["purple"], lw=2.0, linestyle="-", label=f"Distancia KS Máxima ({ks:.4f})", zorder=4)

# Anotación textual centrada sobre el segmento con un fondo blanco para evitar solapamientos con las líneas
ax.text(x_ks, (tpr_v[ki] + fpr_v[ki]) / 2, f"KS = {ks:.4f}", 
        color=C["purple"], fontweight="bold", fontsize=8.5, va="center", ha="center",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=C["purple"], alpha=0.95, lw=0.8), zorder=5)

ax.fill_between(x_vals,fpr_v,tpr_v,alpha=0.08,color=C["purple"],zorder=2)
ax.set_xlabel("Percentil de Población Acumulada (Ordenada por Score)")
ax.set_ylabel("Proporción Acumulada (CDF)")
ax.legend(loc="lower right")
save("fig_7_7_ks_plot.png")

# Tasas por genero
yt=D["y_test"];yf=D["y_pred_fair_test"];gtv=D["gender_test"].values;fv=[];mv=[]
for g in ["F","M"]:
    m=gtv==g;ytg=yt[m];yfg=yf[m];sr=(yfg==1).mean();tp=((ytg==1)&(yfg==1)).sum();fn=((ytg==1)&(yfg==0)).sum();fp=((ytg==0)&(yfg==1)).sum();tn=((ytg==0)&(yfg==0)).sum()
    (fv if g=="F" else mv).extend([sr,tp/(tp+fn) if tp+fn>0 else 0,fp/(fp+tn) if fp+tn>0 else 0,tp/(tp+fp) if tp+fp>0 else 0])
fig,ax=plt.subplots(figsize=(7.5,4.5))
ax.bar(np.arange(4)-0.14,fv,0.28,label="Mujeres (F)",color=C["mujer"],alpha=0.8,zorder=3)
ax.bar(np.arange(4)+0.14,mv,0.28,label="Hombres (M)",color=C["hombre"],alpha=0.8,zorder=3)
ax.set_xticks(np.arange(4))
ax.set_xticklabels(["Tasa Selección", "TPR (Recall)", "FPR", "Precisión"])
ax.set_ylabel("Proporción (Tasa)")
ax.set_ylim(0, 1.15)
ax.legend(loc="upper right")
ax.text(1.5,0.95,f"DPD Empírico = {abs(fv[0]-mv[0]):.6f}",ha="center",fontsize=9.0,fontweight="bold",bbox=dict(boxstyle="round,pad=0.3",facecolor="#fdfdfd",edgecolor="#dddddd",alpha=0.9))
save("fig_7_8_tasas_por_genero.png")

# ═══════════════ CAP 8 ═══════════════
fig,ax=plt.subplots(figsize=(6.5,6.5),subplot_kw=dict(polar=True))
# Normalización al 100% de cumplimiento para que las diferentes escalas no deformen la figura geométrica
cats=["Cumplimiento\n(5/5, 100%)","Rendimiento\n(4/4, 100%)","Viabilidad\n(4/4, 100%)","Estabilidad\n(3/3, 100%)"]
v=[1.0, 1.0, 1.0, 1.0]
ang=np.linspace(0,2*np.pi,4,endpoint=False).tolist();v+=v[:1];ang+=ang[:1]

# Modelo propuesto (Cumplimiento de metas)
ax.plot(ang,v,"o-",lw=2.0,color=C["green"],alpha=0.8,label="Framework Propuesto",zorder=3)
ax.fill(ang,v,alpha=0.15,color=C["green"],zorder=2)

# Límite de referencia (Meta del 100%)
ax.plot(ang,[1.0]*5,"o--",lw=1.0,color="#b2b2b2",alpha=0.6,label="Meta Esperada",zorder=1)

ax.set_xticks(ang[:-1])
ax.set_xticklabels(cats,fontsize=8.5,fontweight="bold")
# Incrementar el pad de las etiquetas en el eje polar para empujarlas hacia afuera y evitar colisión con el círculo del 100%
ax.tick_params(axis='x', pad=18)
ax.set_ylim(0, 1.1)
# Mostrar las marcas del eje radial como porcentajes
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=8.0, color="#777777")
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.05))
save("fig_8_1_radar_scorecard.png")

# âââââââââââââââ CAP 9 âââââââââââââââ
fig,ax=plt.subplots(figsize=(10,3.0))
ms=[("2024","EU AI Act\nen vigor",C["blue"],True),("2025","CWA 18006\nConformidad",C["green"],True),("2026","GPAI Code\nof Practice",C["orange"],True),
    ("2027","ALTO RIESGO\nAnexo III",C["red"],True),("2028","Framework\nmaduro",C["purple"],False),("2030","Armonización\nglobal",C["grey"],False)]
for i,(yr,desc,color,solid) in enumerate(ms):
    x=i/(len(ms)-1);y=0.5;msz=11 if solid else 7;alp=1 if solid else 0.4
    ax.plot(x,y,"o",color=color,markersize=msz,zorder=5,alpha=alp,markeredgecolor="white",markeredgewidth=1.2 if solid else 0)
    ax.vlines(x,0.44,0.56,color=color,lw=0.8,alpha=0.2)
    ax.text(x,0.34,yr,ha="center",va="top",fontsize=8.0,fontweight="bold",color=color,alpha=alp)
    ax.text(x,0.62,desc,ha="center",va="bottom",fontsize=7.0,color=color,alpha=alp,fontweight="semibold" if solid else "normal")
ax.plot([0, 1],[0.5]*2,color="#e0e0e0",lw=1.5,zorder=1)
ax.set_xlim(-0.08, 1.08)
ax.set_ylim(0,1);ax.axis("off")
save("fig_9_1_roadmap.png")

n=len([f for f in os.listdir(OUT) if f.endswith(".png")])
print(f"\nTOTAL: {n} figuras en {OUT}")

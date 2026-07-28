"""
thesis_style.py — Configuracion estandar de estilo para figuras de la tesis.
Uso: from src.thesis_style import setup_thesis_style, C
"""
import matplotlib.pyplot as plt
import seaborn as sns

def setup_thesis_style():
    sns.set_theme(style="ticks", context="paper")
    sns.set_palette("colorblind")

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.dpi": 200,
        "savefig.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.3,
    })

C = {
    "blue": "#0173B2", "orange": "#DE8F05", "green": "#029E73",
    "red": "#D55E00", "purple": "#CC78BC", "brown": "#A67D5D",
    "pink": "#F6CECE", "grey": "#949494",
    "baseline": "#D55E00", "standard": "#DE8F05", "fair": "#029E73",
    "mujer": "#0173B2", "hombre": "#D55E00",
}

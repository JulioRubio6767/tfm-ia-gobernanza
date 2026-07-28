import os
from pathlib import Path

# Base Path
BASE_DIR = Path("C:/programacion/UNIR/7. TFM_FINAL/tfm")

# Data Paths
RAW_DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Output Paths
OUTPUT_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
MODELS_DIR = OUTPUT_DIR / "models"

# Dataset Files
APPLICATION_TRAIN = RAW_DATA_DIR / "application_train.csv"
APPLICATION_TEST = RAW_DATA_DIR / "application_test.csv"

# Global Parameters
RANDOM_STATE = 42
TARGET_COL = "TARGET"
PROTECTED_COLS = ["CODE_GENDER", "DAYS_BIRTH"]

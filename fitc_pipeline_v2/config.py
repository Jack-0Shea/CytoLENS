import os

BASE_DIR   = r"C:\Users\Admin\OneDrive - NIBRT Ltd\260605_trincebiodataset"
BLUE_DIR   = os.path.join(BASE_DIR, "Blue_allwells")
GREEN_DIR  = os.path.join(BASE_DIR, "Green_allwells")
OUTPUT_DIR = os.path.join(BASE_DIR, "results_nuclear_only")

WELL_CONDITIONS = {
    "B2": "UTC",            "C2": "UTC",            "D2": "UTC",
    "B3": "CargoControl",   "C3": "CargoControl",   "D3": "CargoControl",
    "B4": "PhotoControl32", "C4": "PhotoControl32", "D4": "PhotoControl32",
    "B5": "FD150_125",      "C5": "FD150_125",      "D5": "FD150_125",
    "B6": "FD150_62",       "C6": "FD150_62",       "D6": "FD150_62",
    "B7": "FD150_32",       "C7": "FD150_32",       "D7": "FD150_32",
}

UTC_WELLS = ["B2", "C2", "D2"]

DAPI_CHANNEL = 2
FITC_CHANNEL = 1

CELLPOSE_MODEL           = "nuclei"
CELLPOSE_DIAMETER        = 17.0
CELLPOSE_FLOW_THRESH     = 0.4
CELLPOSE_CELLPROB_THRESH = 0.0
CELLPOSE_USE_GPU         = True

NUCLEUS_MIN_AREA_PX = 80
NUCLEUS_MAX_AREA_PX = 2000

THRESHOLD_N_STD = 5.0

SAVE_QC_IMAGES = True

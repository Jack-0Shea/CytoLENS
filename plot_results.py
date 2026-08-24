import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fitc_pipeline_v2"))

import config
from visualisation import save_summary_plots

well_df = pd.read_csv(os.path.join(config.OUTPUT_DIR, "per_well_results.csv"))
save_summary_plots(well_df, config.OUTPUT_DIR)
print("Done")

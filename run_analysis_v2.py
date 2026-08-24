import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fitc_pipeline_v2"))

from pipeline import run

if __name__ == "__main__":
    run()

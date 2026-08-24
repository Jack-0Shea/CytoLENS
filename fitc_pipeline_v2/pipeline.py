import os
import warnings
import pandas as pd
import numpy as np

import config
from io_utils       import build_file_index, load_channel
from segmentation   import load_cellpose_model, segment_nuclei, voronoi_expand, nucleus_count
from threshold      import derive_threshold
from quantification import measure_cells, summarise_field
from visualisation  import save_qc_image, save_summary_plots


def run():
    warnings.filterwarnings("ignore", category=UserWarning)

    print("=" * 65)
    print("FITC Uptake Analysis Pipeline v2 — Nuclear mask only")
    print(f"  Blue  : {config.BLUE_DIR}")
    print(f"  Green : {config.GREEN_DIR}")
    print(f"  Output: {config.OUTPUT_DIR}")
    print("=" * 65)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    qc_dir = os.path.join(config.OUTPUT_DIR, "QC_images")
    if config.SAVE_QC_IMAGES:
        os.makedirs(qc_dir, exist_ok=True)

    thresh_info = derive_threshold(
        green_dir        = config.GREEN_DIR,
        utc_wells        = config.UTC_WELLS,
        fitc_channel_idx = config.FITC_CHANNEL,
        n_std            = config.THRESHOLD_N_STD,
    )
    fitc_threshold = thresh_info["threshold"]

    print("\nLoading Cellpose model...")
    model = load_cellpose_model(config.CELLPOSE_MODEL, config.CELLPOSE_USE_GPU)

    blue_index  = build_file_index(config.BLUE_DIR)
    green_index = build_file_index(config.GREEN_DIR)

    common_keys = set(blue_index) & set(green_index)
    common_keys = {k for k in common_keys if k[0] in config.WELL_CONDITIONS}
    common_keys = sorted(common_keys)

    print(f"\nFound {len(common_keys)} complete fields across "
          f"{len(set(k[0] for k in common_keys))} wells\n")

    records = []

    for well, frame in common_keys:
        condition = config.WELL_CONDITIONS.get(well, "Unknown")
        print(f"  {well} frame {frame} | {condition}")

        dapi = load_channel(blue_index[(well, frame)],  config.DAPI_CHANNEL)
        fitc = load_channel(green_index[(well, frame)], config.FITC_CHANNEL)

        nucleus_labels   = segment_nuclei(
            dapi               = dapi,
            model              = model,
            diameter           = config.CELLPOSE_DIAMETER,
            flow_threshold     = config.CELLPOSE_FLOW_THRESH,
            cellprob_threshold = config.CELLPOSE_CELLPROB_THRESH,
            min_area_px        = config.NUCLEUS_MIN_AREA_PX,
            max_area_px        = config.NUCLEUS_MAX_AREA_PX,
        )
        cell_territories = voronoi_expand(nucleus_labels)
        cell_results     = measure_cells(nucleus_labels, cell_territories, fitc, fitc_threshold)
        summary          = summarise_field(cell_results)

        print(f"    Nuclei={nucleus_count(nucleus_labels)} | "
              f"FITC+={summary['n_positive']} ({summary['pct_positive']:.1f}%) | "
              f"Mean FITC={summary['mean_fitc_255']:.1f}/255")

        if config.SAVE_QC_IMAGES:
            save_qc_image(
                fname            = os.path.basename(blue_index[(well, frame)]),
                dapi             = dapi,
                fitc             = fitc,
                nucleus_labels   = nucleus_labels,
                cell_territories = cell_territories,
                cell_results     = cell_results,
                threshold        = fitc_threshold,
                output_dir       = qc_dir,
            )

        records.append({"well": well, "frame": frame, "condition": condition, **summary})

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(config.OUTPUT_DIR, "per_image_results.csv"), index=False)

    well_df = df.groupby(["well", "condition"]).agg(
        n_fields      = ("n_cells", "count"),
        total_cells   = ("n_cells", "sum"),
        mean_pct_pos  = ("pct_positive", "mean"),
        sd_pct_pos    = ("pct_positive", "std"),
        mean_fitc_255 = ("mean_fitc_255", "mean"),
        sd_fitc_255   = ("mean_fitc_255", "std"),
    ).reset_index()
    well_df.to_csv(os.path.join(config.OUTPUT_DIR, "per_well_results.csv"), index=False)

    cond_df = well_df.groupby("condition").agg(
        n_wells       = ("well", "count"),
        mean_pct_pos  = ("mean_pct_pos", "mean"),
        sd_pct_pos    = ("mean_pct_pos", "std"),
        mean_fitc_255 = ("mean_fitc_255", "mean"),
        sd_fitc_255   = ("mean_fitc_255", "std"),
    ).reset_index()
    cond_df.to_csv(os.path.join(config.OUTPUT_DIR, "condition_summary.csv"), index=False)

    save_summary_plots(well_df, config.OUTPUT_DIR)

    print(f"\n{'='*65}")
    print("CONDITION SUMMARY")
    print(cond_df[["condition","mean_pct_pos","sd_pct_pos",
                   "mean_fitc_255","sd_fitc_255"]].to_string(index=False))
    print(f"{'='*65}")

    return df

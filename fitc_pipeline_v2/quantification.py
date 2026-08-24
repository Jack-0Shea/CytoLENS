import numpy as np
from skimage import measure


def measure_cells(nucleus_labels, cell_territories, fitc, threshold):
    results = []
    for p in measure.regionprops(nucleus_labels):
        nuc_mask  = nucleus_labels == p.label
        nuc_fitc  = fitc[nuc_mask]
        mean_fitc = float(nuc_fitc.mean())
        results.append({
            "label"      : p.label,
            "area_px"    : p.area,
            "mean_fitc"  : mean_fitc,
            "mean_fitc_255" : mean_fitc * 255,
            "is_positive": mean_fitc > threshold,
        })
    return results


def summarise_field(cell_results):
    if not cell_results:
        return {
            "n_cells"         : 0,
            "n_positive"      : 0,
            "pct_positive"    : float("nan"),
            "mean_fitc_255"   : float("nan"),
            "median_fitc_255" : float("nan"),
            "sd_fitc_255"     : float("nan"),
        }

    n           = len(cell_results)
    n_positive  = sum(r["is_positive"] for r in cell_results)
    intensities = [r["mean_fitc_255"] for r in cell_results]

    return {
        "n_cells"         : n,
        "n_positive"      : n_positive,
        "pct_positive"    : 100.0 * n_positive / n,
        "mean_fitc_255"   : float(np.mean(intensities)),
        "median_fitc_255" : float(np.median(intensities)),
        "sd_fitc_255"     : float(np.std(intensities)),
    }

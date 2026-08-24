import numpy as np
from skimage import measure


def measure_cells(cell_labels, fitc, threshold):
    results = []
    for p in measure.regionprops(cell_labels, intensity_image=fitc):
        mask = cell_labels == p.label
        cell_fitc = fitc[mask]
        mean_fitc = float(cell_fitc.mean())
        results.append({
            "label"          : p.label,
            "area_px"        : p.area,
            "mean_fitc"      : mean_fitc,
            "mean_fitc_255"  : mean_fitc * 255,
            "is_positive"    : mean_fitc > threshold,
            "fitc_area_frac" : float(np.mean(cell_fitc > threshold)),
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

    n_cells     = len(cell_results)
    n_positive  = sum(r["is_positive"] for r in cell_results)
    intensities = [r["mean_fitc_255"] for r in cell_results]

    return {
        "n_cells"         : n_cells,
        "n_positive"      : n_positive,
        "pct_positive"    : 100.0 * n_positive / n_cells,
        "mean_fitc_255"   : float(np.mean(intensities)),
        "median_fitc_255" : float(np.median(intensities)),
        "sd_fitc_255"     : float(np.std(intensities)),
    }

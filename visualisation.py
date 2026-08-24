import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from skimage import measure, segmentation


def save_qc_image(fname, dapi, fitc, nucleus_labels, cell_territories, cell_results, threshold, output_dir):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    n_nuclei = int(nucleus_labels.max())

    axes[0].imshow(dapi, cmap="Blues", vmin=0, vmax=dapi.max() or 1)
    if n_nuclei > 0:
        bounds = segmentation.find_boundaries(nucleus_labels, mode="outer")
        axes[0].contour(bounds, colors="yellow", linewidths=0.5)
        terr_bounds = segmentation.find_boundaries(cell_territories, mode="outer")
        axes[0].contour(terr_bounds, colors="white", linewidths=0.3, alpha=0.4)
    axes[0].set_title(f"DAPI — {n_nuclei} nuclei | yellow=nucleus white=territory", fontsize=9)
    axes[0].axis("off")

    axes[1].imshow(fitc, cmap="Greens", vmin=0, vmax=fitc.max() or 1)
    fitc_mask = fitc > threshold
    if fitc_mask.any():
        axes[1].contour(fitc_mask.astype(np.uint8), colors="red", linewidths=0.5)
    axes[1].set_title(f"FITC — threshold={threshold:.4f} ({threshold*255:.1f}/255)", fontsize=9)
    axes[1].axis("off")

    overlay = np.stack([np.zeros_like(dapi), fitc * 0.9, dapi * 0.6], axis=-1)
    overlay = np.clip(overlay, 0, 1)
    axes[2].imshow(overlay)
    if n_nuclei > 0 and cell_results:
        status = {r["label"]: r["is_positive"] for r in cell_results}
        for p in measure.regionprops(nucleus_labels):
            cy, cx = p.centroid
            color = "lime" if status.get(p.label, False) else "red"
            axes[2].plot(cx, cy, ".", color=color, markersize=3, alpha=0.8)
    pos_patch = mpatches.Patch(color="lime", label="FITC positive")
    neg_patch = mpatches.Patch(color="red", label="FITC negative")
    axes[2].legend(handles=[pos_patch, neg_patch], loc="upper right", fontsize=7)
    axes[2].set_title("Overlay", fontsize=9)
    axes[2].axis("off")

    fig.suptitle(fname, fontsize=8)
    plt.tight_layout()
    out_path = os.path.join(output_dir, os.path.splitext(fname)[0] + "_QC.png")
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def save_summary_plots(condition_df, output_dir):
    conditions = condition_df["condition"].unique()
    order = ["UTC", "CargoControl", "PhotoControl32", "FD150_32", "FD150_62", "FD150_125"]
    order = [c for c in order if c in conditions] + [c for c in conditions if c not in order]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, metric, ylabel, title in [
        (axes[0], "mean_fitc_255", "Mean FITC intensity (0-255)", "Mean FITC Intensity per Cell"),
        (axes[1], "mean_pct_pos",  "FITC-positive cells (%)",     "% FITC-Positive Cells"),
    ]:
        means, sds, xs = [], [], []
        for i, cond in enumerate(order):
            sub = condition_df[condition_df["condition"] == cond][metric]
            means.append(sub.mean())
            sds.append(sub.std())
            xs.append(i)
            ax.scatter([i] * len(sub), sub, color="black", zorder=5, s=30, alpha=0.8)
        ax.bar(xs, means, yerr=sds, capsize=6, alpha=0.7, color="steelblue",
               width=0.5, error_kw={"elinewidth": 1.5})
        ax.set_xticks(xs)
        ax.set_xticklabels(order, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "condition_summary_plots.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Summary plots saved: {out_path}")

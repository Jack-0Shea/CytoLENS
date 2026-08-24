import numpy as np
from io_utils import build_file_index, load_channel


def derive_threshold(green_dir, utc_wells, fitc_channel_idx, n_std):
    green_index = build_file_index(green_dir)

    utc_files = [
        path for (well, frame), path in green_index.items()
        if well in utc_wells
    ]

    if not utc_files:
        raise ValueError(f"No UTC files found for wells {utc_wells} in {green_dir}")

    print(f"Deriving FITC threshold from {len(utc_files)} UTC images (wells: {utc_wells})...")

    all_pixels = []
    for f in utc_files:
        ch = load_channel(f, fitc_channel_idx)
        all_pixels.append(ch.ravel())

    pooled    = np.concatenate(all_pixels)
    utc_mean  = float(pooled.mean())
    utc_std   = float(pooled.std())
    threshold = float(np.clip(utc_mean + n_std * utc_std, 0.0, 1.0))

    print(f"  UTC G: mean={utc_mean:.4f} std={utc_std:.4f}")
    print(f"  Threshold = mean + {n_std}*std = {threshold:.4f} [{threshold*255:.1f}/255]")

    return {
        "threshold" : threshold,
        "utc_mean"  : utc_mean,
        "utc_std"   : utc_std,
        "n_std"     : n_std,
        "n_images"  : len(utc_files),
        "n_pixels"  : len(pooled),
    }

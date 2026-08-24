import os
import re
import glob
import numpy as np
import tifffile

_FNAME_RE = re.compile(r'_([A-H]\d+)_(\d+)_[A-Z]+\.tif$', re.IGNORECASE)


def parse_well_frame(path):
    fname = os.path.basename(path)
    m = _FNAME_RE.search(fname)
    if not m:
        raise ValueError(f"Cannot parse well/frame from: {fname}")
    return m.group(1).upper(), m.group(2)


def find_tiffs(directory):
    files = sorted(
        glob.glob(os.path.join(directory, "*.tif")) +
        glob.glob(os.path.join(directory, "*.tiff"))
    )
    if not files:
        raise FileNotFoundError(f"No TIFFs found in: {directory}")
    return files


def build_file_index(directory):
    index = {}
    for f in find_tiffs(directory):
        try:
            key = parse_well_frame(f)
            index[key] = f
        except ValueError:
            continue
    return index


def load_channel(path, channel_idx):
    with tifffile.TiffFile(path) as tif:
        data = tif.asarray()
    if data.ndim != 3 or data.shape[2] < 3:
        raise ValueError(f"Expected RGB image, got shape {data.shape}: {path}")
    return data[:, :, channel_idx].astype(np.float32) / 255.0

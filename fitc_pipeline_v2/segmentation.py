import numpy as np
from scipy import ndimage as ndi
from skimage import measure, segmentation, filters
from cellpose import models


def load_cellpose_model(model_name, use_gpu):
    model = models.CellposeModel(model_type=model_name, gpu=use_gpu)
    print(f"  Cellpose '{model_name}' loaded | GPU={use_gpu}")
    return model


def segment_nuclei(dapi, model, diameter, flow_threshold, cellprob_threshold, min_area_px, max_area_px):
    dapi_uint8 = (dapi * 255).clip(0, 255).astype(np.uint8)
    masks, flows, styles = model.eval(
        dapi_uint8,
        diameter=diameter,
        channels=[0, 0],
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold,
    )
    labels = masks.astype(np.int32)
    labels = _filter_by_area(labels, min_area_px, max_area_px)
    return labels


def voronoi_expand(nucleus_labels):
    """
    Expand nuclear masks to fill the entire image using Voronoi tessellation.
    Each pixel is assigned to its nearest nucleus.
    Returns a label array where every pixel belongs to a cell territory.
    """
    distance = ndi.distance_transform_edt(nucleus_labels == 0)
    cell_territories = segmentation.watershed(distance, nucleus_labels, mask=np.ones_like(nucleus_labels, dtype=bool))
    return cell_territories


def _filter_by_area(labels, min_area, max_area):
    out = labels.copy()
    for p in measure.regionprops(labels):
        if not (min_area <= p.area <= max_area):
            out[labels == p.label] = 0
    out, _, _ = segmentation.relabel_sequential(out)
    return out


def nucleus_count(labels):
    return int(labels.max())

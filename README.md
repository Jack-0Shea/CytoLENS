# CytoLENS

**CytoLENS** is an automated fluorescence image analysis pipeline for quantifying intracellular cargo uptake in iPSCs using Cellpose-based nuclear segmentation. Developed at NIBRT Ltd, Dublin.

## Overview

CytoLENS provides an image-based alternative to flow cytometry for quantifying cargo delivery (e.g. FD150 dextran, RNP) in iPSCs imaged on the xCELLigence eSight platform. It includes a Gradio web interface for interactive use and modular Python pipelines for batch processing.

### Key features

- Cellpose deep learning nuclear segmentation
- UTC-derived background thresholding
- Nuclear mask and Voronoi territory measurement methods
- CLAHE preprocessing for faint DAPI staining
- Per-well plate layout Excel output
- Validated against flow cytometry (r = 0.883, p = 0.002)
- Gradio web interface with single image and batch processing modes

## Requirements

- Python 3.11
- CUDA-compatible GPU recommended (RTX 4080 tested)

Install dependencies:

```bash
pip install cellpose tifffile numpy scipy scikit-image pandas matplotlib gradio openpyxl
```

## Project structure

```
CytoLENS/
├── app.py                        # Gradio web interface
├── src_v2/                       # FD150 uptake pipeline
│   ├── run_analysis_v2.py
│   └── fitc_pipeline_v2/
│       ├── config.py
│       ├── io_utils.py
│       ├── segmentation.py
│       ├── threshold.py
│       ├── quantification.py
│       ├── visualisation.py
│       └── pipeline.py
├── src_nanog/                    # NANOG 1x nuclear analysis
│   ├── run_nanog.py
│   └── nanog_pipeline/
├── src_nuclear/                  # IF titration — nuclear mask
│   ├── run_if_analysis.py
│   └── if_pipeline/
└── src_vosonoi/                  # IF titration — Voronoi territory
    ├── run_if_voronoi.py
    └── if_pipeline_voronoi/
```

## Running the web interface

```bash
conda activate cellpose_env
python app.py
```

Open `http://127.0.0.1:7860` in your browser.

### Tabs

| Tab | Description |
|-----|-------------|
| Single image | Upload DAPI + signal TIFF, point to UTC folder, run analysis |
| Batch — RGB composites | DAPI and signal in same RGB file (e.g. FD150 dataset) |
| Batch — separate channels | DAPI and signal in separate folders (e.g. Blue_allwells / Green_allwells) |

### Advanced parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Cellpose diameter | 17 px | Nucleus diameter — measure from images in ImageJ |
| Threshold N×SD | 5 | Background threshold = UTC mean + N×SD |
| Min nucleus area | 80 px | Filter out debris |
| Max nucleus area | 2000 px | Filter out cell aggregates |
| Cell probability threshold | 0.0 | Lower = more detections in dense regions |
| Enhance faint DAPI (CLAHE) | Off | Enable for dim or uneven DAPI staining |
| Measurement method | Nuclear mask | Nuclear mask only or Voronoi territory |

## Running batch pipelines

```bash
# FD150 uptake
cd src_v2
python run_analysis_v2.py

# NANOG 1x
cd src_nanog
python run_nanog.py

# IF titration — nuclear mask
cd src_nuclear
python run_if_analysis.py

# IF titration — Voronoi
cd src_vosonoi
python run_if_voronoi.py
```

## Validation

CytoLENS was validated against flow cytometry using FD150 dextran uptake in iPSCs across three concentrations (n=9 wells):

- Pearson correlation: r = 0.883, R² = 0.779, p = 0.002
- Paired t-test: no significant difference at any concentration (all p > 0.05)
- Bland-Altman: mean bias = 0.44 percentage points

## Platform

- Imaging: xCELLigence RTCA eSight (Agilent)
- Cell line: iPSCs (HD05, 1146, SCTi003-A)
- GPU: NVIDIA RTX 4080, CUDA 12.1
- Cellpose version: 4.1.1

## Author

Jack O'Shea
NIBRT Ltd, Dublin

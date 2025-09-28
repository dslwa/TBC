# TBC Codebase Orientation

## High-Level Purpose
This repository collects experiments for segmenting porous material micrographs and analyzing how different binarization and morphological operations influence porosity metrics. The code is written in Python and expects grayscale TIFF images as input.

## Repository Layout
- `orginal/` – raw microscope captures stored as TIFF files. Use these as the canonical inputs when (re-)generating cropped datasets.
- `Cropped/` – curated subsets of the originals, typically the starting point for the processing pipelines.
- `processed_selected/` – workspace for generated outputs such as masks, comparison panels, and CSV summaries.
- `sd15_outputs/`, `Realistic_Vision_*`, `stable-diffusion-2-base/`, etc. – Stable Diffusion checkpoints and generated samples that support dataset augmentation. These directories are large and are not used directly by the analysis scripts but are helpful context for model provenance.
- `binary_global_metrics_plot.png` – example visualization of threshold sweeps.
- Python scripts (`python_bianary.py`, `dylatacja.py`, `dylatacja_2.py`, `tbc_quick_selected_with_panels.py`) – core automation utilities described below.

## Key Scripts
### `python_bianary.py`
This script sweeps global thresholds from 1 to 255 across up to five TIFF images, saves the resulting binary masks to separate folders, and records the average white-pixel ratio per threshold in a CSV file alongside a matplotlib plot for quick inspection of porosity trends. It uses the Python Imaging Library (Pillow) for raster access and matplotlib for charting.

### `dylatacja.py`
Performs "black dilation" (dilating the background instead of the foreground) on every binary image contained in folders prefixed with `binary_adaptive_`. The script inverts the masks, dilates the background with a configurable square structuring element, and saves the inverted result to new folders with the `_blackdilated` suffix.

### `dylatacja_2.py`
Extends the dilation workflow by iterating over both `binary_adaptive_*` and `binary_global_t*` directories and by trying multiple structuring-element sizes. Each run exports results into folders suffixed with both `_blackdilated` and the dilation size (for example `_blackdilated_s3`).

### `tbc_quick_selected_with_panels.py`
A more elaborate benchmarking utility that:
1. Loads selected cropped images, optionally applies CLAHE contrast enhancement, and computes binary masks using a mix of adaptive (Sauvola, Niblack) and fixed thresholding strategies.
2. Exports per-method masks, measures porosity (mean mask value) and connected-component counts, and writes the statistics to `processed_selected/summary.csv`.
3. Generates panel figures comparing the original image against every thresholding method for qualitative review.

## Suggested First Steps for New Contributors
1. **Set up the environment** – Install Python 3.10+ and the dependencies used across scripts: `numpy`, `pillow`, `matplotlib`, `scikit-image`, `opencv-python`, and `pandas`.
2. **Inspect sample data** – Start with the `Cropped/` directory to familiarize yourself with typical image resolutions and contrast variations.
3. **Recreate the global threshold sweep** – Run `python python_bianary.py` to understand how metrics and visualizations are produced.
4. **Experiment with morphological operations** – Use `dylatacja.py` or `dylatacja_2.py` to see how dilation affects pore isolation; tweak `dilate_size` or add new structuring elements.
5. **Study the benchmarking pipeline** – Review `tbc_quick_selected_with_panels.py` to learn how multiple thresholding strategies are orchestrated, then extend the `METHODS` list or integrate new metrics.
6. **Document findings** – Place new experiments or notebooks inside a dedicated subfolder (for example `experiments/`) and record parameter choices so others can reproduce your results.

## Concepts Worth Learning
- Fundamentals of image binarization (global vs. adaptive thresholds) and how histogram characteristics guide threshold selection.
- Morphological operations (dilation, erosion, closing) and their use in cleaning binary masks of porous materials.
- Basic porosity metrics: area fraction, component counts, and how they relate to physical sample properties.
- Workflow automation with Python for batch-processing large sets of TIFF images.

Staying consistent with the existing folder conventions (`binary_*`, `_blackdilated`) makes it easier for teammates to locate and compare results.


#!/usr/bin/env python3

import cv2
import numpy as np
import pandas as pd
import skimage
from skimage import morphology, measure
from skimage.filters import (
    threshold_otsu, threshold_yen, threshold_triangle,
    threshold_sauvola, threshold_niblack
)
from pathlib import Path
import math
import matplotlib.pyplot as plt

EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")
TARGETS = {"img3", "img79", "img89"}

METHODS = (
    ["otsu", "yen", "triangle", "sauvola", "niblack"]
    + [f"fixed_{t}" for t in [48,64,80,96,112,128,144,160,176,192]]
)

def load_gray(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Normalize to uint8
    if img.dtype != np.uint8:
        maxv = img.max() if img.max() is not None else 1
        if maxv == 0: maxv = 1
        img = skimage.util.img_as_ubyte(img / maxv) if maxv > 1 else skimage.util.img_as_ubyte(img)
    return img

def apply_clahe(img: np.ndarray, clip_limit=2.0, tile_grid_size=(8,8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(img)

def compute_mask(img: np.ndarray, method: str, invert: bool=False) -> np.ndarray:
    if method == "otsu":
        t = threshold_otsu(img)
    elif method == "yen":
        t = threshold_yen(img)
    elif method == "triangle":
        t = threshold_triangle(img)
    elif method == "sauvola":
        t = threshold_sauvola(img, window_size=31, k=0.2)
    elif method == "niblack":
        t = threshold_niblack(img, window_size=31, k=0.2)
    elif method.startswith("fixed_"):
        t = int(method.split("_")[1])
    else:
        raise ValueError(f"Unknown method: {method}")
    bin_img = (img < t) if isinstance(t, np.ndarray) else (img < t)
    if invert:
        bin_img = ~bin_img
    # clean small specks
    bin_img = morphology.remove_small_objects(bin_img.astype(bool), min_size=32)
    return bin_img.astype(np.uint8)

def panel_figure(original: np.ndarray, masks_dict: dict, title: str, out_path: Path):
    # Create a grid: 4 columns, enough rows for original + all methods
    names = ["original"] + list(masks_dict.keys())
    items = [original] + [masks_dict[k]*255 for k in masks_dict.keys()]  # scale masks to 0..255 for display
    n = len(items)
    cols = 4
    rows = math.ceil(n / cols)

    fig = plt.figure(figsize=(cols*3.2, rows*3.2))
    for i, (name, img) in enumerate(zip(names, items), start=1):
        ax = plt.subplot(rows, cols, i)
        ax.imshow(img, cmap="gray")
        ax.set_title(name, fontsize=9)
        ax.axis("off")
    fig.suptitle(title, fontsize=12)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(str(out_path), dpi=200)
    plt.close(fig)

def main():
    in_dir = Path("D:/Daniel Salawa/TBC/Cropped")
    out_dir = Path("D:/Daniel Salawa/TBC/processed_selected")

    use_clahe = True     # poprawa kontrastu
    invert_mask = True  # False = 1=pory, True = 1= materiał

    out_masks = out_dir / "masks"
    out_csv = out_dir / "summary.csv"
    out_panels = out_dir / "panels"

    files = sorted([p for p in in_dir.rglob("*") if p.suffix.lower() in EXTS and p.stem in TARGETS])
    if not files:
        print("Nie znalazłem plików: img3, img79, img89 w", in_dir)
        return

    rows = []
    for img_path in files:
        img = load_gray(img_path)
        if use_clahe:
            img = apply_clahe(img)

        masks = {}
        for m in METHODS:
            mask = compute_mask(img, m, invert=invert_mask)
            masks[m] = mask
            (out_masks / m).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_masks / m / f"{img_path.stem}.png"), (mask*255).astype(np.uint8))

            porosity = float(mask.mean())
            lbl = measure.label(mask, connectivity=2)
            components = int(len(measure.regionprops(lbl)))
            rows.append({
                "image": img_path.name,
                "method": m,
                "porosity": porosity,
                "components": components
            })

        # panel z porównaniem
        panel_figure(img, masks, f"{img_path.stem} (original + methods)", out_panels / f"{img_path.stem}_panel.png")

    pd.DataFrame(rows).to_csv(out_csv, index=False)

    print(f"Przetworzono {len(files)} obrazów: {[p.name for p in files]}")
    print(f"Maski zapisane w: {out_masks}")
    print(f"Panele zapisane w: {out_panels}")
    print(f"CSV z metrykami: {out_csv}")


if __name__ == "__main__":
    main()

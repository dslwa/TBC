import os
import numpy as np
from PIL import Image
from skimage.morphology import dilation, square


base_folder = '.'                  # katalog zawierający foldery binary_adaptive_
output_suffix = '_blackdilated'    # dopisek do nazwy folderu wyjściowego
dilate_size = 3                    # rozmiar elementu strukturalnego (square)

# Znajdź wszystkie foldery z prefixem
folders = [d for d in os.listdir(base_folder)
           if d.startswith('binary_adaptive_') and os.path.isdir(d)]

for folder in folders:
    out_folder = f"{folder}{output_suffix}"
    os.makedirs(out_folder, exist_ok=True)

    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg')):
            continue

        # Wczytaj maskę binarną (0=black, 255=white)
        img = Image.open(os.path.join(folder, fname)).convert('L')
        arr = np.array(img) > 0  # True=białe, False=czarne

        # Inwersja: True=czarne piksele (tło)
        bg = ~arr
        # Dylatacja na tle, co "rozszerza" czarne obszary
        bg_dilated = dilation(bg, square(dilate_size))
        # Inwersja z powrotem: białe = oryginalne obiekty skurczone przez czarne
        result = ~bg_dilated

        # Konwersja na obraz (0/255)
        out_img = Image.fromarray((result.astype(np.uint8) * 255))
        out_img.save(os.path.join(out_folder, fname))

    print(f"Przetworzono czarną dylatację: {folder} -> {out_folder}")

print("\nGotowe! Czarne obszary zostały rozszerzone we wszystkich folderach.")
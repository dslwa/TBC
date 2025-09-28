import os
import numpy as np
from PIL import Image
from skimage.morphology import dilation, square

# =============================================
#  Morphological "black-dilation" dla różnych rozmiarów
#  Przetwarzane są foldery:
#   - binary_adaptive_*
#   - binary_global_t*
# =============================================

# Parametry użytkownika
base_folder   = '.'                          # katalog roboczy
prefixes      = ['binary_adaptive_', 'binary_global_t']  # wzorce nazw folderów
out_suffix    = '_blackdilated'              # dopisek do nazwy folderu
# Lista różnych rozmiarów elementu strukturalnego do testów
dilate_sizes  = [1, 2, 3, 5, 7]

def get_target_folders(base, prefixes):
    """Zwraca listę folderów zaczynających się od podanych prefixów."""
    return [d for d in os.listdir(base)
            if any(d.startswith(p) for p in prefixes) and os.path.isdir(os.path.join(base, d))]

# Główna pętla: dla każdego dilate_size i każdego folderu
folders = get_target_folders(base_folder, prefixes)
for size in dilate_sizes:
    struct_elem = square(size)
    for folder in sorted(folders):
        src_path = os.path.join(base_folder, folder)
        dst_folder = f"{folder}{out_suffix}_s{size}"
        os.makedirs(dst_folder, exist_ok=True)

        for fname in sorted(os.listdir(src_path)):
            if not fname.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg')):
                continue
            img = Image.open(os.path.join(src_path, fname)).convert('L')
            arr = np.array(img) > 0    # True = białe piksele

            # Inwersja: True = czarne piksele (tło)
            bg = ~arr
            # Dylatacja tła (czernie się poszerzają)
            bg_dil = dilation(bg, struct_elem)
            # Inwersja z powrotem
            result = ~bg_dil

            # Konwersja na obraz (0/255)
            out_img = Image.fromarray((result.astype(np.uint8) * 255), mode='L')
            out_img.save(os.path.join(dst_folder, fname))

        print(f"Rozmiar {size}: przetworzono {folder} -> {dst_folder}")

print("\nGotowe! Wszystkie foldery zostały rozszerzone dla podanych rozmiarów.")
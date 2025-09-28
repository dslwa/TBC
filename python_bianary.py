import os
import csv
from PIL import Image
import matplotlib.pyplot as plt

# Parametry użytkownika
input_folder = 'cropped'           # Folder z obrazami do przetworzenia
output_prefix = 'binary_global'    # Prefiks nazw folderów wyjściowych
thresholds = range(1, 256)         # Progi od 1 do 255
max_images = 5                     # Maksymalna liczba plików do przetworzenia

# Pobranie listy pierwszych max_images plików TIFF
files = sorted(
    f for f in os.listdir(input_folder)
    if f.lower().endswith('.tif')
)[:max_images]

# Utworzenie folderów wyjściowych dla każdego progu
for t in thresholds:
    folder = f"{output_prefix}_t{t}"
    os.makedirs(folder, exist_ok=True)

# Słownik do przechowywania metryk ilości białych pikseli
metrics = {t: [] for t in thresholds}

# Przetwarzanie obrazów
def process_images():
    for filename in files:
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path).convert('L')
        width, height = img.size
        pixels = img.load()
        total_pixels = width * height

        # Binarizacja i zbieranie metryk dla każdego progu
        for t in thresholds:
            binary = Image.new('1', (width, height))
            bin_pix = binary.load()
            for y in range(height):
                for x in range(width):
                    bin_pix[x, y] = 255 if pixels[x, y] > t else 0

            # Zapis wyniku
            out_folder = f"{output_prefix}_t{t}"
            out_path = os.path.join(out_folder, filename)
            binary.save(out_path)

            # Obliczenie ilości białych pikseli i ratio
            white_count = list(binary.getdata()).count(255)
            ratio = white_count / total_pixels
            metrics[t].append(ratio)

        print(f"{filename}: przetworzono dla progów 1-255.")

# Zapis CSV i wykres zależności
def generate_metrics_and_plot():
    overview_file = f"{output_prefix}_metrics.csv"
    with open(overview_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['threshold', 'average_white_ratio'])
        thresholds_list = sorted(metrics.keys())
        avg_ratios = []
        for t in thresholds_list:
            avg_ratio = sum(metrics[t]) / len(metrics[t])
            writer.writerow([t, avg_ratio])
            avg_ratios.append(avg_ratio)

    print(f"\nMetryki zapisano w pliku '{overview_file}'.")

    # Tworzenie wykresu
    plt.figure()
    plt.plot(thresholds_list, avg_ratios)
    plt.xlabel('Threshold')
    plt.ylabel('Average White Pixel Ratio')
    plt.title('White Pixel Ratio vs. Threshold')
    plt.grid(True)
    plot_file = f"{output_prefix}_metrics_plot.png"
    plt.savefig(plot_file)
    plt.close()
    print(f"Wykres zapisano w pliku '{plot_file}'.")

if __name__ == '__main__':
    process_images()
    generate_metrics_and_plot()
    print(f"\nGotowe! Przetworzono {len(files)} plików dla wszystkich progów od 1 do 255.")
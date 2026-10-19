import os
from pathlib import Path

def extract_gutenberg_text(input_file, output_file):
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK "
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK "

    start_gefunden = False
    ende_gefunden = False
    textzeilen = []

    with open(input_file, "r", encoding="utf-8") as infile:
        for zeile in infile:
            if not start_gefunden:
                if zeile.startswith(start_marker):
                    start_gefunden = True
                continue

            if zeile.startswith(end_marker):
                ende_gefunden = True
                break

            textzeilen.append(zeile)

    if not start_gefunden or not ende_gefunden:
        print(f"Keine gültigen Start- und End-Marker gefunden: {input_file}")
        return False

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.writelines(textzeilen)

    return True

if __name__ == "__main__":
    volltextordner = Path(__file__).parent / "fulltexts"

    anzahl_erfolgreich = 0
    fehlerdateien = []

    for input_file in sorted(volltextordner.glob("*.txt")):
        if not input_file.stem.isdigit():
            continue

        output_file = volltextordner / f"{input_file.stem}_filtered.txt"

        if extract_gutenberg_text(input_file, output_file):
            anzahl_erfolgreich += 1
        else:
            fehlerdateien.append(input_file.name)

    print(f"Erfolgreich gefiltert: {anzahl_erfolgreich}")
    print(f"Dateien mit fehlenden oder ungültigen Markern: {len(fehlerdateien)}")

    if fehlerdateien:
        print("Betroffene Dateien:")
        for dateiname in fehlerdateien:
            print(dateiname)
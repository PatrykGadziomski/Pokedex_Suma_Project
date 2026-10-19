import requests
import re
import os
import time
from pathlib import Path

def download_file(url, filename):
    # Zwischen 0,5 und 2 Sekunden warten
    time.sleep(0.5 + 1.5 * (os.urandom(1)[0] / 255))

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as fehler:
        print(f"Download fehlgeschlagen: {url} – {fehler}")
        return False

    response.encoding = "utf-8"
    text = response.text

    if not text.strip():
        print(f"Leere Datei erhalten: {url}")
        return False

    # Erst vollständig in eine vorläufige Datei schreiben
    temporaere_datei = Path(str(filename) + ".part")

    with temporaere_datei.open("w", encoding="utf-8") as datei:
        datei.write(text)

    temporaere_datei.replace(filename)

    print(f"Erfolgreich gespeichert: {filename}")
    return True

if __name__ == "__main__":
    projektordner = Path(__file__).parent
    id_datei = projektordner / "ebook_ids.txt"
    volltextordner = projektordner / "fulltexts"

    volltextordner.mkdir(exist_ok=True)

    with id_datei.open("r", encoding="utf-8") as datei:
        ebook_ids = []
        for zeile in datei:
            ebook_id = zeile.strip()
            if ebook_id:
                ebook_ids.append(ebook_id)

    print(f"Eingelesene IDs: {len(ebook_ids)}")

    anzahl_downloads = 0
    anzahl_fehler = 0
    anzahl_uebersprungen = 0

    for ebook_id in ebook_ids:
        url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"
        output_file = volltextordner / f"{ebook_id}.txt"

        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"Bereits vorhanden: {ebook_id}.txt")
            anzahl_uebersprungen += 1
            continue

        if download_file(url, output_file):
            anzahl_downloads += 1
        else:
            anzahl_fehler += 1

    print(f"Neu heruntergeladen: {anzahl_downloads}")
    print(f"Bereits vorhanden und übersprungen: {anzahl_uebersprungen}")
    print(f"Fehler: {anzahl_fehler}")
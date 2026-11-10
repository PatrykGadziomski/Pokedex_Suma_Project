import os
import random
import time

import requests

OUTPUT_DIR = "fulltexts"
IDS_FILE = "ebook_ids.txt"


def download_file(url, filename):
    """
    Lädt eine UTF-8-codierte Textdatei herunter und speichert sie unter 'filename'.
    Wartet zufällig 0.5-2 Sekunden, um den Server nicht zu überlasten.

    Rückgabe: (True, None) bei Erfolg, sonst (False, Fehlergrund)
    """
    time.sleep(random.uniform(0.5, 2.0))

    try:
        response = requests.get(url, timeout=60)
    except requests.RequestException as e:
        return False, f"Ausnahme: {e}"

    if response.status_code != 200:
        return False, f"HTTP {response.status_code}"

    response.encoding = "utf-8"
    text = response.text
    if not text.strip():
        return False, "Datei ist leer"

    # Erst in temporäre Datei schreiben, dann atomar umbenennen:
    # So bleibt bei einem Abbruch nie eine halbe Datei unter dem Zielnamen liegen.
    tmp_filename = filename + ".part"
    with open(tmp_filename, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp_filename, filename)
    return True, None


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(IDS_FILE):
        print(f"Datei '{IDS_FILE}' nicht gefunden. Bitte zuerst 01_get_ebook_ids.py ausführen.")
        raise SystemExit(1)

    with open(IDS_FILE, "r", encoding="utf-8") as f:
        ebook_ids = [line.strip() for line in f if line.strip()]
    print(f"{len(ebook_ids)} E-Book-IDs aus '{IDS_FILE}' geladen.")

    downloaded = 0
    skipped = 0
    errors = []  # Liste von (ebook_id, Grund)

    try:
        for ebook_id in ebook_ids:
            url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"
            filename = os.path.join(OUTPUT_DIR, f"{ebook_id}.txt")

            # Inkrementell: vorhandene, nicht leere Dateien überspringen
            if os.path.exists(filename):
                if os.path.getsize(filename) > 0:
                    skipped += 1
                    continue
                os.remove(filename)  # leere Datei entfernen und neu laden

            print(f"Herunterladen von {url}")
            ok, reason = download_file(url, filename)
            if ok:
                downloaded += 1
            else:
                errors.append((ebook_id, reason))
                print(f"{ebook_id}: {reason}")
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer. Beim nächsten Start geht es inkrementell weiter.")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print(f"Neu heruntergeladen:              {downloaded}")
    print(f" Bereits vorhanden (übersprungen): {skipped}")
    print(f"Fehler:                           {len(errors)}")
    for ebook_id, reason in errors:
        print(f"   - {ebook_id}: {reason}")
    print("=" * 60)
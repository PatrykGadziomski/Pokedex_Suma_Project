import os
import re

INPUT_DIR = "fulltexts"

# Toleranter als ein fester String: THE/THIS, optionale Leerzeichen nach den Sternen,
# Groß-/Kleinschreibung egal
START_RE = re.compile(r"^\s*\*{3}\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK", re.IGNORECASE)
END_RE = re.compile(r"^\s*\*{3}\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK", re.IGNORECASE)


def extract_gutenberg_text(input_file, output_file):
    """
    Extrahiert den Text zwischen START- und END-Marker und schreibt ihn nach output_file.
    Die Ausgabedatei wird nur angelegt, wenn beide Marker gefunden wurden.

    Rückgabe: (True, None) bei Erfolg, sonst (False, Fehlergrund)
    """
    try:
        with open(input_file, "r", encoding="utf-8-sig") as infile:  # utf-8-sig entfernt ein BOM
            lines = infile.readlines()
    except UnicodeDecodeError as e:
        return False, f"Dekodierfehler: {e}"

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if start_idx is None:
            if START_RE.match(line):
                start_idx = i
        elif END_RE.match(line):
            end_idx = i
            break

    if start_idx is None and end_idx is None:
        return False, "START- und END-Marker fehlen"
    if start_idx is None:
        return False, "START-Marker fehlt"
    if end_idx is None:
        return False, "END-Marker fehlt"

    content = lines[start_idx + 1:end_idx]
    if not "".join(content).strip():
        return False, "Text zwischen den Markern ist leer"

    # Erst in temporäre Datei schreiben, dann atomar umbenennen
    tmp_file = output_file + ".part"
    with open(tmp_file, "w", encoding="utf-8", newline="") as outfile:
        outfile.writelines(content)
    os.replace(tmp_file, output_file)
    return True, None


if __name__ == "__main__":
    if not os.path.exists(INPUT_DIR):
        print(f"Verzeichnis '{INPUT_DIR}' nicht gefunden. Bitte zuerst 02_fetch_fulltext.py ausführen.")
        raise SystemExit(1)

    files = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.endswith(".txt") and not f.endswith("_filtered.txt")
    )

    num_processed = 0
    num_skipped = 0
    errors = []  # Liste von (Dateiname, Grund)

    try:
        for filename in files:
            input_file = os.path.join(INPUT_DIR, filename)
            output_file = os.path.join(INPUT_DIR, f"{filename[:-4]}_filtered.txt")

            # Inkrementell: nur überspringen, wenn die gefilterte Datei existiert und nicht leer ist
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                num_skipped += 1
                continue

            ok, reason = extract_gutenberg_text(input_file, output_file)
            if ok:
                num_processed += 1
            else:
                errors.append((filename, reason))
                print(f"{filename}: {reason}")
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer. Beim nächsten Start geht es inkrementell weiter.")

    print("\n" + "=" * 60)
    print(f"Erfolgreich gefiltert:             {num_processed}")
    print(f" Übersprungen (bereits vorhanden): {num_skipped}")
    print(f"Fehler (keine gültigen Marker):    {len(errors)}")
    for filename, reason in errors:
        print(f"   - {filename}: {reason}")
    print("=" * 60)

    if errors:
        print("\nFür diese E-Books wurde keine _filtered.txt erzeugt; sie werden nicht indexiert.")
    else:
        print("\nAlle E-Books enthalten gültige Start- und End-Marker.")
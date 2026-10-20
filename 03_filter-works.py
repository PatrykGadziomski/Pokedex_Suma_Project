import os
from pathlib import Path

def extract_ebook_text(input_file, output_file):
    """
    Extrahiert den Text zwischen '*** START … ***' und '*** END … ***' aus der übergebenen E-Book-Textdatei vom
    Project Gutenberg und speichert den gefilterten Inhalt in einer neuen Textdatei mit dem angegebenen Namen ab.

    Parameter:
    - input_file (str): Pfad zur Originaldatei.
    - output_file (str): Pfad zur bereinigten Ausgabedatei ohne Header und Footer.
    """
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK "
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK "
    inside_text = False # Flag, um zu verfolgen, ob wir uns innerhalb des relevanten Textabschnitts befinden

    # zeilenweises Einlesen der Originaldatei, um relevanten Textabschnitte zu extrahieren und in Ausgabedatei zu schreiben
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            if line.startswith(start_marker):
                inside_text = True  # Start-Marker gefunden → Ab jetzt den Inhalt aus dem E-Book aufsammeln
                continue
            if line.startswith(end_marker):
                break # Ende-Marker gefunden → Den weiteren Inhalt der Textdatei ignorieren
            if inside_text:
                outfile.write(line)  # relevanter Text für die Ausgabedatei

    if inside_text:
        return True
    print(f"Keine gültigen Start- und End-Marker für Header und Footer gefunden in: {input_file}.")
    return False

if __name__ == "__main__":
    input_dir = Path("/Users/miros/PA_IndexingAndRetrieval/fulltexts")
    # Suche in Autorverzeichnissen nach Textdateien mit der Endung ".txt"
    num_of_files_processed = 0
    num_of_errors = 0
    
    if os.path.isdir(input_dir):
            print(f"Verarbeitung der Volltexte für Autor {input_dir}")
            for filename in os.listdir(input_dir):
                if filename.endswith(".txt"):
                    num_of_files_processed += 1
                    input_file = os.path.join(input_dir, filename)
                    output_file = os.path.join(input_dir, filename.replace(".txt", "_filtered.txt"))
                    if not extract_ebook_text(input_file, output_file):
                        num_of_errors += 1

    print(f"Insgesamt {num_of_files_processed} Dateien verarbeitet (Anzahl Fehler: {num_of_errors}).")
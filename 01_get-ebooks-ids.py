import csv
from pathlib import Path

CATALOG_PATH = Path("/Users/miros/Documents/GitHub/suma-tech/praxisteile/04/pg_catalog.csv")
FILE_PATH = Path("/Users/miros/PA_IndexingAndRetrieval/ebook_ids.txt")

"""
Die Funktion index_metadata liest die CSV-Datei ein, filtert die Zeilen basierend auf bestimmten Kriterien und speichert die gefilterten IDs in einer Textdatei. 
Die Kriterien sind:
- Die Spalte "Text#" ist nicht leer
- Die Spalte "Language" ist "de"
"""

def index_metadata(CATALOG_PATH, FILE_PATH):

    total = 0
    filtered_data = []
   
    
    with open(CATALOG_PATH, "r", newline="", encoding="utf-8") as f, \
         open(FILE_PATH, "w", newline="", encoding="utf-8") as output_file:
         reader = csv.DictReader(f)
         for row in reader:
            if row["Text#"] and row["Language"] == "de":
                filtered_data.append(row["Text#"])
                output_file.write(row["Text#"] + "\n")
                total = len(filtered_data)

    print(f"Es wurden {total:n} IDs gespeichert.")

if __name__ == "__main__":
    
    index_metadata(CATALOG_PATH, FILE_PATH)
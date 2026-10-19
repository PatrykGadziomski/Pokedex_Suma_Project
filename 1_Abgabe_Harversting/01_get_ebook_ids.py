import pysolr
from pathlib import Path

solr = pysolr.Solr(
    "http://localhost:8983/solr/my1stcore",
    timeout=10
)

ergebnisse = solr.search(
    "language:de AND type:Text",
    fl="id",
    sort="id asc",
    cursorMark="*"
)

ausgabedatei = Path(__file__).parent / "ebook_ids.txt"

anzahl = 0

with ausgabedatei.open("w", encoding="utf-8") as datei:
    for dokument in ergebnisse:
        datei.write(dokument["id"] + "\n")
        anzahl += 1

print(f"Gespeicherte IDs: {anzahl}")
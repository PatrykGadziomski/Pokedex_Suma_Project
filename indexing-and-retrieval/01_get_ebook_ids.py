import pysolr

# Solr-Konfiguration
SOLR_URL = "http://localhost:8983/solr/my1stcore"
solr = pysolr.Solr(SOLR_URL, timeout=60)

# Filter: Sprache = Deutsch und Dokumenttyp = Text (Feldnamen müssen zum Schema passen)
# Deep Paging: pysolr durchläuft alle Seiten automatisch, sobald cursorMark angegeben ist
results = solr.search(
    "*:*",
    fq=["language:de", "type:Text"],
    fl="id",
    rows=1000,        # Seitengröße pro Request, nicht das Gesamtlimit
    sort="id asc",    # cursorMark verlangt eine Sortierung nach dem Unique-Key
    cursorMark="*",
)

# Iterieren holt automatisch alle Seiten
ebook_ids = [doc["id"] for doc in results]

# IDs in Datei schreiben (eine ID pro Zeile)
output_file = "ebook_ids.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for ebook_id in ebook_ids:
        f.write(f"{ebook_id}\n")

print(f"{len(ebook_ids)} E-Book-IDs wurden in '{output_file}' gespeichert.")

# Kontrolle (vor der Abgabe optional entfernen): sollten alle gleich sein
print(f"Solr numFound: {results.hits}, eindeutige IDs: {len(set(ebook_ids))}")
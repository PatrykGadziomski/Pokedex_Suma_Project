from pathlib import Path
import pysolr

# Verbindung zu den beiden Solr-Cores
metadaten_solr = pysolr.Solr(
    "http://localhost:8983/solr/my1stcore",
    timeout=30
)

volltext_solr = pysolr.Solr(
    "http://localhost:8983/solr/pg_fulltexts",
    timeout=120
)

volltextordner = Path(__file__).parent / "fulltexts"
textdateien = sorted(volltextordner.glob("*_filtered.txt"))

anzahl_erfolgreich = 0
fehlerdateien = []

print(f"Gefundene bereinigte Textdateien: {len(textdateien)}")

for nummer, textdatei in enumerate(textdateien, start=1):
    ebook_id = textdatei.stem.removesuffix("_filtered")

    try:
        # Volltext einlesen
        volltext = textdatei.read_text(encoding="utf-8")

        if not volltext.strip():
            raise ValueError("Der Volltext ist leer.")

        # Metadaten anhand der E-Book-ID abfragen
        ergebnisse = metadaten_solr.search(
            f'id:"{ebook_id}"',
            fl="id,title,authors,language,subjects,issued",
            rows=1
        )

        if not ergebnisse.docs:
            raise ValueError("Keine Metadaten gefunden.")

        metadaten = ergebnisse.docs[0]

        # Titel in eine einzelne Zeichenfolge umwandeln
        titel = metadaten["title"]
        if isinstance(titel, list):
            titel = " ".join(titel)

        # Dokument für den neuen Core zusammenstellen
        dokument = {
            "id": ebook_id,
            "title": titel,
            "authors": metadaten.get("authors", []),
            "language": metadaten.get("language", []),
            "subjects": metadaten.get("subjects", []),
            "issued": metadaten["issued"],
            "fulltext": volltext
        }

        # Dokument an Solr übergeben
        volltext_solr.add([dokument], commit=False)
        anzahl_erfolgreich += 1

        print(
            f"[{nummer}/{len(textdateien)}] "
            f"E-Book {ebook_id} übertragen."
        )

    except (OSError, ValueError, KeyError, pysolr.SolrError) as fehler:
        fehlerdateien.append(textdatei.name)
        print(f"Fehler bei {textdatei.name}: {fehler}")

# Alle übertragenen Dokumente für Suchanfragen sichtbar machen
volltext_solr.commit()

print()
print(f"Erfolgreich indexiert: {anzahl_erfolgreich}")
print(f"Fehler: {len(fehlerdateien)}")

if fehlerdateien:
    print("Betroffene Dateien:")
    for dateiname in fehlerdateien:
        print(dateiname)
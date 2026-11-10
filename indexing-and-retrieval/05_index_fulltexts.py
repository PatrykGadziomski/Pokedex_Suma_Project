import re
from pathlib import Path

import pysolr

# Solr-Konfiguration
SOLR_SOURCE_URL = "http://localhost:8983/solr/my1stcore"
SOLR_TARGET_URL = "http://localhost:8983/solr/pg_fulltexts"
FULLTEXTS_DIR = "fulltexts"

# Volltexte sind groß (mehrere hundert KB pro Buch) -> kleine Batches
BATCH_SIZE = 10

solr_source = pysolr.Solr(SOLR_SOURCE_URL, timeout=60)
solr_target = pysolr.Solr(SOLR_TARGET_URL, timeout=300)


def get_metadata_by_id(ebook_id: str) -> dict | None:
    """Fragt die Metadaten eines E-Books im Core my1stcore ab."""
    try:
        results = solr_source.search(
            f'id:"{ebook_id}"',
            fl="id,title,authors,language,subjects,issued",
            rows=1,
        )
        if len(results) == 0:
            return None
        return results.docs[0]
    except Exception as e:
        print(f"Fehler bei der Suche nach ID {ebook_id}: {e}")
        return None


def extract_ebook_id_from_filename(filename: str) -> str | None:
    """'1234_filtered.txt' -> '1234'"""
    match = re.match(r"^(\d+)_filtered\.txt$", filename)
    return match.group(1) if match else None


def build_doc(ebook_id: str, metadata: dict, fulltext: str) -> dict:
    """Baut das Solr-Dokument. Fehlende oder leere Felder werden weggelassen
    (ein leerer String in einem pdate-Feld würde den ganzen Batch ablehnen lassen)."""
    doc = {"id": ebook_id, "fulltext": fulltext}

    if metadata.get("title"):
        doc["title"] = metadata["title"]
    if metadata.get("issued"):
        doc["issued"] = metadata["issued"]

    for field in ("authors", "language", "subjects"):
        value = metadata.get(field)
        if value:
            doc[field] = value if isinstance(value, list) else [value]

    return doc


def get_indexed_ids() -> set:
    """Ermittelt per Deep Paging (cursorMark) alle bereits indexierten IDs."""
    try:
        results = solr_target.search(
            "*:*", fl="id", rows=1000, sort="id asc", cursorMark="*"
        )
        return {str(doc["id"]) for doc in results}
    except Exception as e:
        print(f"Warnung beim Abrufen der bereits indexierten IDs: {e}")
        return set()


def index_batch(batch: list, errors: list) -> int:
    """Indexiert einen Batch inkl. Commit. Schlägt er fehl, wird jedes Dokument
    einzeln versucht, damit das problematische E-Book identifiziert werden kann.
    Gibt die Anzahl erfolgreich indexierter Dokumente zurück."""
    try:
        solr_target.add(batch, commit=True)
        return len(batch)
    except Exception as e:
        print(f"Batch fehlgeschlagen ({e}) – versuche Dokumente einzeln...")

    ok = 0
    for doc in batch:
        try:
            solr_target.add([doc], commit=True)
            ok += 1
        except Exception as e:
            errors.append((doc["id"], f"Indexierung fehlgeschlagen: {e}"))
            print(f"ID {doc['id']}: {e}")
    return ok


def index_fulltexts():
    fulltexts_path = Path(FULLTEXTS_DIR)
    if not fulltexts_path.exists():
        print(f"Verzeichnis '{FULLTEXTS_DIR}' nicht gefunden.")
        return

    filtered_files = sorted(fulltexts_path.glob("*_filtered.txt"))
    print(f"{len(filtered_files)} gefilterte Volltextdateien gefunden.")

    existing_ids = get_indexed_ids()
    print(f"Bereits indexiert: {len(existing_ids)} Dokumente.")

    success_count = 0
    skipped_count = 0
    errors = []  # Liste von (ebook_id, Grund)
    batch = []

    try:
        for file_path in filtered_files:
            ebook_id = extract_ebook_id_from_filename(file_path.name)
            if not ebook_id:
                errors.append((file_path.name, "Keine ID im Dateinamen"))
                continue

            if ebook_id in existing_ids:
                skipped_count += 1
                continue

            try:
                fulltext = file_path.read_text(encoding="utf-8").strip()
            except Exception as e:
                errors.append((ebook_id, f"Lesefehler: {e}"))
                continue
            if not fulltext:
                errors.append((ebook_id, "Volltext ist leer"))
                continue

            metadata = get_metadata_by_id(ebook_id)
            if not metadata:
                errors.append((ebook_id, "Keine Metadaten in my1stcore gefunden"))
                continue

            batch.append(build_doc(ebook_id, metadata, fulltext))

            if len(batch) >= BATCH_SIZE:
                success_count += index_batch(batch, errors)
                batch = []
                print(f"{success_count} Dokumente indexiert.")

        if batch:
            success_count += index_batch(batch, errors)
            print(f"{success_count} Dokumente indexiert.")
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer. Beim nächsten Start geht es inkrementell weiter.")

    print("\n" + "=" * 60)
    print(f"Neu indexiert:                    {success_count}")
    print(f" Übersprungen (bereits indexiert): {skipped_count}")
    print(f"Fehler:                           {len(errors)}")
    for ebook_id, reason in errors:
        print(f"   - {ebook_id}: {reason}")
    print("=" * 60)


if __name__ == "__main__":
    print("Starte Indexierung der gefilterten Volltexte in Solr-Core 'pg_fulltexts'...")
    index_fulltexts()
    print("\nIndexierung abgeschlossen.")
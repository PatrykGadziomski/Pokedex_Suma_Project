from datetime import datetime

import pysolr

# Solr-Konfiguration
SOLR_CORE_URL = "http://localhost:8983/solr/pg_fulltexts"

MONATE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def format_date(value) -> str:
    """
    Wandelt ein Datum in das Format '17. Mai 2023' um.
    pysolr liefert Datumsfelder meist schon als datetime-Objekt, sonst als ISO-String.
    Die Monatsnamen kommen aus einer eigenen Liste, damit keine Systemlocale nötig ist.
    """
    if not value:
        return "unbekannt"
    try:
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return f"{dt.day}. {MONATE[dt.month - 1]} {dt.year}"
    except Exception:
        return str(value)


def search(solr, query: str):
    """Führt eine Edismax-Suche auf dem Solr-Core pg_fulltexts durch (Top-10)."""
    params = {
        "defType": "edismax",
        "qf": "title^5 authors^2 subjects^1 fulltext^2 fulltext_alternative^3",
        "q.op": "OR",
        "mm": "10%",  # mindestens 10% der Suchterme müssen im Dokument vorkommen
        "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",  # neuere E-Books höher bewerten
        "rows": 10,
        "fl": "id,title,issued,authors,language,subjects,score",
    }

    try:
        results = solr.search(query, **params)
    except Exception as e:
        print(f"Fehler bei der Suchanfrage: {e}")
        return

    if len(results) == 0:
        print("\nIhre Suchanfrage liefert keine Treffer!")
        return

    print(f"\n* * * {results.hits} Suchergebnisse gefunden – {len(results)} Treffer werden angezeigt. * * *\n")

    for rank, result in enumerate(results, start=1):
        authors = "; ".join(result["authors"]) if result.get("authors") else "Unbekannt"
        languages = ", ".join(result["language"]) if result.get("language") else "Unbekannt"
        subjects = "; ".join(result["subjects"]) if result.get("subjects") else "Keine Themen"

        print(f"Rang {rank}")
        print(f"   ID: {result.get('id')}")
        print(f"   Titel: {result.get('title', 'Ohne Titel')}")
        print(f"   Aufnahme in Project Gutenberg: {format_date(result.get('issued'))}")
        print(f"   Autor(en): {authors}")
        print(f"   Sprache(n): {languages}")
        print(f"   Subject(s): {subjects}")
        print(f"   Relevanz-Score: {result.get('score', 0.0):.4f}")
        print()


if __name__ == "__main__":
    print("Willkommen bei der Solr-Volltextsuche (Core: pg_fulltexts)")
    print("Tippen Sie eine Suchanfrage ein oder 'quit!' zum Beenden.\n")

    solr = pysolr.Solr(SOLR_CORE_URL, timeout=60)

    while True:
        try:
            user_query = input("🔍 Suchanfrage: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAuf Wiedersehen!")
            break

        if not user_query:
            continue

        if user_query.lower() in ["quit!", "exit", "q", "beenden"]:
            print("Auf Wiedersehen!")
            break

        print(f"\nSuche nach: '{user_query}'")
        search(solr, user_query)
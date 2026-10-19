import pysolr


def als_text(wert):
    """Mehrere Werte für die Ausgabe zusammenfügen."""
    if isinstance(wert, list):
        return "; ".join(str(element) for element in wert)
    if wert is None:
        return "–"
    return str(wert)


solr = pysolr.Solr(
    "http://localhost:8983/solr/pg_fulltexts",
    timeout=30
)

suchanfrage = input("Was möchtest du suchen? ").strip()

if not suchanfrage:
    print("Bitte einen Suchbegriff eingeben.")
else:
    ergebnisse = solr.search(
        suchanfrage,
        **{
            "defType": "edismax",
            "qf": (
                "title^5 authors^2 subjects^1 "
                "fulltext^2 fulltext_alternative^3"
            ),
            "q.op": "OR",
            "mm": "10%",
            "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",
            "rows": 10,
            "fl": "id,title,authors,language,subjects,issued,score"
        }
    )
    print(f"\nTreffer insgesamt: {ergebnisse.hits}\n")

    for rang, dokument in enumerate(ergebnisse, start=1):
        print(f"Rang: {rang}")
        print(f"Bewertung: {dokument.get('score')}")
        print(f"ID: {dokument['id']}")
        print(f"Titel: {als_text(dokument.get('title'))}")
        print(f"Aufgenommen am: {als_text(dokument.get('issued'))}")
        print(f"Autor(en): {als_text(dokument.get('authors'))}")
        print(f"Sprache(n): {als_text(dokument.get('language'))}")
        print(f"Subject(s): {als_text(dokument.get('subjects'))}")
        print()
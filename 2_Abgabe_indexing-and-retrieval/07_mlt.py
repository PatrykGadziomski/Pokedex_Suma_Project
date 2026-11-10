import requests
import pysolr

core_url = "http://localhost:8983/solr/pg_fulltexts"

# Vorgaben aus der Bonusaufgabe
MLT_HANDLER_DEFAULTS = {
    "mlt.fl": "fulltext",
    "mlt.mintf": 2,
    "mlt.mindf": 5,
    "mlt.minwl": 5,
    "mlt.maxdfpct": 25,
    "mlt.interestingTerms": "list",
    "mlt.match.include": "false",
    "mlt.boost": "true"
}


def buch_ausgeben(buch):
    """ID, Titel und Autoren eines Buches ausgeben."""
    autoren = buch.get("authors", [])
    if isinstance(autoren, list):
        autoren = "; ".join(autoren)

    print(f"ID: {buch['id']}")
    print(f"Titel: {buch.get('title', '–')}")
    print(f"Autor(en): {autoren}")


# Prüfen, ob /mlt bereits vorhanden ist
response = requests.get(
    f"{core_url}/config/requestHandler",
    params={"wt": "json"},
    timeout=10
)
response.raise_for_status()

handler = response.json()["config"]["requestHandler"]

if "/mlt" in handler:
    print("Der Request Handler /mlt ist bereits vorhanden.")
else:
    neuer_handler = {
        "add-requesthandler": {
            "name": "/mlt",
            "class": "solr.MoreLikeThisHandler",
            "defaults": MLT_HANDLER_DEFAULTS
        }
    }

    response = requests.post(
        f"{core_url}/config",
        json=neuer_handler,
        timeout=30
    )

    if not response.ok:
        print(response.text)

    response.raise_for_status()
    print("Der Request Handler /mlt wurde angelegt.")


# Verbindung für die normale Suche
solr = pysolr.Solr(core_url, timeout=30)

suchanfrage = input(
    "\nZu welchem Thema suchst du ein Buch? "
).strip()

if not suchanfrage:
    print("Bitte einen Suchbegriff eingeben.")
else:
    # Besten Treffer als Ausgangsbuch ermitteln
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
            "rows": 1,
            "fl": "id,title,authors"
        }
    )

    if not ergebnisse.docs:
        print("Kein passendes Buch gefunden.")
    else:
        ausgangsbuch = ergebnisse.docs[0]

        print("\nAusgangsbuch für die Ähnlichkeitssuche:")
        buch_ausgeben(ausgangsbuch)

        # Ähnliche Bücher zum Ausgangsbuch suchen
        response = requests.get(
            f"{core_url}/mlt",
             params={
                "q": f'id:"{ausgangsbuch["id"]}"',
                "rows": 3,
                "fl": "id,title,authors",
                "wt": "json",
            },
            timeout=60
        )

        if not response.ok:
            print(response.text)

        response.raise_for_status()
        mlt_ergebnis = response.json()

        aehnliche_buecher = mlt_ergebnis["response"]["docs"]

        print("\nÄhnliche Bücher:")

        if not aehnliche_buecher:
            print(
                "Mit diesen Einstellungen wurden "
                "keine ähnlichen Bücher gefunden."
            )

        for rang, buch in enumerate(aehnliche_buecher, start=1):
            print(f"\nÄhnlicher Treffer {rang}:")
            buch_ausgeben(buch)

        print("\nFür die Ähnlichkeitssuche verwendete Begriffe:")

        interessante_terme = mlt_ergebnis.get("interestingTerms", [])

        for term in interessante_terme:
            print(f"- {term}")

        if not interessante_terme:
            print("Keine Begriffe zurückgegeben.")
import pysolr
import requests

# Solr-Konfiguration
SOLR_BASE_URL = "http://localhost:8983/solr"
SOLR_CORE_NAME = "pg_fulltexts"
SOLR_CORE_URL = f"{SOLR_BASE_URL}/{SOLR_CORE_NAME}"
MLT_HANDLER_PATH = "/mlt"

# MLT-Handler-Standardparameter
MLT_HANDLER_DEFAULTS = {
    "mlt.fl": "fulltext",
    "mlt.mintf": 2,
    "mlt.mindf": 5,
    "mlt.minwl": 5,
    "mlt.maxdfpct": 25,
    "mlt.interestingTerms": "list",
    # das Ausgangsdokument selbst soll nicht in der Trefferliste erscheinen
    "mlt.match.include": "false",
    "mlt.boost": "true",
}


def mlt_handler_exists() -> bool:
    """Fragt die Core-Konfiguration ab und prüft, ob '/mlt' vorhanden ist."""
    try:
        resp = requests.get(f"{SOLR_CORE_URL}/config/requestHandler", timeout=30)
        resp.raise_for_status()
        handlers = resp.json().get("config", {}).get("requestHandler", {})
        return MLT_HANDLER_PATH in handlers
    except Exception as e:
        print(f"Warnung beim Prüfen der Handler: {e}")
        return False


def create_mlt_handler_if_not_exists() -> bool:
    """Legt den Request Handler '/mlt' an, falls er noch nicht existiert."""
    if mlt_handler_exists():
        print(f"Request Handler '{MLT_HANDLER_PATH}' existiert bereits.")
        return True

    print(f"Erstelle Request Handler '{MLT_HANDLER_PATH}'...")
    payload = {
        "add-requesthandler": {
            "name": MLT_HANDLER_PATH,
            "class": "solr.MoreLikeThisHandler",
            # Die mlt.*-Parameter müssen unter "defaults" stehen
            "defaults": MLT_HANDLER_DEFAULTS,
        }
    }
    try:
        resp = requests.post(f"{SOLR_CORE_URL}/config", json=payload, timeout=30)
        if not resp.ok:
            print(f"Solr-Antwort ({resp.status_code}): {resp.text}")
            return False
        # Die Config API meldet Fehler teils mit HTTP 200 im Body
        body = resp.json()
        if "errorMessages" in body or "error" in body:
            print(f"Solr-Antwort: {body}")
            return False
        print(f"Request Handler '{MLT_HANDLER_PATH}' erfolgreich erstellt.")
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen des Handlers: {e}")
        return False


def search_top1(solr, query: str):
    """Führt die Suchanfrage aus und gibt das Top-1-Dokument zurück."""
    params = {
        "defType": "edismax",
        "qf": "title^5 authors^2 subjects^1 fulltext^2 fulltext_alternative^3",
        "q.op": "OR",
        "mm": "10%",
        "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",
        "rows": 1,
        "fl": "id,title,authors",
    }
    try:
        results = solr.search(query, **params)
    except Exception as e:
        print(f"Fehler bei der Suchanfrage: {e}")
        return None

    if len(results) == 0:
        print("Keine Treffer für Ihre Suchanfrage.")
        return None
    return results.docs[0]


def get_similar_docs(doc_id: str, mlt_params: dict = None):
    """
    Ruft über den MLT-Handler die ähnlichsten E-Books zur gegebenen ID ab.
    Gibt (Liste der Dokumente, interessante Terme) zurück.
    """
    params = {
        "q": f'id:"{doc_id}"',  # Ausgangsdokument über q bestimmen
        "rows": 3,
        "fl": "id,title,authors",
        "wt": "json",
    }
    if mlt_params:
        params.update(mlt_params)

    try:
        resp = requests.get(f"{SOLR_CORE_URL}{MLT_HANDLER_PATH}", params=params, timeout=60)
        if not resp.ok:
            print(f"Solr-Antwort ({resp.status_code}): {resp.text}")
            return [], []
        data = resp.json()
        docs = data.get("response", {}).get("docs", [])
        interesting_terms = data.get("interestingTerms", [])
        return docs, interesting_terms
    except Exception as e:
        print(f"Fehler beim MLT-Aufruf: {e}")
        return [], []


def print_doc(doc, prefix=""):
    """Gibt ID, Titel und Autor(en) eines Dokuments aus."""
    authors = doc.get("authors")
    if isinstance(authors, list):
        authors = "; ".join(authors)
    print(f"{prefix}ID: {doc.get('id')}")
    print(f"{prefix}Titel: {doc.get('title', 'Ohne Titel')}")
    print(f"{prefix}Autor(en): {authors or 'Unbekannt'}")


def print_interesting_terms(terms):
    """Gibt die 'interessantesten' Terme des Ausgangsdokuments aus."""
    if not terms:
        print("\nKeine interessanten Terme gefunden.")
        return

    print("\nInteressanteste Terme des Ausgangsdokuments:")
    if isinstance(terms, dict):
        for term, score in terms.items():
            print(f"  • {term}: {score}")
    elif isinstance(terms, list):
        for term in terms:
            print(f"  • {term}")
    else:
        print(f"  • {terms}")


def show_similar(doc_id: str, mlt_params: dict = None):
    similar_docs, interesting_terms = get_similar_docs(doc_id, mlt_params)
    if similar_docs:
        print(f"\n{len(similar_docs)} ähnliche E-Books gefunden:")
        for i, doc in enumerate(similar_docs, start=1):
            print(f"\n  Ähnlichkeit #{i}:")
            print_doc(doc, "    ")
    else:
        print("Keine ähnlichen Dokumente gefunden.")
    print_interesting_terms(interesting_terms)


MLT_PARAM_NAMES = {
    "fl", "qf", "mintf", "mindf", "minwl", "maxwl", "maxqt", "maxntp",
    "maxdf", "maxdfpct", "boost", "interestingTerms", "match.include",
}


def parse_overrides(text: str) -> dict:
    """
    'mindf=10 maxdfpct=10 rows=5' -> {'mlt.mindf': '10', 'mlt.maxdfpct': '10', 'rows': '5'}
    Nur echte MLT-Parameter erhalten das Präfix 'mlt.', andere (z. B. rows) bleiben unverändert.
    """
    params = {}
    for part in text.split():
        if "=" in part:
            k, v = part.split("=", 1)
            if k in MLT_PARAM_NAMES:
                k = f"mlt.{k}"
            params[k] = v
    return params


def interactive_mlt():
    print("MoreLikeThis (MLT) – Ähnlichkeitssuche im Solr-Core 'pg_fulltexts'")

    if not create_mlt_handler_if_not_exists():
        print("Abbruch: MLT-Handler konnte nicht erstellt werden.")
        return

    solr = pysolr.Solr(SOLR_CORE_URL, timeout=60)

    while True:
        try:
            user_query = input("\nSuchanfrage (oder 'quit!' zum Beenden): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAuf Wiedersehen!")
            break

        if not user_query:
            continue
        if user_query.lower() in ["quit!", "exit", "q", "beenden"]:
            print("Auf Wiedersehen!")
            break

        top1 = search_top1(solr, user_query)
        if not top1:
            continue

        print("\nTop-1-Treffer (Ausgangsdokument für MLT):")
        print_doc(top1, "  ")

        print("\nErmittle ähnlichste E-Books...")
        show_similar(top1["id"])

        print("\nMLT-Parameter testen? (z. B. 'mindf=10 maxdfpct=10', leer = weiter, 'quit' = Ende)")
        override = input("  Eingabe: ").strip()
        if override.lower() in ["quit", "q", "beenden"]:
            break
        if override:
            print("\nTeste MLT mit angepassten Parametern...")
            show_similar(top1["id"], parse_overrides(override))


if __name__ == "__main__":
    interactive_mlt()
import pysolr
import locale
from datetime import datetime

SOLR_CORE_URL = "http://localhost:8983/solr/pg_fulltexts"
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

def search(solr, query):
    params = {
        "qf": "title^5 authors^2 subjects fulltext^2 fulltext_alternative^3",     # Gewichtung der Felder, die durchsucht werden
        "defType": "edismax",      
        "mm": "10%",  
        "q.op": "OR",
        "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",                                                    # Erweiterte DisMax-Suche
        "rows": 10,                                                                 # maximale Anzahl der Suchergebnisse
        "fl": "id, title, issued, authors, language, subjects, score",        # Felder, die zurückgegeben werden
    }

    results = solr.search(query, **params)  # Top-10-Ranking ermitteln
    if not results or len(results) == 0:
        print("Ihre Suchanfrage liefert keine Treffer!")
        return

    print(f"\n* * * Insgesamt {results.hits} Suchergebnisse gefunden – {len(results)} Treffer werden angezeigt. * * *\n")

    # einzelne Suchergebnisse ausgeben
    for i, result in enumerate(results, start=1):
        issued = datetime.fromisoformat(result.get("issued").replace("Z", "+00:00"))
        print(f"""Rang # {i} (ID: {result.get('id')}): {result.get("title")}
          Autor: {", ".join(result.get("authors"))}
          Aufnahmedatum: {issued:%d. %B %Y}
          Sprache: {', '.join(result.get('language'))}
          Themengebiete: {', '.join(result.get('subjects'))}
          Score-Wert: {result.get("score")}""")

if __name__ == "__main__":
    print("Gib eine Suchanfrage ein oder 'quit!' zum Verlassen.")
    solr = pysolr.Solr(SOLR_CORE_URL)

    while True:
        user_query = input("Suchanfrage: ").strip()
        if user_query.lower() == "quit!":
            break
        elif user_query:
            search(solr, user_query)

import json
import requests
import pysolr

SOLR_BASE = "http://localhost:8983/solr"
CORE_NAME = "pg_fulltexts"          # oder deine Collection/Core
HANDLER_NAME = "/mlt"              # mit führendem /

url = f"{SOLR_BASE}/{CORE_NAME}/config/requestHandler"
def search(solr, query):
    # Alle Request Handler holen
    response = requests.get(url)
    data = response.json()

    # Prüfen, ob der Handler da ist
    handlers = data.get("config", {}).get("requestHandler", {})
    exists = HANDLER_NAME in handlers

    print(f"Handler '{HANDLER_NAME}' existiert:", exists)

    if not exists:
            # Name des neuen Handlers (mit führendem /)

        # 1. Request Handler anlegen via Config API

        config_url = f"{SOLR_BASE}/{CORE_NAME}/config"

        payload = {
            "add-requesthandler": {
                "name": HANDLER_NAME,
                "class": "solr.MoreLikeThisHandler",
                "defaults": {
                        "mlt.fl": "fulltext",
                        "mlt.mindf": 5,
                        "mlt.mintf": 2,
                        "mlt.minwl": 5,
                        "mlt.maxdfpct": 25,
                        "mlt.interestingTerms": "list",
                        "mlt.match.include": "false",
                        "mlt.boost": "true",
                },
                # optional:
                # "invariants": {"fq": "type:product"},
                # "appends": {"fq": ["category:electronics"]},
                # "useParams": "mein_paramset"
            }
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            config_url,
            data=json.dumps(payload),
            headers=headers,
            # auth=("user", "pass")  # falls Basic Auth nötig
        )

        print("Status:", response.status_code)
        print(response.json())

        if response.status_code == 200:
            print(f"Request Handler '{HANDLER_NAME}' erfolgreich angelegt.")
        else:
            print("Fehler beim Anlegen:", response.text)

    if exists:
        print(f"Request Handler '{HANDLER_NAME}' existiert bereits. Suche wird durchgeführt.")
        
        # Suche über den neuen Handler
        params = {
            "defType": "edismax",
            "qf": "title^5 authors^2 subjects^1 fulltext^2 fulltext_alternative^3",
            "q.op": "OR",
            "mm": "10%",
            "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",
            "rows": 1,
            "fl": "id,title,authors"      # Felder, die zurückgegeben werden
            }

       
        

        results = solr.search(query, **params)  # Top-10-Ranking ermitteln
        if not results or len(results) == 0:
            print("Ihre Suchanfrage liefert keine Treffer!")
            return


        for doc in results:
            print(doc.get("id"), doc.get("authors"), doc.get("title"))

        doc_id = results.docs[0].get("id")
        print(f"Suche ähnliche Dokumente für ID: {doc_id}")

        try: 
            response = requests.get(
                f"{SOLR_BASE}/{CORE_NAME}/mlt",
                    params={
                    "q": f'id:"{doc_id}"',
                    "rows": 3,
                    "fl": "id,title,authors",
                    "wt": "json",
                    },
                timeout=10
            )
            print(f"Gefundene ähnliche Dokumente für {query}:")
            response.raise_for_status()
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            interesting_terms = data.get("interestingTerms", [])
        except requests.exceptions.RequestException as e:
            print("Boo!")

        if docs:
            for doc in docs:
                print(f"ID: {doc.get('id')}, Titel: {doc.get('title')}, Autoren: {doc.get('authors')}")
        else:
            print("Keine ähnlichen Dokumente gefunden.")    

        if interesting_terms:
            print("Interessante Terme:", interesting_terms) 


if __name__ == "__main__":
    print("Gib eine Suchanfrage ein oder 'quit!' zum Verlassen.")
    solr = pysolr.Solr(f"{SOLR_BASE}/{CORE_NAME}", timeout=60)

    while True:
        user_query = input("Suchanfrage: ").strip()
        if user_query.lower() == "quit!":
            break
        elif user_query:
            search(solr, user_query)
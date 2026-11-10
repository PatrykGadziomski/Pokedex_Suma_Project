import requests

# Solr-Konfiguration
SOLR_BASE_URL = "http://localhost:8983/solr"
SOLR_CORE_NAME = "pg_fulltexts"
SOLR_CORE_URL = f"{SOLR_BASE_URL}/{SOLR_CORE_NAME}"

# Feldtypen definieren
FIELD_TYPES = [
    {
        "name": "text_de_custom",
        "class": "solr.TextField",
        "positionIncrementGap": "100",
        "analyzer": {
            "tokenizer": {"class": "solr.StandardTokenizerFactory"},
            "filters": [
                {"class": "solr.LowerCaseFilterFactory"},
                # stopwords_de.txt liegt im Snowball-Format ("wort | Kommentar") vor,
                # daher ist format="snowball" nötig, sonst wird kein Stopwort erkannt
                {
                    "class": "solr.StopFilterFactory",
                    "words": "lang/stopwords_de.txt",
                    "format": "snowball",
                    "ignoreCase": "true",
                },
                {"class": "solr.GermanMinimalStemFilterFactory"},
            ],
        },
    },
]

# Indexfelder definieren
FIELDS = [
    {"name": "id", "type": "string", "stored": True, "indexed": True, "required": True, "multiValued": False},
    {"name": "title", "type": "text_de", "stored": True, "indexed": True, "multiValued": False},
    {"name": "authors", "type": "text_general", "stored": True, "indexed": True, "multiValued": True},
    {"name": "language", "type": "string", "stored": True, "indexed": True, "multiValued": True},
    {"name": "subjects", "type": "text_general", "stored": True, "indexed": True, "multiValued": True},
    {"name": "issued", "type": "pdate", "stored": True, "indexed": True, "multiValued": False},
    {
        "name": "fulltext",
        "type": "text_de",
        "stored": False,
        "indexed": True,
        "multiValued": False,
        "termVectors": True,  # nötig für MoreLikeThis
    },
    {
        "name": "fulltext_alternative",
        "type": "text_de_custom",
        "stored": False,
        "indexed": True,
        "multiValued": False,
    },
]

# Copy-Fields definieren
COPY_FIELDS = [
    {"source": "fulltext", "dest": "fulltext_alternative"},
]


# Hilfsfunktionen
def get_existing_field_type_names(solr_core_url: str) -> set:
    try:
        resp = requests.get(f"{solr_core_url}/schema/fieldtypes", timeout=30)
        resp.raise_for_status()
        return {t["name"] for t in resp.json().get("fieldTypes", [])}
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Feldtypen: {e}")
        return set()


def get_existing_field_names(solr_core_url: str) -> set:
    try:
        resp = requests.get(f"{solr_core_url}/schema/fields", timeout=30)
        resp.raise_for_status()
        return {f["name"] for f in resp.json().get("fields", [])}
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Felder: {e}")
        return set()


def get_existing_copy_fields(solr_core_url: str) -> set:
    try:
        resp = requests.get(f"{solr_core_url}/schema/copyfields", timeout=30)
        resp.raise_for_status()
        return {(c["source"], c["dest"]) for c in resp.json().get("copyFields", [])}
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Copy-Fields: {e}")
        return set()


def post_schema(solr_core_url: str, payload: dict, ok_message: str) -> None:
    """Sendet einen Schema-API-Befehl und gibt bei Fehlern die Solr-Antwort aus."""
    try:
        resp = requests.post(f"{solr_core_url}/schema", json=payload, timeout=60)
        if not resp.ok:
            print(f"Solr-Antwort ({resp.status_code}): {resp.text}")
            return
        body = resp.json()
        if "errors" in body:
            print(f"Solr-Fehler: {body['errors']}")
            return
        print(ok_message)
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Schema-Anfrage: {e}")


def create_core_if_not_exists():
    """Erstellt den Core pg_fulltexts, falls er noch nicht existiert."""
    try:
        resp = requests.get(
            f"{SOLR_BASE_URL}/admin/cores",
            params={"action": "STATUS", "core": SOLR_CORE_NAME},
            timeout=30,
        )
        resp.raise_for_status()
        if resp.json().get("status", {}).get(SOLR_CORE_NAME):
            print(f"Core '{SOLR_CORE_NAME}' existiert bereits.")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Warnung beim Prüfen des Cores: {e}")

    print(f"Erstelle Core '{SOLR_CORE_NAME}'...")
    try:
        params = {
            "action": "CREATE",
            "name": SOLR_CORE_NAME,
            "instanceDir": SOLR_CORE_NAME,
            "configSet": "_default",
        }
        resp = requests.get(f"{SOLR_BASE_URL}/admin/cores", params=params, timeout=60)
        if not resp.ok:
            print(f"Solr-Antwort ({resp.status_code}): {resp.text}")
            return False
        print(f"Core '{SOLR_CORE_NAME}' erfolgreich erstellt.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen des Cores: {e}")
        return False


def create_schema(solr_core_url: str = SOLR_CORE_URL) -> None:
    if not create_core_if_not_exists():
        print("Abbruch: Core konnte nicht erstellt werden.")
        return

    # Feldtypen: neu anlegen oder (falls schon vorhanden) mit aktueller Definition ersetzen
    existing_types = get_existing_field_type_names(solr_core_url)
    new_types = [t for t in FIELD_TYPES if t["name"] not in existing_types]
    replace_types = [t for t in FIELD_TYPES if t["name"] in existing_types]
    if new_types:
        post_schema(
            solr_core_url,
            {"add-field-type": new_types},
            f"{len(new_types)} Feldtyp(en) angelegt: {[t['name'] for t in new_types]}",
        )
    if replace_types:
        post_schema(
            solr_core_url,
            {"replace-field-type": replace_types},
            f"Feldtyp(en) aktualisiert: {[t['name'] for t in replace_types]}",
        )

    # Felder
    existing_fields = get_existing_field_names(solr_core_url)
    new_fields = [f for f in FIELDS if f["name"] not in existing_fields]
    if new_fields:
        post_schema(
            solr_core_url,
            {"add-field": new_fields},
            f"{len(new_fields)} Feld(er) angelegt: {[f['name'] for f in new_fields]}",
        )
    else:
        print("Alle Felder sind bereits im Schema vorhanden.")

    # Copy-Fields
    existing_copy_fields = get_existing_copy_fields(solr_core_url)
    new_copy_fields = [
        c for c in COPY_FIELDS if (c["source"], c["dest"]) not in existing_copy_fields
    ]
    if new_copy_fields:
        post_schema(
            solr_core_url,
            {"add-copy-field": new_copy_fields},
            f"{len(new_copy_fields)} Copy-Field(s) angelegt: {new_copy_fields}",
        )
    else:
        print("Alle Copy-Fields sind bereits vorhanden.")


if __name__ == "__main__":
    print("Starte Schema-Erstellung für Solr-Core 'pg_fulltexts'...")
    create_schema()
    print("\nSchema-Erstellung abgeschlossen.")
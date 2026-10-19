import requests

schema_url = "http://localhost:8983/solr/pg_fulltexts/schema"

# Vorhandene Feldtypen abfragen
response = requests.get(f"{schema_url}/fieldtypes", timeout=10)
response.raise_for_status()

vorhandene_namen = {
    feldtyp["name"]
    for feldtyp in response.json()["fieldTypes"]
}

# Eigenen Feldtyp beschreiben
neuer_feldtyp = {
    "name": "text_de_custom",
    "class": "solr.TextField",
    "analyzer": {
        "tokenizer": {
            "name": "standard"
        },
        "filters": [
            {
                "name": "lowercase"
            },
            {
                "name": "stop",
                "words": "lang/stopwords_de.txt",
                "ignoreCase": True,
                "format": "snowball"
            },
            {
                "name": "germanMinimalStem"
            }
        ]
    }
}

# Feldtyp nur anlegen, wenn er noch nicht existiert
if "text_de_custom" in vorhandene_namen:
    print("text_de_custom ist bereits vorhanden.")
else:
    response = requests.post(
        schema_url,
        json={"add-field-type": neuer_feldtyp},
        timeout=10
    )

    if not response.ok:
        print(response.text)

    response.raise_for_status()
    print("text_de_custom wurde angelegt.")


# Felder gemäß Aufgabenstellung beschreiben
felder = [
    {
        "name": "id",
        "type": "string",
        "indexed": True,
        "stored": True,
        "multiValued": False
    },
    {
        "name": "title",
        "type": "text_de",
        "indexed": True,
        "stored": True,
        "multiValued": False
    },
    {
        "name": "authors",
        "type": "text_general",
        "indexed": True,
        "stored": True,
        "multiValued": True
    },
    {
        "name": "language",
        "type": "string",
        "indexed": True,
        "stored": True,
        "multiValued": True
    },
    {
        "name": "subjects",
        "type": "text_general",
        "indexed": True,
        "stored": True,
        "multiValued": True
    },
    {
        "name": "issued",
        "type": "pdate",
        "indexed": True,
        "stored": True,
        "multiValued": False
    },
    {
        "name": "fulltext",
        "type": "text_de",
        "indexed": True,
        "stored": False,
        "multiValued": False,
        "termVectors": True
    },
    {
        "name": "fulltext_alternative",
        "type": "text_de_custom",
        "indexed": True,
        "stored": False,
        "multiValued": False
    }
]

# Bereits vorhandene Felder ermitteln
response = requests.get(f"{schema_url}/fields", timeout=10)
response.raise_for_status()

vorhandene_felder = {
    feld["name"]
    for feld in response.json()["fields"]
}

# Vorhandene Felder anpassen, fehlende Felder anlegen
for feld in felder:
    if feld["name"] in vorhandene_felder:
        aktion = "replace-field"
    else:
        aktion = "add-field"

    response = requests.post(
        schema_url,
        json={aktion: feld},
        timeout=10
    )

    if not response.ok:
        print(response.text)

    response.raise_for_status()
    print(f"Feld eingerichtet: {feld['name']}")


# Vorhandene Copy-Field-Regeln abfragen
response = requests.get(f"{schema_url}/copyfields", timeout=10)
response.raise_for_status()

kopierregeln = response.json()["copyFields"]

regel_vorhanden = any(
    regel["source"] == "fulltext"
    and regel["dest"] == "fulltext_alternative"
    for regel in kopierregeln
)

if regel_vorhanden:
    print("Copy-Field-Regel ist bereits vorhanden.")
else:
    response = requests.post(
        schema_url,
        json={
            "add-copy-field": {
                "source": "fulltext",
                "dest": "fulltext_alternative"
            }
        },
        timeout=10
    )

    if not response.ok:
        print(response.text)

    response.raise_for_status()
    print("Copy-Field-Regel wurde angelegt.")

# Gespeicherte Feldeinstellungen prüfen
response = requests.get(
    f"{schema_url}/fields",
    params={"showDefaults": "true"},
    timeout=10
)
response.raise_for_status()

gespeicherte_felder = {
    feld["name"]: feld
    for feld in response.json()["fields"]
}

for soll_feld in felder:
    name = soll_feld["name"]
    ist_feld = gespeicherte_felder.get(name, {})

    abweichungen = [
        eigenschaft
        for eigenschaft, soll_wert in soll_feld.items()
        if ist_feld.get(eigenschaft) != soll_wert
    ]

    if abweichungen:
        print(f"Abweichung bei {name}: {', '.join(abweichungen)}")
    else:
        print(f"Geprüft: {name} – OK")
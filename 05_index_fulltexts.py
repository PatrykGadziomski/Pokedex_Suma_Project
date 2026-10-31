import re
import pysolr
from pathlib import Path

FILE_PATH = Path("/Users/miros/PA_IndexingAndRetrieval/ebook_ids.txt")
BATCH_SIZE = 1000
ORIG_SOLR_CORE_URL = "http://localhost:8983/solr/my1stcore"
DEST_SOLR_CORE_URL = "http://localhost:8983/solr/pg_fulltexts"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$") 
value = "id,title,authors,language,subjects,issued"

def index_metadata():
   def split_multivalue(value: str) -> list:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]

   orig_solr = pysolr.Solr(ORIG_SOLR_CORE_URL, timeout=60, always_commit=False)
   dest_solr = pysolr.Solr(DEST_SOLR_CORE_URL, timeout=60, always_commit=False)

   with open(FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            ebook_id = line.strip()
            if ebook_id:
                print(ebook_id) 

                row = orig_solr.search(
                                    f'id:"{ebook_id}"',
                                    fl="id,title,authors,language,subjects,issued",
                                    rows=1
                                    )

                p = Path(f"/Users/miros/PA_IndexingAndRetrieval/fulltexts/{ebook_id}_filtered.txt")
                if p.exists():
                    with open(p, "r", encoding="utf-8") as f:
                     fulltext = f.read()


                doc = {
                    "id": ebook_id,
                    "title": row.docs[0].get("title") or None,
                    "language": row.docs[0].get("language", []) or "",
                    "authors": row.docs[0].get("authors", []) or "",
                    "subjects": row.docs[0].get("subjects", []) or "",
                    "issued": row.docs[0].get("issued") or None,
                    "fulltext": fulltext,
                    }

                

                print(f"Dokument für E-Book-ID {ebook_id} erstellt: Volltext hat {len(fulltext)} Zeichen")

                total = 0
                batch = []
          
                if row:
                    batch.append(row.docs[0])
                    if len(batch) >= BATCH_SIZE:
                        dest_solr.add(batch)
                        total += len(batch)
                        print(f"{total} Dokumente indexiert.")
                        batch = []

                    if batch:
                        dest_solr.add(batch)
                        total += len(batch)

                dest_solr.commit()
                print(f"{total} Metadatensätze indexiert und erfolgreich in Solr gespeichert.")

if __name__ == "__main__":
    index_metadata()

import os
from nltk.stem import SnowballStemmer

def compute_terms_per_author(input_dir, stemmer=none):
    """
    Berechnet die Menge der Terme in allen Werken eines Autors, indem die Tokens aus den ".tokens"-Dateien gelesen
    und optional gestemmt werden. Die berechneten Terme werden in einer neuen Datei "terms.txt" im jeweiligen
    Autorenverzeichnis gespeichert. Hierbei erfolgt die Ausgabe der Terme in lexikographischer Reihenfolge. Zusätzlich
    wird die Anzahl der Terme sowie die Gesamtanzahl der Tokens für jeden Autor ausgegeben.

    Parameter:
    - input_dir (str): Der Pfad zum Hauptverzeichnis, das die Unterverzeichnisse der Autoren enthält.
    - stemmer (SnowballStemmer): Der Stemmer, der verwendet werden soll (Standard: None, wenn kein Stemming gewünscht ist).
    """
    # Suche in Autorverzeichnissen nach Textdateien mit der Endung ".tokens"
    for author_dir in os.listdir(input_dir):
        author_path = os.path.join(input_dir, author_dir)
        if os.path.isdir(author_path):
            terms = set()
            num_of_tokens = 0
            # alle Tokens in einer Menge sammeln, so dass jedes Token nur einmal betrachtet wird
            for filename in os.listdir(author_path):
                if filename.endswith(".tokens"):
                    file_path = os.path.join(author_path, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        for token in f:
                            if stemmer:
                                token = stemmer.stem(token.strip())
                            else:
                                token = token.strip()
                            if token:
                                num_of_tokens += 1
                                terms.add(token)
            print(f"Anzahl Terme / Tokens für Autor {author_dir}: {len(terms)} / {num_of_tokens}")
            with open(os.path.join(author_path, "terms.txt"), "w", encoding="utf-8") as f:
                for term in sorted(terms):
                    f.write(term + "\n")

if __name__ == "__main__":
    input_dir = "german-works"
    stemmer = SnowballStemmer("german")
    compute_terms_per_author(input_dir, stemmer)
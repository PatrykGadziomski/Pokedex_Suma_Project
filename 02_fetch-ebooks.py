import requests
import re
import os
import time
from pathlib import Path

def download_file(url, output_file):
    """
    Lädt eine UTF-8-codierte Textdatei von der angegebenen URL herunter und speichert sie als UTF-8-codierte Textdatei
    unter dem angegebenen Namen im lokalen Dateisystem. Bei der Textdatei handelt es sich um den Volltext eines
    E-Books aus dem Project Gutenberg. Die Funktion wartet zufällig zwischen 0.5 und 2 Sekunden, bevor sie die Datei
    von der angegebenen URL herunterlädt, um den Webserver von Project Gutenberg nicht zu überlasten.

    Parameter:
    - url (str): URL der Textdatei, die vom Project Gutenberg heruntergeladen werden soll.
    - output_file (str): Der Name der lokal abzuspeichernden Datei.
    """

    # zwischen 0.5 und 2 Sekunden zufällig warten
    time.sleep(0.5 + 1.5 * (os.urandom(1)[0] / 255))

    response = requests.get(url, timeout=60, stream=True)
    response.encoding = 'utf-8'
    if response.status_code == requests.codes.ok:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Datei erfolgreich heruntergeladen und gespeichert unter {output_file}")
        return True

    print(f"Fehler beim Herunterladen der Datei von URL {url}: {response.status_code}")
    return False

if __name__ == "__main__":

    base_dir = Path("/Users/miros/PA_IndexingAndRetrieval/fulltexts")
    FILE_PATH = Path("/Users/miros/PA_IndexingAndRetrieval/ebook_ids.txt")
    num_of_downloads = 0
    num_of_overall_downloads = 0
    num_of_errors = 0


    with open(FILE_PATH, "r", encoding="utf-8") as file:
        for text in file:      
            ebook_id = text.strip()
            if ebook_id:
                url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"
                print(f"Herunterladen der Textdatei von {url}")
                output_file = os.path.join(base_dir, f"{ebook_id}.txt")
                if download_file(url, output_file):
                    num_of_downloads += 1
                else:
                    num_of_errors += 1
            print(f"{num_of_downloads} Volltextdateien heruntergeladen.\n")
            num_of_overall_downloads += num_of_downloads

    print(f"Insgesamt {num_of_overall_downloads} Volltextdateien erfolgreich heruntergeladen (Anzahl Fehler: {num_of_errors}).")
  




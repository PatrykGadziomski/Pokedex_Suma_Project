import requests
import re
import os
import time

def download_file(url, filename):
    """
    Lädt eine UTF-8-codierte Datei von der angegebenen URL herunter und speichert sie als UTF-8-codierte Textdatei
    unter dem angegebenen Namen.

    Parameter:
    - url (str): URL der Datei, die vom Project Gutenberg heruntergeladen werden soll.
    - filename (str): Der Name der lokal abzuspeichernden Datei.
    """

    # zwischen 0.5 und 2 Sekunden zufällig warten, um Project Gutenberg Server nicht zu überlasten
    time.sleep(0.5 + 1.5 * (os.urandom(1)[0] / 255))

    response = requests.get(url, timeout=60, stream=True)
    response.encoding = 'utf-8'
    if response.status_code == requests.codes.ok:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Datei erfolgreich heruntergeladen: {filename}")
        return True

    print(f"Fehler beim Herunterladen der Datei {filename}: {response.status_code}")
    return False

if __name__ == "__main__":
    base_dir = "german-works"
    if not os.path.exists(base_dir):
        print(f"Der Ordner '{base_dir}' existiert nicht. Bitte zuerst die URLs der E-Books ermitteln.")
        exit(1)

    num_of_downloads = 0
    for filename in os.listdir(base_dir):
        if filename.endswith("-ebook-urls.txt"):
            author_name = filename.replace("-ebook-urls.txt", "")
            file_path = os.path.join(base_dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for base_url in file:
                    match = re.search(r"/ebooks/(\d+)$", base_url)
                    if match:
                        ebook_id = match.group(1)
                        url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"
                        print(f"Herunterladen von {url}")
                        if not os.path.exists(os.path.join(base_dir, author_name)):
                            os.makedirs(os.path.join(base_dir, author_name))
                        output_file = os.path.join(base_dir, f"{author_name}", f"{ebook_id}.txt")
                        if download_file(url, output_file):
                            num_of_downloads += 1
            print(f"{num_of_downloads} Volltextdateien für Autor {author_name} heruntergeladen.")

    print(f"{num_of_downloads} Volltextdateien erfolgreich heruntergeladen.")
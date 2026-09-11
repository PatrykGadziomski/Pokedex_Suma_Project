# Projektarbeit Suchmaschinentechnologie Bibliotheksinformatik BIM-25

## Projektaufgabe 1: Harvesting und Analyse von ausgewählten Volltexten aus dem Project Gutenberg

Im ersten Schritt wollen wir uns einen Korpus von Werken in deutscher Sprache aus dem Project Gutenberg zusammenstellen.

**Hinweis**: Legen Sie vor der Ausführung der nachfolgend beschriebenen Python-Skripte eine virtuelle Python-Umgebung an
(wie in der Vorlesung demonstriert) und installieren Sie zuerst die benötigten Python-Pakete mit dem Befehl
`pip install -r requirements.txt`. In der Datei `requirements.txt` sind die benötigten Python-Pakete aufgelistet.

### Harvesting ausgewählter Volltextdateien aus dem Project Gutenberg

Das Beziehen der Volltextdateien erfolgt in zwei Schritten:

1. Zunächst wollen wir die URLs (aus dem Project Gutenberg) der deutschsprachigen Werke ausgewählter Autoren sammeln.
Hierfür kann das Python-Skript `01_fetch-german-work-urls-by-author.py` genutzt werden. Im Programm werden dazu 10
Autoren definiert. Jeder Autor hat eine eindeutige ID im Project Gutenberg. Für jeden Autor wird die Übersichtsseite mit
den zugehörigen Werken im Project Gutenberg abgerufen und die URLs der einzelnen Werke eingesammelt. Hierbei werden nur
die Werke berücksichtigt, die in deutscher Sprache verfasst wurden. Aus dieser Übersichtsseite (HTML) werden die URLs
der einzelnen Werke extrahiert. Wenn erforderlich folgt das Programm der Paginierung, um Folgeseiten aufzurufen. Die
eingesammelten URLs werden zeilenweise in Textdateien (eine Datei pro Autor) gespeichert. Die Textdateien mit den URLs
werden in einem Unterverzeichnis namens `german-works` abgelegt, wobei die Dateinamen das Format
`{author_name}-ebook-urls.txt` haben.

2. Im nächsten Schritt wollen wir die gesammelten URLs der Werke aus dem vorherigen Schritt nutzen, um schließlich die
Volltextdateien der Werke aus dem Project Gutenberg in der UTF-8-Kodierung herunterzuladen. Hierfür kann das
Python-Skript `02_fetch-works.py` genutzt werden. Das Skript liest die zuvor in Textdateien (eine Datei pro Autor)
gespeicherten URLs der Werke ein, lädt die entsprechenden Volltextdateien (in UTF-8-Kodierung) herunter und speichert
die Volltextdateien in einem Unterverzeichnis mit dem Namen des Autors innerhalb des Verzeichnisses `german-works` ab.
Die Dateinamen der Volltextdateien folgen dem Format `{work_id}.txt` gespeichert, wobei `{work_id}` die eindeutige ID
des Werks im Project Gutenberg ist.

### Vorverarbeitung der Volltextdateien

Wir haben schon in der Vorlesung diskutiert, dass die Volltextdateien aus dem Project Gutenberg Header und Footer
enthalten, die nicht zum eigentlichen Text des Werks gehören. Im nächsten Schritt wollen wir Header und Footer
entfernen, um nur den reinen Text des Werks zu erhalten. Hierfür kann das Python-Skript `03_remove-header-footer.py`
genutzt werden. Das Skript liest die zuvor heruntergeladenen Volltextdateien ein, entfernt Header und Footer und
speichert die bereinigten Volltextdateien in einem Unterverzeichnis mit dem Namen des Autors innerhalb des
Verzeichnisses `german-works` ab. Die Dateinamen der bereinigten Volltextdateien folgen dem Format
`{work_id}.txt.clean`.

### Vom Text zum Token: Tokenisierung der bereinigten Volltextdateien

Wir wollen nun - analog zum Vorgehen in der Vorlesung - eine einfache Whitespace-Tokenisierung auf Basis der bereinigten
Volltextdateien (in den Textdateien mit der Endung `.txt.clean`) durchführen. Hierfür kann das Python-Skript
`04_tokenize-works.py` genutzt werden. Das Skript liest die bereinigten Volltextdateien ein, führt eine einfache
Whitespace-Tokenisierung durch und speichert die erzeugten Token-Listen in der Datei `{work_id}.tokens` im Verzeichnis
`german-works/{author_name}` ab. Pro Zeile wird ein Token gespeichert, wobei die Tokens vor der
Speicherung in Kleinbuchstaben umgewandelt werden und nicht-alphabetische Zeichen am Anfang und Ende des Tokens entfernt
werden. Außerdem müssen Tokens aus mindestens vier Zeichen bestehen, damit sie in die Token-Listen aufgenommen werden.

### Vom Token zum Term

Mit dem Python-Skript `05_compute-terms-per-author.py` können die erzeugten Token-Listen der Werke eines Autors
eingelesen und die einzigartigen Tokens, die als Terme bezeichnet werden, für jeden Autor berechnet werden. Die
berechneten Terme (pro Autor) werden schließlich in der Datei `terms.txt` im Autor-Verzeichnis (innerhalb von
`german-works/{author_name}`) gespeichert, wobei pro Zeile ein Term gespeichert wird. Die Terme werden vor der Ausgabe
in lexikographischer Reihenfolge sortiert.

Das Skript gibt für jeden Autor die Anzahl der berechneten Terme sowie die Anzahl der Token in allen Werken aus.

Im Skript kann optional die Stemming-Funktionalität aktiviert werden, um die Terme durch Stemming zu reduzieren. Hierfür
kann die Variable `stemmer`mit einem Stemming-Objekt aus der NLTK-Bibliothek initialisiert werden. Beispielsweise kann
ein Snowball-Stemmer für die deutsche Sprache verwendet werden, indem die Variable `stemmer = SnowballStemmer("german")`
gesetzt wird. Wenn die Stemming-Funktionalität aktiviert ist, werden die Tokens vor der Aufnahme in die Term-Menge
auf ihren Wortstamm reduziert. Das Stemming führt somit zu einer Reduktion der Termanzahl, da verschiedene Tokens
auf denselben Stamm (und damit identische Terme) reduziert werden können.

## Berechnung der Autor-Ähnlichkeit auf Basis der Termlisten ihrer Werke

Wir wollen nun die Ähnlichkeit von Autoren auf Basis der Termlisten ihrer Werke untersuchen. Hierfür kann das
Python-Skript `06_compute-author-similarity.py` genutzt werden. Das Skript liest die zuvor berechneten Termlisten der
Werke der Autoren ein (aus den Dateien `terms.txt`), berechnet für jedes Autorenpaar _(author_A, author_B)_ die
Ähnlichkeit auf Basis der zugehörigen Termlisten, _similarity(author_A, author_B)_, und speichert die berechneten
Ähnlichkeitswerte schließlich in einer CSV-Datei mit dem Namen `author-similarity_{mode}.csv` ab. Die CSV-Datei enthält
drei Spalten `author_1`, `author_2` und `similarity`, wobei `author_1` und `author_2` die Namen der Autoren und
`similarity` der für das Autor paar berechnete Ähnlichkeitswert ist. Für die Berechnung der Ähnlichkeit von zwei
Termlisten können verschiedene Ähnlichkeitsmaße verwendet werden, wie z.B.

* Jaccard-Ähnlichkeit: Jaccard-Similarity(A1, A2) = S / V, wobei S die Größe der Schnittmenge der Term-Mengen der Autoren
A1 und A2 ist, also die Anzahl der Terme, die in Werken beider Autoren vorkommen, und V die Größe der Vereinigungsmenge
der Term-Mengen von A1 und A2 ist, also die Anzahl der Terme, die in mindestens einem Werk der beiden Autoren
vorkommen.
* Dice-Ähnlichkeit: Dice-Similarity(A1, A2) = 2 * S / (T1 + T2), wobei S die Größe der Schnittmenge der Term-Mengen der
Autoren ist und T1 bzw. T2 die Anzahl der Terme in den Term-Mengen von A1 bzw. A2 ist. Die Formel kann umgeschrieben
werden zu Dice-Similarity(A1, A2) = S / 0.5 * (T1 + T2). Im Nenner steht nun der aritmetische Mittelwert der Anzahl der
Terme in den Term-Mengen von A1 und A2.
* Otsuka-Ochiai-Ähnlichkeit: OtsukaOchiai-Similarity(A1, A2) = S / sqrt(T1 * T2). Im Nenner steht hier der geometrische
Mittelwert der Anzahl der Terme in den Term-Mengen von A1 und A2.

Alle drei Ähnlichkeitsmaße können Werte zwischen 0 und 1 annehmen, wobei 0 bedeutet, dass die Autoren keine gemeinsamen
Terme haben, und 1 bedeutet, dass die Autoren identische Term-Mengen haben. Je höher der Ähnlichkeitswert, desto
ähnlicher sind die Autoren auf Basis der Term-Mengen ihrer Werke. Alle Ähnlichkeitsmaße sind symmetrisch, d.h. es gilt
similarity(A1, A2) = similarity(A2, A1). Daher brauchen wir für jedes Autorenpaar nur einmal die Ähnlichkeit zu
berechnen.

Das Skript ermöglicht die Auswahl des Ähnlichkeitsmaßes über die Variable `mode`, die auf einen der Werte `"jaccard"`
(Default), `"dice"` oder `"otsuka-ochiai"` gesetzt werden kann.

## Darstellung der Ähnlichkeitswerte in einer Heatmap

Wir wollen nun die berechneten Ähnlichkeitswerte für alle Autorenpaare in einer Heatmap visualisieren.
Hierfür kann das Python-Skript `07_author-similarity-heatmap.py` genutzt werden. Das Skript liest die zuvor berechneten
Ähnlichkeitswerte aus der CSV-Datei `author-similarity_{mode}.csv` ein, erstellt eine Heatmap der Ähnlichkeitswerte und
speichert die Heatmap als Bilddatei mit dem Namen `author-similarity_{mode}.png` ab. In der zweidimensionalen Heatmap
werden die Autoren auf den Achsen dargestellt. In einer Zelle steht der Ähnlichkeitswert des Autorenpaares, das sich aus
Zeile und Spalte ergibt. Die Farbintensität der Zellen repräsentiert die Größe der Ähnlichkeitswerte, wobei eine höhere
Farbintensität eine höhere Ähnlichkeit zwischen den Autoren (genauer den Term-Mengen ihrer Werke) anzeigt.

## Aufgaben

1. Führen Sie die zuvor beschriebenen Schritte (1 bis 4) zur Erstellung eines Korpus von Werken in deutscher Sprache aus
dem Project Gutenberg durch, indem Sie die Python-Skripte in der angegebenen Reihenfolge ausführen. Überprüfen Sie
die Ergebnisse nach jedem Schritt, um sicherzustellen, dass die Daten korrekt verarbeitet werden.

2. Erzeugen Sie für jeden Autor die Termliste seiner Werke, indem Sie das Skript `05_compute-terms-per-author.py`
ausführen.

3. Berechnen Sie die Ähnlichkeit der Autoren auf Basis der Termlisten ihrer Werke, indem Sie das Skript
`06_compute-author-similarity.py` mit den verschiedenen Ähnlichkeitsmaßen (Jaccard, Dice, Otsuka-Ochiai) ausführen.

4. Erstellen Sie auf Grundlage der berechneten Ähnlichkeitswerte (drei CSV-Dateien) zugehörige Heatmaps der berechneten
Ähnlichkeitswerte für die verschiedenen Ähnlichkeitsmaße, indem Sie das Skript
`07_author-similarity-heatmap.py` ausführen. Vergleichen Sie die berechneten Heatmaps für die verschiedenen
Ähnlichkeitsmaße und diskutieren Sie die Gemeinsamkeiten sowie Unterschiede.

5. Entwickeln Sie ein eigenes Python-Skript, das die 10 Paare von Werken ermittelt, die die höchste Jaccard-Ähnlichkeit
aufweisen. Geben Sie für jedes der zehn Paare die Namen der Werke sowie die zugehörigen Autoren und den berechneten
Jaccard-Ähnlichkeitswert aus. Beim Vergleich sollen auch Paare von Werken desselben Autors berücksichtigt werden.

Bestimmen Sie anschließend für die Werke, die in den zehn Paaren mit der höchsten Jaccard-Ähnlichkeit vorkommen,
eine Heatmap der Jaccard-Ähnlichkeitswerte zwischen diesen Werken (die Heatmap kann somit höchstens 20 Zeilen und 20
Spalten umfassen). Vergleichen Sie die berechnete Heatmap mit der zuvor berechneten Heatmap der Jaccard-Ähnlichkeitswerte
zwischen den Autoren (bzw. ihren Term-Mengen).

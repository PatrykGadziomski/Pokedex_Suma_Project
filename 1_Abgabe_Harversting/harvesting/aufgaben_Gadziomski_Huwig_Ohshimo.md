# Aufgaben Suchmaschinentechnologie

---
Authoren: Patryk Gadziomski, Annabell Huwig, Hiromi Ohshimo
Semester: Sommersemester 2026
Studiengang: Bibliotheksinfomratik 2025
Abgabedatum: 08.09.2026
---

## Aufgabe 4
Die drei Heatmaps basieren auf denselben Termmengen der Autoren, unterscheiden sich jedoch in der Normalisierung der gemeinsamen Terme. 

Die Jaccard-Ähnlichkeit teilt die Schnittmenge durch die Vereinigungsmenge und liefert daher die niedrigsten Werte. Die Werte außerhalb der Hauptdiagonale liegen überwiegend zwischen 0,15 und 0,27. Jaccard ist gut interpretierbar (Anteil der gemeinsamen Terme an allen Termen, die bei mindestens einem der beiden Autoren vorkommen.) Die Metrik ist relativ streng und eignet sich gut für Mengenvergleiche.

Der Dice-Koeffizient normalisiert die Schnittmenge durch das arithmetische Mittel der Mengengrößen und erzeugt entsprechend höhere Werte zwischen ungefähr 0,26 und 0,43. Dice betont die gemeinsamen Terme etwas stärker. Es liefert höhere Werte und kann dadurch Unterschiede visuell deutlicher darstellen. Da Dice mathematisch direkt aus Jaccard berechnet werden kann, liefert es allerdings keine grundsätzlich neue Rangfolge.

Der Otsuka-Ochiai-Koeffizient verwendet das geometrische Mittel und liefert Werte zwischen ungefähr 0,28 und 0,44. Otsuka-Ochiai ist besonders hilfreich, wenn die Termmengen stark unterschiedliche Größen besitzen. Es verhindert, dass ein Autor mit einer sehr großen Termmenge automatisch einen besonders niedrigen Vergleichswert erhält. Für Autoren mit unterschiedlich vielen oder unterschiedlich langen Werken kann diese Metrik deshalb interessant sein.

Die höheren Werte der Dice- und Otsuka-Ochiai-Heatmaps bedeuten nicht, dass die Autoren nach diesen Verfahren tatsächlich ähnlicher sind. Vielmehr entstehen sie durch eine andere Normierung. Die Wahl der Metrik beeinflusst daher vor allem die numerische Höhe der Werte und teilweise die Gewichtung unterschiedlich großer Termmengen, während die grundlegenden Ähnlichkeitsmuster weitgehend erhalten bleiben.


## Aufgabe 5

Die bisherige Autoren-Heatmap vergleicht jeweils die Vereinigung der Termmengen aller Werke eines Autors. Dadurch besitzt ein Autor eine sehr große und vielfältige Termmenge. Die neue Heatmap vergleicht dagegen einzelne Werke.

Die Jaccard-Ähnlichkeit berücksichtigt keine Häufigkeiten. Ein Term, der tausendmal vorkommt, zählt genauso wie ein Term, der nur einmal vorkommt. Verglichen wird ausschließlich, ob ein Term in der jeweiligen Menge enthalten ist.

Die Heatmap der einzelnen Werke weist eine größere Verschiedenheit der Jaccard-Ähnlichkeitswerte auf als die zuvor erstellte Autoren-Heatmap. Dies lässt sich dadurch erklären, dass bei der Autorenanalyse sämtliche Werke eines Autors zu einer gemeinsamen Termmenge vereinigt wurden. Dadurch werden werkbezogene Besonderheiten abgeschwächt und die Ähnlichkeitswerte geglättet. 

Bei der Analyse einzelner Werke werden dagegen thematische, stilistische und gattungsspezifische Gemeinsamkeiten deutlicher sichtbarer. Werke desselben Autors weisen teilweise hohe Ähnlichkeiten auf, allerdings treten auch hohe Ähnlichkeiten zwischen Werken verschiedener Autoren auf. Die beiden Zuordnungen des gemeinsamen Briefwerks von Goethe und Schiller erreichen sogar einen Wert von 1,00. Dies deutet darauf hin, dass dieselbe oder eine vollständig identische Termmenge in den Verzeichnissen beider Autoren vorliegt.

Kommt es zu sehr großer Übereinstimmung, sollte man die verglichenen Werke genauer überprüfen. Zwei Gutenberg-Dateien können verschiedene Ausgaben desselben Werks sein oder nahezu identische Texte enthalten. Ein hoher Wert bedeutet daher nicht automatisch, dass zwei eigenständige Werke besonders ähnlich verfasst wurden. Bei unterschiedlichen Ausgaben des gleichen Werks eines Autoren, kann es zu durchaus größeren Abweichungen der Werke voneinander kommen (z.B. ein wert von 0.75 bei "Faust - der Tragödie erster Teil ID 21000 und 2229).

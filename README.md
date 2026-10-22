Team workflow and GitHub guidelines

1. Track your work with Issues. Create an issue for each concrete task, assign yourself and briefly describe the expected result. Update it with progress or problems so everyone knows what is happening.
2. Use separate branches. Work on a branch with a clear name such as feature/camera-capture or docs/backend-setup. Keep main as our working, integrated version.
3. Submit changes through Pull Requests. Explain what you changed and how you tested it. Before merging anything into main, please arrange a short meeting with Leo or Tomer to review the changes together. This will help us keep main stable and avoid breaking existing functionality. Keep commits small and use meaningful messages.
5. Document while you work. Each component should explain its purpose, setup, dependencies, configuration and how to run it. Record experiments, results and limitations. Our online documentation is a required deliverable, so everyone should contribute to it.
6. Agree on interfaces early. Coordinate shared details such as detection event formats, API endpoints, message topics and storage locations. This will help us connect the camera, detection, backend, monitoring and tracking components.
7. Keep large files and secrets out of Git. Do not commit passwords, tokens, datasets, videos or large model files. Use agreed storage locations and document how to access them. Provide example configuration files without real credentials.
8. Integrate and test regularly. Start with a small working version of your component and connect it to the others early. Save test results and measurements so we can use them in our evaluation and final presentation.

===============================================================================================================================================================================================================================

Zusammenarbeit im Team und GitHub-Richtlinien

1. Verfolgt eure Aufgaben über Issues. Erstellt für jede konkrete Aufgabe ein Issue, weist es euch selbst zu und beschreibt kurz das erwartete Ergebnis. Aktualisiert es bei Fortschritten oder Problemen, damit alle auf dem Laufenden bleiben.
2. Verwendet separate Branches. Arbeitet auf einem Branch mit einem eindeutigen Namen wie feature/camera-capture oder docs/backend-setup. Der Branch main soll unsere funktionsfähige, zusammengeführte Version enthalten.
3. Reicht Änderungen über Pull Requests ein. Beschreibt, was ihr geändert und wie ihr es getestet habt. Bevor ihr etwas in main zusammenführt, vereinbart bitte ein kurzes Meeting mit Leo oder Tomer, um die Änderungen gemeinsam zu prüfen. So halten wir main stabil und vermeiden, dass bestehende Funktionen beeinträchtigt werden. Haltet eure Commits klein und verwendet aussagekräftige Commit-Nachrichten.
4. Dokumentiert während der Arbeit. Beschreibt für jede Komponente ihren Zweck, die Einrichtung, Abhängigkeiten, Konfiguration und die Schritte zum Starten. Haltet auch Experimente, Ergebnisse und Einschränkungen fest. Die Online-Dokumentation ist ein verpflichtender Bestandteil des Projekts, deshalb sollten alle dazu beitragen.
5. Stimmt Schnittstellen frühzeitig ab. Klärt gemeinsame Details wie das Format von Erkennungsereignissen, API-Endpunkte, Nachrichten-Topics und Speicherorte. Dadurch können wir die Komponenten für Kameras, Erkennung, Backend, Monitoring und Tracking leichter miteinander verbinden.
6. Haltet große Dateien und Zugangsdaten aus Git heraus. Committet keine Passwörter, Tokens, Datensätze, Videos oder großen Modelldateien. Nutzt dafür vereinbarte Speicherorte und dokumentiert den Zugriff. Stellt Beispielkonfigurationen ohne echte Zugangsdaten bereit.
7. Integriert und testet regelmäßig. Beginnt mit einer kleinen, funktionsfähigen Version eurer Komponente und verbindet sie frühzeitig mit den anderen Komponenten. Speichert Testergebnisse und Messwerte, damit wir sie für die Auswertung und die Abschlusspräsentation verwenden können.

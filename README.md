## Anforderungen

- Python muss auf dem System installiert sein. 
- Das Programm erfordert die Installation einiger externer Bibliotheken und richtet eine virtuelle Python Umgebung ein. 

(ToDo: Windows noch nicht getestet, kann nicht ohne Weiteres mit Shell-Skripten umgehen)

## Installation

- Terminal öffnen und zu gewünschtem Installationspfad wechseln und folgendes eingeben:

     ```git clone "https://github.com/iradraconis/Posteingang.git"```

  Alternativ: Dateien herunterladen und entpacken, dann aber keine automatischen Updates möglich
- unter MacOS kann mit dem Scripteditor ein Applescript erstellt werden, dass als Anwendung unter Programme gespeichert wird und auch in das Dock gezogen werden kann. 

    - Öffne den "Script Editor" auf deinem Mac (befindet sich im Ordner "Programme" > "Dienstprogramme").

    - Erstelle ein neues Script mit folgendem Inhalt:

        ```tell application "Terminal"
            activate
            do script "sh ~/path/to/Posteingang.sh"
        end tell```

    - Ersetze ~/path/to/Posteingang.sh mit dem tatsächlichen Pfad zu deinem Script.

    - Speichere das Script:
    
        Wähle im Menü "Ablage" die Option "Sichern".
        Im Dialogfeld, das erscheint, wähle "Anwendung" im Dropdown-Menü bei "Dateiformat".
        Gib dem File einen Namen und speichere es an einem geeigneten Ort, z.B. unter Programme.

# E-Mail zu PDF Konverter

Dieses Python-Programm ist ein Werkzeug, das E-Mail-Nachrichten und Bilder in einem ausgewählten Ordner zu PDF-Dateien konvertiert, diese dann zusammenführt und die resultierende PDF-Datei in einen Zielordner verschiebt. Zudem wird auch eine optische Zeichenerkennung (OCR) auf die generierte PDF durchgeführt.
Installation

Zum Starten des Programms (und auch zur erstmaligen Installation) Terminal öffnen, zu Installationspfad wechseln und folgenden Befehl eingeben:

```./Posteingang.sh```

Das Skript überprüft, ob ein Python installiert ist. Falls nein, wird Python.org geöffnet. Es wird auf Updates im Github repository geprüft.
Für den Fall, dass ein Update bereitsteht, wird das Update automatisch durchgeführt.

Unter MacOS kann das Skript bequem über einen Kurzbefehl gestartet werden. Dazu Kurzbefehl erstellen. Element "Shell-Skript ausführen" hinzufügen. dort eingeben "cd /Users/NameDesNutzers/SpeicherortDesScripts" in der nächsten Zeile "./Posteingang.sh"

## Benutzung

Dies öffnet ein Fenster, in dem Sie zwei Ordner auswählen müssen: einen Eingabeordner und einen Ausgabeordner. 
Der Eingabeordner sollte alle E-Mails und Bilder enthalten, die Sie in eine PDF umwandeln möchten, 
während der Ausgabeordner der Ort ist, an dem die resultierenden PDFs abgelegt werden.

Nachdem Sie die Ordner ausgewählt haben, klicken Sie auf die Schaltfläche "Run Script", um den Konvertierungsprozess zu starten. 
Das Programm durchläuft mehrere Schritte:

    Konvertieren von .eml-Dateien in PDFs.
    Anpassung der Größe von Bildern und Konvertieren dieser in PDFs.
    Zusammenführen aller PDFs zu einer einzigen Datei.
    Durchführung einer OCR auf der zusammengefügten PDF.
    Verschieben der finalen PDF in den Ausgabeordner.

Nach Abschluss des Prozesses werden alle temporären Dateien wieder entfernt.

## Fehlersuche
Falls während der Ausführung des Programms ein Fehler auftritt, werden entsprechende Meldungen in die Datei app.log geschrieben. 

## Lizenz
Dieses Programm ist unter der MIT-Lizenz lizenziert.

## Kontakt
Bei Fragen oder Anregungen, bitte Ticket erstellen. 

# E-Mail zu PDF Konverter

Dieses Python-Programm ist ein Werkzeug, das E-Mail-Nachrichten und Bilder in einem ausgewählten Ordner zu PDF-Dateien konvertiert, diese dann zusammenführt und die resultierende PDF-Datei in einen Zielordner verschiebt. Zudem wird auch eine optische Zeichenerkennung (OCR) auf die generierte PDF durchgeführt.
Installation

Das Programm erfordert die Installation einiger externer Bibliotheken und richtet eine virtuelle Python Umgebung ein. 

Python muss auf dem System installiert sein.

Zum Starten des Programms (und auch zur erstmaligen Installation folgenden Befehl:

./Posteingang.sh

Das Skript überprüft, ob ein Python installiert ist. Falls nein, wird Python.org geöffnet. Es wird auf Updates im Github repository geprüft.
Für den Fall, dass ein Update bereitsteht, wird das Update automatisch durchgeführt.

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

Fehlersuche
Falls während der Ausführung des Programms ein Fehler auftritt, werden entsprechende Meldungen in die Datei app.log geschrieben. 

Lizenz
Dieses Programm ist unter der MIT-Lizenz lizenziert.

Kontakt
Falls Sie Fragen oder Anregungen haben, kontaktieren Sie mich bitte unter me@myemail.com. 
Ich freue mich immer über Feedback und Verbesserungsvorschläge!

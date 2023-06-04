# E-Mail zu PDF Konverter

Dieses Python-Programm ist ein Werkzeug, das E-Mail-Nachrichten und Bilder in PDF-Dateien konvertiert, diese dann zusammenführt und die resultierende PDF-Datei in einen Zielordner verschiebt. Zudem wird auch eine optische Zeichenerkennung (OCR) auf die generierte PDF durchgeführt.
Installation

Das Programm erfordert die Installation einiger externer Bibliotheken, darunter:

    PyPDF2
    email
    PIL
    reportlab
    ocrmypdf
    pdfkit
    PySide6

Um diese Bibliotheken zu installieren, verwenden Sie folgenden Befehl:

bash

pip install PyPDF2 email PIL reportlab ocrmypdf pdfkit PySide6

## Benutzung

Um das Programm zu starten, führen Sie einfach die Python-Datei aus:

bash

python main.py

Dies öffnet ein Fenster, in dem Sie zwei Ordner auswählen müssen: einen Eingabeordner und einen Ausgabeordner. Der Eingabeordner sollte alle E-Mails und Bilder enthalten, die Sie in eine PDF umwandeln möchten, während der Ausgabeordner der Ort ist, an dem die resultierenden PDFs abgelegt werden.

Nachdem Sie die Ordner ausgewählt haben, klicken Sie auf die Schaltfläche "Run Script", um den Konvertierungsprozess zu starten. Das Programm durchläuft mehrere Schritte:

    Konvertieren von .eml-Dateien in PDFs.
    Anpassung der Größe von Bildern und Konvertieren dieser in PDFs.
    Zusammenführen aller PDFs zu einer einzigen Datei.
    Durchführung einer OCR auf der zusammengefügten PDF.
    Verschieben der finalen PDF in den Ausgabeordner.

Nach Abschluss des Prozesses werden alle temporären Dateien gelöscht.
Fehlersuche

Falls während der Ausführung des Programms ein Fehler auftritt, werden entsprechende Meldungen auf der Konsole ausgegeben. Lesen Sie diese sorgfältig durch, um das Problem zu verstehen und zu beheben. Achten Sie dabei besonders auf Fehlermeldungen im Zusammenhang mit Dateipfaden, fehlenden Dateien und Bibliotheken.
Lizenz

Dieses Programm ist unter der MIT-Lizenz lizenziert.
Kontakt

Falls Sie Fragen oder Anregungen haben, kontaktieren Sie mich bitte unter me@myemail.com. Ich freue mich immer über Feedback und Verbesserungsvorschläge!
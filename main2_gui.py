import json
import os
import shutil

from PyPDF2 import PdfMerger
import email
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
import ocrmypdf
from datetime import datetime
import pdfkit
from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QFileDialog, QWidget

# wkhtmltopdf muss installiert sein brew install wkhtmltopdf oder dnf install wkhtmltopdf


class PDF:
    def __init__(self):
        self.merger = PdfMerger()
        self.filepath = os.path.join(os.path.dirname(__file__), "folders.json")  # Füge den Pfad zur JSON-Datei hinzu

        if os.path.exists(self.filepath):  # Prüfen, ob die JSON-Datei existiert
            with open(self.filepath, "r") as json_file:
                data = json.load(json_file)
                self.input_folder = data.get("input_folder")
                self.temp_folder = data.get("temp_folder")
                self.scan_eingang_pfad = data.get("scan_eingang_pfad")
        else:
            self.input_folder = None
            self.temp_folder = None
            self.scan_eingang_pfad = None


    def folder_contains_files(self, folder_path):
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                return True
        return False

    def convert_eml_to_pdf(self):
        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)

            if file_path.endswith(".eml"):
                print(file_name)

                if not os.path.isfile(file_path):
                    print(f"Die Datei {file_name} konnte nicht gefunden werden im Pfad {file_path}.")
                    return

                with open(file_path, 'r', encoding='utf-8') as f:
                    msg = email.message_from_file(f)

                sender = msg['From']
                sender_email = msg['From'].split('<')[1][:-1]

                html = ""
                plain_text = ""
                for part in msg.walk():
                    charset = part.get_content_charset()
                    if part.get_content_type() == "text/html":
                        html += part.get_payload(decode=True).decode(charset if charset else 'utf-8', errors='replace')
                    elif part.get_content_type() == "text/plain":
                        plain_text += part.get_payload(decode=True).decode(charset if charset else 'utf-8',
                                                                           errors='replace')

                if html:
                    content = html.replace('\n', '<br>')
                elif plain_text:
                    content = f"<pre>{plain_text}</pre>"
                else:
                    print(f"Die EML-Datei {file_name} enthält keinen erkennbaren Inhalt.")
                    return

                content = f"<meta charset='UTF-8'><p>Absender: {sender}<br>Email: {sender_email}</p>" + content

                pdf_filename = os.path.splitext(file_name)[0] + "-eml.pdf"
                pdf_path = os.path.join(self.input_folder, pdf_filename)

                try:
                    pdfkit.from_string(content, pdf_path)
                    print(
                        f"Die E-Mail wurde erfolgreich in {pdf_filename} konvertiert und gespeichert im Pfad {file_path}.")
                except Exception as e:
                    print(f"Fehler beim Konvertieren der E-Mail in PDF: {str(e)}")

    def resize_image(self, image_path, max_size):
        with PILImage.open(image_path) as img:
            if max(img.size) > max_size:
                scaling_factor = max_size / float(max(img.size))
                new_size = tuple([int(x * scaling_factor) for x in img.size])
                img = img.resize(new_size, PILImage.LANCZOS)
                img.save(image_path)


    def create_ocr_pdf(self, input_pdf, output_pdf):
        try:
            ocrmypdf.ocr(input_pdf, output_pdf, deskew=True, skip_text=True, language='deu')
        except ZeroDivisionError:
            print("Die Datei konnte nicht konvertiert werden.")
            return

    def merge_pdf(self):
        self.temp_folder = self.input_folder + "/temp_folder/"

        # Erstellt den temp_folder, wenn er nicht existiert.
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        image_pdfs = []
        eml_pdfs = []

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)

            if file_name.endswith(".pdf"):
                if file_name.endswith("-eml.pdf"):  # Wir nehmen an, dass EML-PDFs die Endung ".eml.pdf" haben
                    eml_pdfs.append(file_path)
                else:
                    image_pdfs.append(file_path)

            elif file_name.lower().endswith(('.jpg', '.jpeg', '.png', 'heic')):
                self.resize_image(file_path, 2160)  # Ändert die Größe des Bildes, wenn es größer als 1080px ist.

                img = PILImage.open(file_path)
                img = img.convert('RGB')

                pdf_path = os.path.join(self.temp_folder, f"{file_name[:-4]}.pdf")

                canv = canvas.Canvas(pdf_path, pagesize=img.size)
                canv.drawImage(file_path, 0, 0, *img.size)
                canv.showPage()
                canv.save()

                image_pdfs.append(pdf_path)

        # Zuerst die EML-PDFs einfügen
        for pdf_path in eml_pdfs:
            self.merger.append(pdf_path)

        # Dann die anderen PDFs einfügen
        for pdf_path in image_pdfs:
            self.merger.append(pdf_path)

        with open(os.path.join(self.temp_folder, "Email_Posteingang.pdf"), "wb") as f:
            self.merger.write(f)

    def move_pdf_to_scan_folder(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_Email_Posteingang_OCR.pdf"
        new_filepath = os.path.join(self.scan_eingang_pfad, filename)
        for pdf_file in ["Email_Posteingang_OCR.pdf", "Email_Posteingang.pdf"]:
            if pdf_file in os.listdir(self.temp_folder):
                pdf_file_path = os.path.join(self.temp_folder, pdf_file)
                shutil.move(pdf_file_path, new_filepath)  # Verwenden von shutil.move anstelle von os.rename

        for file_name in os.listdir(self.temp_folder):
            if file_name != "Email_Posteingang.pdf":
                file_path = os.path.join(self.temp_folder, file_name)
                os.remove(file_path)

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        if os.path.exists(self.temp_folder):
            try:
                # Entfernen Sie das Verzeichnis und alle darin enthaltenen Dateien und Unterverzeichnisse.
                shutil.rmtree(self.temp_folder)
                print(f"Ordner {self.temp_folder} erfolgreich entfernt.")
            except Exception as e:
                print(f"Fehler beim Entfernen des Ordners {self.temp_folder: {str(e)}}")
        else:
            print(f"Der Ordner {self.temp_folder} existiert nicht.")


class App(QWidget):
    def __init__(self, pdf_class):
        super().__init__()

        self.title = 'Email => Posteingang'
        self.pdf = pdf_class
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(250, 230)  # Parameter sind Breite und Höhe in Pixeln

        layout = QVBoxLayout()

        self.label_input = QLabel(self)
        self.label_input.setText(f"Input Folder: {self.pdf.input_folder}" if self.pdf.input_folder else "Input Folder: None")
        layout.addWidget(self.label_input)

        self.btn_input = QPushButton('Choose Input Folder', self)
        self.btn_input.clicked.connect(self.choose_input_folder)
        layout.addWidget(self.btn_input)

        self.label_output = QLabel(self)
        self.label_output.setText(f"Output Folder: {self.pdf.scan_eingang_pfad}" if self.pdf.scan_eingang_pfad else "Output Folder: None")
        layout.addWidget(self.label_output)

        self.btn_output = QPushButton('Choose Output Folder', self)
        self.btn_output.clicked.connect(self.choose_output_folder)
        layout.addWidget(self.btn_output)

        self.btn_run = QPushButton('Run Script', self)
        self.btn_run.clicked.connect(self.run_script)
        layout.addWidget(self.btn_run)

        self.setLayout(layout)

    def choose_input_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        self.pdf.input_folder = folder_path
        self.label_input.setText(f"Input Folder: {folder_path}")
        self.save_to_json("input_folder", folder_path)

    def choose_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        self.pdf.scan_eingang_pfad = folder_path
        self.label_output.setText(f"Output Folder: {folder_path}")
        self.save_to_json("scan_eingang_pfad", folder_path)

    def save_to_json(self, key, value):
        data = {}
        if os.path.exists(self.pdf.filepath):
            with open(self.pdf.filepath, "r") as json_file:
                data = json.load(json_file)
        data[key] = value
        with open(self.pdf.filepath, "w") as json_file:
            json.dump(data, json_file)

    def run_script(self):
        if self.pdf.folder_contains_files(self.pdf.input_folder):
            try:
                self.pdf.convert_eml_to_pdf()
            except Exception as e:
                print(e)
                print("Die EML-Dateien konnten nicht konvertiert werden.")
            try:
                self.pdf.merge_pdf()
            except Exception as e:
                print(e)
                print(" Die PDF-Dateien konnten nicht zusammengefügt werden.")
            try:
                self.pdf.create_ocr_pdf(os.path.join(self.pdf.temp_folder, "Email_Posteingang.pdf"),
                                        os.path.join(self.pdf.temp_folder, "Email_Posteingang_OCR.pdf"))
            except Exception as e:
                print(e)
                print("Die PDF-Datei konnte nicht konvertiert werden.")
            try:
                self.pdf.move_pdf_to_scan_folder()
            except Exception as e:
                print(e)
                print("Die PDF-Datei konnte nicht in den Scan-Ordner verschoben werden.")
            print("Alles erledigt!")
        else:
            print("Der Input-Ordner ist leer.")


if __name__ == '__main__':
    app = QApplication([])
    pdf = PDF()
    ex = App(pdf)
    ex.show()
    app.exec()

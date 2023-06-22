import os

from pdfkit import pdfkit
from wand.image import Image
from wand.exceptions import WandException
from PyPDF2 import PdfMerger
import email
from weasyprint import HTML
from PIL import Image as PILImage
import ocrmypdf
from datetime import datetime


# TODO: HEIC Bilddateien in PDF konvertieren
# TODO: Systemmessage wenn keine Dateien im Ordner sind
# TODO: Systemmessage, wenn nicht alle Dateien konvertiert werden konnten

class PDF:
    def __init__(self):
        self.merger = PdfMerger()
        self.input_folder = "/Users/max/Downloads/Anhang"
        self.output_folder = "/Users/max/Downloads/Anhang/output_folder"
        self.scan_eingang_pfad = "/Users/max/Scans/Email_Posteingang.pdf"


        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

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

    def create_ocr_pdf(self, input_pdf, output_pdf):
        try:
            ocrmypdf.ocr(input_pdf, output_pdf, deskew=True, skip_text=True, language='deu')
        except ZeroDivisionError:
            print("Die Datei konnte nicht konvertiert werden.")
            return

    def merge_pdf(self):
        image_pdfs = []

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)

            if file_name.endswith(".pdf"):
                self.merger.append(open(file_path, 'rb'))

            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png") or file_name.endswith(".JPG") or file_name.endswith(".JPEG") or file_name.endswith(".PNG"):
                if os.path.splitext(file_path)[1].lower() in ('.jpg', '.jpeg', '.png'):
                    # Check file size
                    if os.path.getsize(file_path) > 1000000:  # 1 MB
                        with PILImage.open(file_path) as img:
                            # Resize image
                            basewidth = 800
                            wpercent = (basewidth / float(img.size[0]))
                            hsize = int((float(img.size[1]) * float(wpercent)))
                            img = img.resize((basewidth, hsize), PILImage.LANCZOS)
                            # Save as PDF
                            pdf_path = os.path.join(self.output_folder, f"{file_name[:-4]}.pdf")
                            img.save(pdf_path, "PDF", resolution=100.0)
                            image_pdfs.append(open(pdf_path, 'rb'))
                    else:
                        # File size is less than or equal to 1 MB, so add the original image to PDF
                        try:
                            with Image(filename=file_path) as img:
                                img.alpha_channel = False
                                img.format = 'pdf'
                                pdf_path = os.path.join(self.output_folder, f"{file_name[:-4]}.pdf")
                                img.save(filename=pdf_path)

                                image_pdfs.append(open(pdf_path, 'rb'))

                                img.alpha_channel = False
                                img.format = 'png'
                                img.save(filename=f"{self.output_folder}/{file_name[:-4]}.png")

                        except WandException:
                            print(f"Die Datei {file_name} konnte nicht gelesen werden.")


        # Append image PDFs to merger
        for image_pdf in image_pdfs:
            self.merger.append(image_pdf)

        with open(os.path.join(self.output_folder, "Email_Posteingang.pdf"), "wb") as f:
            self.merger.write(f)


    def move_pdf_to_scan_folder(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_{os.path.basename('Email_Posteingang.pdf')}"
        new_filepath = os.path.join(os.path.dirname(self.scan_eingang_pfad), filename)
        for pdf_file in ["Email_Posteingang_OCR.pdf", "Email_Posteingang.pdf"]:
            if pdf_file in os.listdir(self.output_folder):
                pdf_file_path = os.path.join(self.output_folder, pdf_file)
                os.rename(pdf_file_path, new_filepath)
        for file_name in os.listdir(self.output_folder):
            if file_name != "Email_Posteingang.pdf":
                file_path = os.path.join(self.output_folder, file_name)
                os.remove(file_path)


        for file_name in os.listdir(self.input_folder): # Löscht alle Dateien im Input-Ordner
            file_path = os.path.join(self.input_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)


if __name__ == '__main__':
    pdf = PDF() # Erstellt eine Instanz der Klasse PDF
    if pdf.folder_contains_files(pdf.input_folder):
        try:
            pdf.convert_eml_to_pdf() # Konvertiert alle EML-Dateien im Input-Ordner in PDF-Dateien
        except:
            print("Die EML-Dateien konnten nicht konvertiert werden.")
        try:
            pdf.merge_pdf() # Erstellt "Email_Posteingang.pdf" im Output-Ordner
        except:
            print("Die PDF-Dateien konnten nicht zusammengefügt werden.")
        try:
            pdf.create_ocr_pdf("/Users/max/Downloads/Anhang/output_folder/Email_Posteingang.pdf","/Users/max/Downloads/Anhang/output_folder/Email_Posteingang_OCR.pdf")
        except:
            print("Die PDF-Datei konnte nicht konvertiert werden.")
        try:
            pdf.move_pdf_to_scan_folder() # Verschiebt "Email_Posteingang_OCR.pdf" in den Scan-Ordner und löscht alle anderen Dateien im Output-Ordner
        except:
            print("Die PDF-Datei konnte nicht in den Scan-Ordner verschoben werden.")
        print("Alles erledigt!")
    else:
        print("Der Input-Ordner ist leer.")

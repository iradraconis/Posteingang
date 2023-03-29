import os
from wand.image import Image
from wand.exceptions import WandException
from PyPDF2 import PdfMerger
import email
from weasyprint import HTML
from PIL import Image as PILImage
import ocrmypdf
from datetime import datetime

class PDF:
    def __init__(self):
        self.merger = PdfMerger()
        self.input_folder = "/home/max/Downloads/Anhang"
        self.output_folder = "/home/max/Downloads/Anhang/output_folder"
        self.scan_eingang_pfad = "/home/max/Scans/Email_Posteingang.pdf"


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

                # Überprüfen, ob die EML-Datei vorhanden ist
                if not os.path.isfile(file_path):
                    print(f"Die Datei {file_name} konnte nicht gefunden werden im Pfad {file_path}.")
                    return

                # Verarbeite die EML-Datei
                with open(file_path, 'r', encoding='utf-8') as f:
                    msg = email.message_from_file(f)

                # Extrahiere den Absender der E-Mail
                sender = msg['From']
                sender_email = msg['From'].split('<')[1][:-1]

                # Extrahiere den HTML-Inhalt der E-Mail
                html = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        html += part.get_payload(decode=True).decode(charset)

                # Füge den Absender und dessen Email-Adresse am Anfang des HTML-Inhalts hinzu
                html = f"<p>Absender: {sender}<br>Email: {sender_email}</p>" + html

                # Erstelle eine neue PDF-Datei
                pdf_filename = os.path.splitext(file_name)[0] + ".pdf"
                pdf_path = os.path.join(self.input_folder, pdf_filename)

                # Konvertiere HTML zu PDF
                HTML(string=html.replace('\n', '<br>')).write_pdf(pdf_path)

                print(
                    f"Die E-Mail wurde erfolgreich in {pdf_filename} konvertiert und gespeichert im Pfad {file_path}.")

    def create_ocr_pdf(self, input_pdf, output_pdf):
        ocrmypdf.ocr(input_pdf, output_pdf, deskew=True, skip_text=True, language='deu')


    def merge_pdf(self):
        image_pdfs = []

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)

            if file_name.endswith(".pdf"):
                self.merger.append(open(file_path, 'rb'))

            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
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


        # Löschen aller Dateien im Output-Ordner außer "Email_Posteingang.pdf"
        for file_name in os.listdir(self.output_folder):
            if file_name != "Email_Posteingang.pdf":
                file_path = os.path.join(self.output_folder, file_name)
                os.remove(file_path)

    def move_pdf_to_scan_folder(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_{os.path.basename(self.scan_eingang_pfad)}"
        new_filepath = os.path.join(os.path.dirname(self.scan_eingang_pfad), filename)
        os.rename(os.path.join(self.output_folder, "Email_Posteingang_OCR.pdf"), new_filepath)
        for file_name in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, file_name)
            os.remove(file_path)
        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)


if __name__ == '__main__':
    pdf = PDF() # Erstellt eine Instanz der Klasse PDF
    if pdf.folder_contains_files(pdf.input_folder):
        pdf.convert_eml_to_pdf() # Konvertiert alle EML-Dateien im Input-Ordner in PDF-Dateien
        pdf.merge_pdf() # Erstellt "Email_Posteingang.pdf" im Output-Ordner
        pdf.create_ocr_pdf("/home/max/Downloads/Anhang/output_folder/Email_Posteingang.pdf","/home/max/Downloads/Anhang/output_folder/Email_Posteingang_OCR.pdf")
        pdf.move_pdf_to_scan_folder() # Verschiebt "Email_Posteingang_OCR.pdf" in den Scan-Ordner und löscht alle anderen Dateien im Output-Ordner
        print("Alles erledigt!")
    else:
        print("Der Input-Ordner ist leer.")

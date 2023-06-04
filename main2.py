import os
from PyPDF2 import PdfMerger, PdfFileWriter, PdfFileReader
import email
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
import ocrmypdf
from datetime import datetime
import pdfkit

# brew install Caskroom/cask/wkhtmltopdf
# brew install tesseract-lang

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
                    if part.get_content_type() == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        html += part.get_payload(decode=True).decode(charset)
                    elif part.get_content_type() == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        plain_text += part.get_payload(decode=True).decode(charset)

                if html:
                    content = html.replace('\n', '<br>')
                elif plain_text:
                    content = f"<pre>{plain_text}</pre>"
                else:
                    print(f"Die EML-Datei {file_name} enthält keinen erkennbaren Inhalt.")
                    return

                content = f"<p>Absender: {sender}<br>Email: {sender_email}</p>" + content

                pdf_filename = os.path.splitext(file_name)[0] + ".pdf"
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
                img = img.resize(new_size, PILImage.ANTIALIAS)
                img.save(image_path)


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
                self.merger.append(file_path)

            elif file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.resize_image(file_path, 2160)  # Ändert die Größe des Bildes, wenn es größer als 1080px ist.

                img = PILImage.open(file_path)
                img = img.convert('RGB')

                pdf_path = os.path.join(self.output_folder, f"{file_name[:-4]}.pdf")

                canv = canvas.Canvas(pdf_path, pagesize=img.size)
                canv.drawImage(file_path, 0, 0, *img.size)
                canv.showPage()
                canv.save()

                image_pdfs.append(pdf_path)

        for pdf_path in image_pdfs:
            self.merger.append(pdf_path)

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

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    pdf = PDF()
    if pdf.folder_contains_files(pdf.input_folder):
        try:
            pdf.convert_eml_to_pdf()
        except:
            print("Die EML-Dateien konnten nicht konvertiert werden.")
        try:
            pdf.merge_pdf()
        except Exception as e:
            print(e)
            print(" Die PDF-Dateien konnten nicht zusammengefügt werden.")
        try:
            pdf.create_ocr_pdf("/Users/max/Downloads/Anhang/output_folder/Email_Posteingang.pdf",
                               "/Users/max/Downloads/Anhang/output_folder/Email_Posteingang_OCR.pdf")
        except Exception as e:
            print(e)
            print("Die PDF-Datei konnte nicht konvertiert werden.")
        # try:
        #     pdf.move_pdf_to_scan_folder()
        # except:
        #     print("Die PDF-Datei konnte nicht in den Scan-Ordner verschoben werden.")
        print("Alles erledigt!")
    else:
        print("Der Input-Ordner ist leer.")


# folder_path = "/home/max/Downloads/Anhang"
# , lang='deu'

# TODO: OCR noch fehlerhaft
# TODO: Images sollten ab einer bestimmten Dateigröße verkleinert werden


import os
import PyPDF2
from wand.image import Image
from wand.exceptions import WandException
import pytesseract
from PyPDF2 import PdfMerger, PdfWriter
import email
from email import policy
from email.parser import BytesParser
from weasyprint import HTML


class PDF:
    def __init__(self):
        self.merger = PdfMerger()
        self.input_folder = "/home/max/Downloads/Anhang"
        self.output_folder = "/home/max/Downloads/Anhang/output_folder"
        self.scan_eingang_pfad = "/home/max/Scans/Email_Posteingang.pdf"


        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

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

                # Extrahiere den HTML-Inhalt der E-Mail
                html = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        html += part.get_payload(decode=True).decode(charset)

                # Erstelle eine neue PDF-Datei
                pdf_filename = os.path.splitext(file_name)[0] + ".pdf"
                pdf_path = os.path.join(self.input_folder, pdf_filename)

                # Konvertiere HTML zu PDF
                HTML(string=html.replace('\n', '<br>')).write_pdf(pdf_path)

                print(
                    f"Die E-Mail wurde erfolgreich in {pdf_filename} konvertiert und gespeichert im Pfad {file_path}.")

            # entfernen des else-Blocks

    def create_ocr_pdf(self, pdf_file_path):
        # Öffne die PDF-Datei
        pdf_file = open(pdf_file_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extrahiere den Text aus der PDF-Datei
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            try:
                page = pdf_reader.pages[page_num]
                text += pytesseract.image_to_string(page)
            except TypeError:
                print(f"Die Seite {page_num} konnte nicht gelesen werden.")

        # Erstelle eine neue PDF-Datei mit dem extrahierten Text
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(PyPDF2.PageObject.create_blank_page(None, 72, 72))
        pdf_writer.add_metadata({
            '/Title': 'OCR Output',
            '/Creator': 'pytesseract',
        })
        pdf_writer.add_outline_item('OCR Output', 0)
        # pdf_writer.addPageLabel(0, PyPDF2.pdf.PageLabel(number=1))
        pdf_writer.add_page(PyPDF2.PageObject.createTextObject(text))

        # Speichere die neue PDF-Datei unter dem Namen "output-ocr.pdf"
        output_file_path = 'output-ocr.pdf'
        with open(output_file_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        # Schließe die PDF-Datei
        pdf_file.close()

        return output_file_path

    def merge_pdf(self):
        image_pdfs = []

        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)



            if file_name.endswith(".pdf"):
                self.merger.append(open(file_path, 'rb'))

            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
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

        # Wende OCR auf die Output.pdf an => Gibt noch Fehlermeldungen
        # self.create_ocr_pdf("/home/max/Downloads/Anhang/output_folder/Output.pdf")

        # Löschen aller Dateien im Output-Ordner außer output.pdf
        for file_name in os.listdir(self.output_folder):
            if file_name != "Email_Posteingang.pdf":
                file_path = os.path.join(self.output_folder, file_name)
                os.remove(file_path)

        # move "Email_Posteingang.pdf to scan_eingang_pfad
        #os.rename(os.path.join(self.output_folder, "Email_Posteingang.pdf"), self.scan_eingang_pfad)


        print("Alles erledigt.")


if __name__ == '__main__':
    pdf = PDF()
    pdf.convert_eml_to_pdf()
    pdf.merge_pdf()
    #pdf.create_ocr_pdf("/home/max/Downloads/Anhang/output_folder/Email_Posteingang.pdf")

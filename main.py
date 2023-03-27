# folder_path = "/home/max/Downloads/Anhang"
# , lang='deu'

# TODO: OCR noch fehlerhaft
# TODO: Convert email to pdf noch fehlerhaft


import os
import PyPDF2
from wand.image import Image
from wand.exceptions import WandException
import pytesseract
from PyPDF2 import PdfMerger, PdfWriter
from email import message_from_file


class PDF:
    def __init__(self):
        self.merger = PdfMerger()
        self.output_folder = "/home/max/Downloads/Anhang/output_folder"
        self.input_folder = "/home/max/Downloads/Anhang"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    # create function to convert eml to pdf file
    def convert_eml_to_pdf(self, eml_filename):
        pdf_filename = "email_text.pdf"

        # Öffne die EML-Datei und lese die Nachricht ein
        with open(eml_filename, 'r') as eml_file:
            message = message_from_file(eml_file)

        # Extrahiere den Text aus der Nachricht
        text = message.get_payload()

        # Erstelle ein neues PDF-Dokument
        output_pdf = PdfWriter()

        # Erstelle eine neue Seite im PDF-Dokument
        output_pdf.addPage()

        # Schreibe den Text in das PDF-Dokument
        output_pdf.getPage(0).addText(text)

        # Speichere das PDF-Dokument
        with open(pdf_filename, 'wb') as pdf_file:
            output_pdf.write(pdf_file)

        print(f"Die EML-Datei wurde erfolgreich in {eml_filename} konvertiert.")

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
        pdf_writer.addPage(PyPDF2.pdf.PageObject.createBlankPage(None, 72, 72))
        pdf_writer.addMetadata({
            '/Title': 'OCR Output',
            '/Creator': 'pytesseract',
        })
        pdf_writer.addBookmark('OCR Output', 0)
        # pdf_writer.addPageLabel(0, PyPDF2.pdf.PageLabel(number=1))
        pdf_writer.addPage(PyPDF2.pdf.PageObject.createTextObject(text))

        # Speichere die neue PDF-Datei unter dem Namen "output-ocr.pdf"
        output_file_path = 'output-ocr.pdf'
        with open(output_file_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        # Schließe die PDF-Datei
        pdf_file.close()

        return output_file_path

    def merge_pdf(self):
        for file_name in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, file_name)

            if file_name.endswith(".eml"):
                print(file_name)
                # self.convert_eml_to_pdf(file_path)


            elif file_name.endswith(".pdf"):
                self.merger.append(open(file_path, 'rb'))

            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
                try:
                    with Image(filename=file_path) as img:
                        img.alpha_channel = False
                        img.format = 'pdf'
                        pdf_path = os.path.join(self.output_folder, f"{file_name[:-4]}.pdf")
                        img.save(filename=pdf_path)
                        self.merger.append(open(pdf_path, 'rb'))

                        img.alpha_channel = False
                        img.format = 'png'
                        img.save(filename=f"{self.output_folder}/{file_name[:-4]}.png")

                except WandException:
                    pass

        with open(os.path.join(self.output_folder, "Output.pdf"), "wb") as f:
            self.merger.write(f)

        # Wende OCR auf die Output.pdf an => Gibt noch Fehlermeldungen
        # self.create_ocr_pdf("/home/max/Downloads/Anhang/output_folder/Output.pdf")

        # Löschen aller Dateien im Output-Ordner außer output.pdf
        for file_name in os.listdir(self.output_folder):
            if file_name != "Output.pdf":
                file_path = os.path.join(self.output_folder, file_name)
                os.remove(file_path)

        print("Alles erledigt.")


if __name__ == '__main__':
    pdf = PDF()
    pdf.merge_pdf()

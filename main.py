import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
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
import logging


class PDF:
    def __init__(self):
        # Set up logging
        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.merger = PdfMerger()
        self.filepath = os.path.join(os.path.dirname(__file__), "folders.json")
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as json_file:
                    data = json.load(json_file)
                    self.input_folder = data.get("input_folder", None)
                    self.temp_folder = data.get("temp_folder", None)
                    self.scan_eingang_pfad = data.get("scan_eingang_pfad", None)
            except Exception as e:
                self.logger.error(f"Failed to load JSON data from {self.filepath}: {e}")
                raise
        else:
            self.logger.warning(f"{self.filepath} does not exist. Setting input_folder and temp_folder to None.")
            self.input_folder = None
            self.temp_folder = None
            self.scan_eingang_pfad = None

    def folder_contains_files(self, folder_path):
        try:
            for filename in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, filename)):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to check if folder {folder_path} contains files: {e}")
            raise

    def convert_eml_to_pdf(self):
        try:
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
                    split_sender = msg['From'].split('<')
                    if len(split_sender) > 1:
                        sender_email = split_sender[1][:-1]
                    else:
                        sender_email = split_sender[0]

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
        except Exception as e:
            self.logger.error(f"Failed to convert EML files to PDF in folder {self.input_folder}: {e}")
            raise

    def resize_image(self, image_path, max_size):
        try:
            with PILImage.open(image_path) as img:
                if max(img.size) > max_size:
                    scaling_factor = max_size / float(max(img.size))
                    new_size = tuple([int(x * scaling_factor) for x in img.size])
                    img = img.resize(new_size, PILImage.LANCZOS)
                    img.save(image_path)
        except Exception as e:
            self.logger.error(f"Failed to resize image {image_path}: {e}")
            raise

    def create_ocr_pdf(self, input_pdf, output_pdf):
        try:
            ocrmypdf.ocr(input_pdf, output_pdf, deskew=True, skip_text=True, language='deu')
        except ZeroDivisionError:
            print("Die Datei konnte nicht konvertiert werden.")
            return

    def merge_pdf(self):
        try:
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

            self.logger.info(f"Successfully merged PDFs in {self.input_folder} and saved the result in {self.temp_folder}")

        except Exception as e:
            self.logger.error(f"Failed to merge PDFs in folder {self.input_folder}: {e}")
            raise


    def move_pdf_to_scan_folder(self):
        try:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_Email_Posteingang_OCR.pdf"
            new_filepath = os.path.join(self.scan_eingang_pfad, filename)
            for pdf_file in ["Email_Posteingang_OCR.pdf", "Email_Posteingang.pdf"]:
                if pdf_file in os.listdir(self.temp_folder):
                    pdf_file_path = os.path.join(self.temp_folder, pdf_file)
                    shutil.move(pdf_file_path, new_filepath)  # Verwenden von shutil.move anstelle von os.rename
            self.logger.info(f"Moved PDF files from {self.temp_folder} to {new_filepath}")

            for file_name in os.listdir(self.temp_folder):
                if file_name != "Email_Posteingang.pdf":
                    file_path = os.path.join(self.temp_folder, file_name)
                    os.remove(file_path)
            self.logger.info(f"Removed non-PDF files from {self.temp_folder}")

            for file_name in os.listdir(self.input_folder):
                file_path = os.path.join(self.input_folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            self.logger.info(f"Removed files from {self.input_folder}")

            if os.path.exists(self.temp_folder):
                try:
                    # Entfernen Sie das Verzeichnis und alle darin enthaltenen Dateien und Unterverzeichnisse.
                    shutil.rmtree(self.temp_folder)
                    self.logger.info(f"Successfully removed folder {self.temp_folder}")
                except Exception as e:
                    self.logger.error(f"Error removing folder {self.temp_folder}: {e}")
                    raise
            else:
                self.logger.warning(f"The folder {self.temp_folder} does not exist.")
        except Exception as e:
            self.logger.error(f"Failed to move PDFs and clean up folders: {e}")
            raise


class App:
    def __init__(self, master, pdf_class):
        self.master = master
        master.title('Email => Posteingang')

        self.master.geometry("300x300")
        self.master.eval('tk::PlaceWindow . center')

        self.pdf = pdf_class

        self.label_input = ttk.Label(master, text="Input Folder: " + (self.pdf.input_folder if self.pdf.input_folder else "None"))
        self.label_input.pack(pady=(10, 10), padx=(10, 0))

        self.btn_input = ttk.Button(master, text='Choose Input Folder', command=self.choose_input_folder)
        self.btn_input.pack(pady=(10, 10), padx=(10, 0))

        self.label_output = ttk.Label(master, text="Output Folder: " + (self.pdf.scan_eingang_pfad if self.pdf.scan_eingang_pfad else "None"))
        self.label_output.pack(pady=(10, 10), padx=(10, 0))

        self.btn_output = ttk.Button(master, text='Choose Output Folder', command=self.choose_output_folder)
        self.btn_output.pack(pady=(10, 10), padx=(10, 0))

        self.btn_run = ttk.Button(master, text='Run Script', command=self.run_script)
        self.btn_run.pack(pady=(10, 20), padx=(10, 0))

    def choose_input_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.pdf.input_folder = folder_path
            self.label_input.config(text="Input Folder: " + folder_path)
            self.save_to_json("input_folder", folder_path)

    def choose_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.pdf.scan_eingang_pfad = folder_path
            self.label_output.config(text="Output Folder: " + folder_path)
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
            self.pdf.convert_eml_to_pdf()
            self.pdf.merge_pdf()
            self.pdf.create_ocr_pdf(os.path.join(self.pdf.temp_folder, "Email_Posteingang.pdf"),
                                    os.path.join(self.pdf.temp_folder, "Email_Posteingang_OCR.pdf"))
            self.pdf.move_pdf_to_scan_folder()
            messagebox.showinfo("Process Completed", "The PDF files have been successfully processed.")
        else:
            messagebox.showinfo("Error", "The input folder is empty.")

if __name__ == '__main__':
    root = ThemedTk(theme="adapta", background=True)
    pdf = PDF()
    app = App(root, pdf)
    root.mainloop()

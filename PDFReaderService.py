import requests
import os
import string
import random
from PyPDF2 import PdfReader


class PDFReaderService:
    def __init__(self):
        pass

    def get_text_from_pdf(self, file_uri):
        download_directory = self.__create_directory_for_files()
        downloaded_file_name = self.__download_file(file_uri, download_directory)
        return self.__extract_file_text(downloaded_file_name)


    def __create_directory_for_files(self):
        pdf_download_folder = f'./pdf_downloads'
        if not os.path.exists(pdf_download_folder):
            os.mkdir(pdf_download_folder)
        return pdf_download_folder

    def __delete_downloaded_file(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    def __download_file(self, file_uri, download_directory):
        local_filename = f'{download_directory}/{self.__randomly_generate_string()}.pdf'
        with requests.get(file_uri, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
        return local_filename

    def __randomly_generate_string(self):
        return ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k=8))

    def __extract_file_text(self, file_path):
        file_info = {'text': ''}
        reader = PdfReader(file_path)

        file_info['file_name'] = os.path.basename(file_path).split('/')[-1]
        file_info['page_len'] = len(reader.pages)

        for page in reader.pages:
            file_info['text'] += page.extract_text()
            file_info['text'] += '\n\n*PAGE BREAK*\n\n'

        return file_info

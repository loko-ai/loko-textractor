import os
import unittest
from datetime import datetime
from pprint import pprint
import requests

ASYNC = True

BASE_URL = "http://localhost:8080/ds4biz/textract/0.1/evaluate"

PATH = './test_resources/docswithannotations'

ANNOTATION_FOLDER = "annot_file.zip"
OCR_FILE_FOLDER = "ocr_file.zip"


class MyTest(unittest.TestCase):


    def get_files(self, ext: str):
        file = os.path.join(PATH, ext, OCR_FILE_FOLDER)
        annotated = os.path.join(PATH, ext, ANNOTATION_FOLDER)
        return file, annotated


    def request(self, file: str, annotated: str):
        start = datetime.now()
        f = open(file, 'rb')
        a = open(annotated, 'rb')
        resp = requests.post(BASE_URL, files = {'file': f, 'annotation': a})
        f.close()
        a.close()
        end = datetime.now()
        print(end - start, resp.status_code)
        self.assertEqual(resp.status_code, 200)
        pprint(resp.json())


    def test_doc_format(self):
        # print()
        # print()
        print('TEST DOC FORMAT')
        file, annotated = self.get_files(ext='doc')
        self.request(file, annotated)

    def test_pdf_format(self):
        pass

    def test_img_format(self):
        pass

    def test_txt_format(self):
        pass

    def test_docx_format(self):
        pass

    def test_eml_format(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=10)
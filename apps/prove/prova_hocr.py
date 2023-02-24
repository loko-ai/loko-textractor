import io
import logging
import os
import subprocess

import fitz
import pytesseract
from PIL import Image
from PyPDF2 import PdfFileMerger

logger = logging.getLogger()
OPTIONS = ""

fname = "/media/alejandro/DATA/Downloads/PDF_Prova/PDF_1/1_PDF.pdf"
fname = "/media/alejandro/DATA/workspace/livetech/ds4biz-textractor/ds4biz_textractor/test/test_resources/valeria2.jpg"

class HOCR:

    def __call__(self, iname):
        command = ["tesseract"] + [iname, iname]
        command = command + ["hocr"]
        subprocess.call(command)
        print(command)

        print(os.path.exists('/home/alejandro/Desktop/testocr.png.hocr'))
        with open(iname + ".hocr") as f:
            s = f.read()
        return s

class HOCR2:

    def __call__(self, iname):
        result = pytesseract.image_to_pdf_or_hocr(Image.open(iname))

        print(result)
        print(type(result))
        with open(iname+".hocr.pdf","wb") as f:
            f.write(result)

def pdf2spdf(fname):
    ret_pdf = PdfFileMerger()
    with open(fname, "rb") as f:
        doc = fitz.open("pdf", f.read())
    logger.debug(doc)
    for i, page in enumerate(doc):
        text = page.getText()
        logger.info(f"Pagina {i}")
        if not text:  # da passare a tesseract
            images = page.getImageList()

            pm = fitz.Pixmap(doc, images[0][0])  # prende la prima immagine
            logger.info(f"{images} {len(pm.samples)}")
            size = [pm.width, pm.height]
            img = Image.frombytes("L", size, pm.samples)
            img = img.rotate(360 - page.rotation, expand=True)
            result = pytesseract.image_to_pdf_or_hocr(img)
            ret_pdf.append(io.BytesIO(result))

    with open(fname+".hocr.pdf", "wb") as f:
        ret_pdf.write(f)






if __name__ == '__main__':
    fname = "/home/alejandro/Desktop/testocr.png"
    fname = "/media/alejandro/DATA/workspace/livetech/ds4biz-textractor/ds4biz_textractor/test/test_resources/DOC090519-09052019083949.pdf"

    print(pdf2spdf(fname))




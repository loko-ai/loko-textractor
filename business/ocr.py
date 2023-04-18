import io
import os
from io import BytesIO

import PIL
import cv2
import numpy as np
import pytesseract
from PIL import Image
from langdetect import detect_langs

from config.app_config import VOCABULARY_PATH, PATTERNS_PATH
from dao.bb_dao import RDao
from loguru import logger

LANG_MAPPING = dict(it='ita', en='eng')

class TESSERACT:
    def __init__(self,
                 preprocessing_configs: dict = None,
                 analyzer_configs: dict = None,
                 postprocessing_configs: dict = None,
                 hocr: dict = None,
                 output: str = None):

        preprocessing_configs = preprocessing_configs or {}
        analyzer_configs = analyzer_configs or {}
        postprocessing_configs = postprocessing_configs or {}
        self.hocr = hocr or False
        self.output = output
        if hocr:
            analyzer_configs["hocr"] = hocr
            analyzer_configs["output"] = output
        self.preprocessing = Preprocessing(**preprocessing_configs)
        self.analyzer = Analyzer(**analyzer_configs)
        self.postprocessing = Postprocessing(**postprocessing_configs)

    def __call__(self, img: PIL.Image.Image):
        try:
            img = self.preprocessing(img)
            text = self.analyzer(img)
            text = self.postprocessing(text)
            return text
        except Exception as inst:
            logger.exception(inst)


# detect language in preprocessing o analyzer?
class Preprocessing:

    def __init__(self,
                 resize_zoom: float = None,  interpolation_mode: int = 0, resize_dim: tuple = None, dpi: int = None):
        self.resize_zoom = resize_zoom
        self.resize_dim = resize_dim
        self.interpolation_mode = interpolation_mode
        self.dpi = dpi
        # print(self.__dict__)
        # todo: aggiungere qualita' immagini
        # - possibilita' di capovolgere immagini automaticamente o no
        # -

    def __call__(self, img: PIL.Image.Image):
        try:
            img = img.convert('RGB')
            if self.dpi:
                img = self.change_dpi(img)
            img = np.array(img)
            # print("ok")
            # print(self.dpi)

            if self.resize_zoom or self.resize_dim:
                img = self.resize_img(img)

            return img
        except Exception as inst:
            logger.exception(inst)

    def resize_img(self, img):
        logger.debug(
            "resizing the image... new dim: %s, zoom level: %s, interpolation mode: %s" % (str(self.resize_dim), str(self.resize_zoom), str(self.interpolation_mode)))
        return cv2.resize(img, dsize=self.resize_dim, fx=self.resize_zoom, fy=self.resize_zoom,
                          interpolation=self.interpolation_mode)

    def change_dpi(self, img: PIL.Image.Image):
        logger.debug("updating dpi value to %s..." % str(self.dpi))
        b = BytesIO()
        img.save(b, format="png",  dpi=(self.dpi, self.dpi))
        b.seek(0)
        img = PIL.Image.open(b)
        # with open("prova.png", "wb") as f:
        #     print("quii")
        #     # b.seek(0)
        #     f.write(b.read())
        return img
    # def zoom_img(self, img):
    #     # mat = fitz.Matrix(self, zoom)
    #     # doc = fitz.open("pdf", content)
    #     # img = page.getPixmap()
    #     return p

    # def img_rotation(self, img):
    #     osd = pytesseract.image_to_osd(img, lang = self.lang, output_type = Output.DICT)
    #     print(osd)
    #     angle = osd["rotate"]
    #     print("angle: ", angle)
    #     rotated_img = imutils.rotate_bound(img, angle)
    #     return rotated_img



class Analyzer:

    def __init__(self,
                 lang: str = 'ita',
                 vocab_file: str = None,
                 patterns_file: str = None,
                 whitelist: str = None,
                 blacklist: str = None,
                 psm: int = 1,
                 oem: int = 1,
                 hocr: bool = False,
                 output: {"html", "pdf", "json"} = None):
        self.hocr = hocr
        self.output = output

        oem = oem if oem is not None else 1
        psm = psm if psm is not None else 1

        self.lang = lang
        self.detect_lang = not lang

        if vocab_file: vocab_file = os.path.join(VOCABULARY_PATH, vocab_file)
        if patterns_file: patterns_file = os.path.join(PATTERNS_PATH, patterns_file)
        self.config = "--psm " + str(psm) + " --oem " + str(oem)
        if whitelist: self.config = '-c tessedit_char_whitelist=' + whitelist + ' '
        if blacklist: self.config = '-c tessedit_char_blacklist=' + blacklist + ' '
        if vocab_file: self.config += " --user-words " + vocab_file
        if patterns_file: self.config += " --user-patterns " + patterns_file
        logger.debug('ANALYZER CONFIGS: ' + str(self.__dict__))

    def __call__(self, img: PIL.Image.Image, resize: int = 1):
        try:
            if not self.hocr:
                logger.debug("start analyzer works...")
                text = pytesseract.image_to_string(img, config=self.config, lang=self.lang)
                if self.detect_lang:
                    text = self.detect_language(text, img) or text
                return text
            else:
                logger.debug("start analyzer works for an ocr...")
                if self.output == "application/json":
                    logger.debug("image to HOCR json format")
                    text_rif = pytesseract.image_to_data(img, config=self.config, lang=self.lang)
                    text = [x.split("\t") for x in text_rif.split("\n")]  # todo aggiungere configs
                    res = [el.__dict__ for el in RDao(text).all()]
                    return res
                elif self.output == "application/pdf":
                    logger.debug("image to HOCR pdf format")
                    result = pytesseract.image_to_pdf_or_hocr(img, config=self.config, lang=self.lang)
                    return io.BytesIO(result)
                elif self.output == "text/html":
                    logger.debug("image to HOCR html format")
                    return pytesseract.image_to_pdf_or_hocr(img, config=self.config, lang=self.lang, extension='hocr').decode()

        except Exception as inst:
            logger.exception(inst)


    # def preprocessing(self, img: PIL.Image.Image, resize: int):
    #     img = img.convert('RGB')
    #     img = np.array(img)
    #     img = cv2.resize(img, None, fx=resize, fy=resize)
    #     return img

    def detect_language(self, text, img):
        dlang = detect_langs(text)[0].lang
        logger.debug("detected language:  {lang}".format(lang=dlang))
        dlang = LANG_MAPPING.get(dlang, dlang)

        if dlang != self.lang:
            try:
                return pytesseract.image_to_string(img, config=self.config, lang=dlang)
            except:
                logger.warning('Language detected "{lang}". This language is not available'.format(lang=dlang))


class Postprocessing:
    def __init__(self, **kwargs):
        pass

    def __call__(self, text: str):
        # todo:
        #  1 - metodo che controlli che parole evidenti e conosciute non abbiano numeri in mezzo ed eventualmente modificare con la lettera piu' simile
        #  2 - introdurre correttore ortografico (avwwocato -> avvocato) es: speller
        #  3 -
        return text


if __name__ == '__main__':
    img_path = '../test/test_resources/valeria2.jpeg'
    img_path = '../test/test_resources/GNN.jpg'
    f = open(img_path, 'rb')
    img = Image.open(f)
    analyzer_configs = dict(lang='eng',
                            vocab_file='/home/cecilia/Documenti/images/vocab.txt',
                            patterns_file='/home/cecilia/Documenti/images/patterns.txt')
    tesseract = TESSERACT(analyzer_configs=analyzer_configs)
    print(tesseract(img))
    f.close()

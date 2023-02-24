import pandas as pd
import textract

from config.app_config import SUPPORTED_EXT
from utils.resources_utils import get_resource

LANGUAGE = "it" #langdetect
ENCODING = "utf8" #chardet


class MRFormatReader():
    '''MachineReadableFormatReader'''

    def read(self, fname):
        try:
            return textract.process(fname, language=LANGUAGE, encoding=ENCODING).decode(ENCODING)
        except:
            return "\f"


class MRFRxls(MRFormatReader):

    def read(self, file):
        df = pd.read_excel(file)
        txt = df.to_string()
        return txt


class MAFRFactory():

    def __init__(self, mapping={"generic": MRFormatReader(), "xls": MRFRxls()}):
        self.mapping = mapping

    def create(self, ext: str):
        if ext in SUPPORTED_EXT:
            ext = "generic"
        try:
            return self.mapping[ext]
        except Exception as inst:
            raise inst


if __name__ == '__main__':
    fname = get_resource("aa.xls",package="test.test_resources")
    reader = MRFRxls()

    txt = reader.read(fname)
    print(txt)

import sanic
from aiostream.stream import merge

from business.converters import CONV_FACTORY, hocr_f
from business.handlers import file_handler
from loguru import logger
from utils.format_utils import get_format


#
# def __call__(self, file, ct):
#
#     if "image/" in ct:
#         img = Image.open(io.BytesIO(file))
#         return self.img2hocr(img)
#     elif ct == "application/pdf":
#         return self.pdf2hocr(file)
#     else:
#         raise Exception("Not supported format")

def hocr_extract_file(file: sanic.request.File, output: {"text/html", "application/pdf", "application/json"} = "application/json", configs: dict = None):
    res = None
    logger.debug("start HOCR process")
    for file in file_handler(file):
        ext = hocr_f + get_format(file.name)
        converter = CONV_FACTORY.get(ext)()
        res_tmp = converter(file, output=output, configs=configs)
        res = merge(res, res_tmp) if res else res_tmp
    return res

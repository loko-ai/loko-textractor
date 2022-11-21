import asyncio

import sanic
from aiostream.stream import merge
from sanic.request import File

from ds4biz_textractor.business.converters import CONV_FACTORY, hocr_f
from ds4biz_textractor.business.handlers import file_handler
from ds4biz_textractor.utils.format_utils import get_format
from ds4biz_textractor.utils.logger_utils import logger


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

def hocr_extract_file(file: sanic.request.File, output: {"html", "pdf", "json"} = "json", configs: dict = None):
    res = None
    logger.debug("start HOCR process")
    for file in file_handler(file):
        ext = hocr_f + get_format(file.name)
        converter = CONV_FACTORY.get(ext)()
        res_tmp = converter(file, output=output, configs=configs)
        res = merge(res, res_tmp) if res else res_tmp
    return res

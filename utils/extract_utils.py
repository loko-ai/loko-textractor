
import sanic
from aiostream.stream import merge

from ds4biz_textractor.business.converters import CONV_FACTORY
from ds4biz_textractor.business.handlers import file_handler
from ds4biz_textractor.utils.format_utils import get_format


def extract_file(file: sanic.request.File, force_extraction: bool = False, configs: dict = None):
    res = None
    # print(file.name)
    for file in file_handler(file):
        ext = get_format(file.name)
        converter = CONV_FACTORY.get(ext)()
        if ext == "pdf":
            res_tmp = converter(file, force_extraction, configs=configs)
        else:
            res_tmp = converter(file, configs=configs)
        res = merge(res, res_tmp) if res else res_tmp
    return res

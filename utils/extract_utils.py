
import sanic
from aiostream.stream import merge

from business.converters import CONV_FACTORY
from business.handlers import file_handler
from loguru import logger
from utils.format_utils import get_format


def extract_file(file: sanic.request.File, force_extraction: bool = False, configs: dict = None):
    res = None
    for file in file_handler(file):
        ext = get_format(file.name)
        converter = CONV_FACTORY.get(ext)()
        logger.debug(f'Converter: {converter}')
        if ext == "pdf":
            res_tmp = converter(file, force_extraction, configs=configs)
        else:
            res_tmp = converter(file, configs=configs)
        res = merge(res, res_tmp) if res else res_tmp
    return res

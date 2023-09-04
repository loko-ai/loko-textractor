
import sanic
from aiostream.stream import merge

from business.converters import CONV_FACTORY
from business.handlers import file_handler
from loguru import logger
from utils.format_utils import get_format


import asyncio

from ds4biz_format_parsers.business.text_extractors import RESTDS4BizTextract
from sanic.request import File



def extract_file(file: sanic.request.File, force_extraction: bool = False, configs: dict = None):
    res = None
    for file in file_handler(file):
        ext = get_format(file.name)
        converter = CONV_FACTORY.get(ext)()
        extractor = Convert()
        logger.debug(f'Converter: {converter}')
        if ext == "pdf":
            res_tmp = converter(file, force_extraction, configs=configs)
        else:
            res_tmp = converter(file, configs=configs, extractor=extractor)
        res = merge(res, res_tmp) if res else res_tmp
    return res



class Convert(RESTDS4BizTextract):
##TODO:applicare ai file di attachment analyzer e preprocessing assegnati
    def __init__(self):
        super().__init__(url=None)

    async def extract(self, filename, accept='plain/text'):
        with open(filename, 'rb') as f:
            res = extract_file(File(type='', body=f.read(), name=filename), configs={})
            if accept == 'plain/text':
                return '\n'.join([el['text'] async for el in res])
            else:
                return [el async for el in res]

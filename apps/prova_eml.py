import asyncio
import email
from pprint import pprint

import sanic
from ds4biz_format_parsers.business.converters import Email2TextEmail
from ds4biz_format_parsers.business.text_extractors import RESTDS4BizTextract
from loguru import logger
from sanic.request import File

from utils.eml_utils import te2text
from utils.extract_utils import extract_file, Convert


class EML2text:

    def __init__(self):
        extractor = RESTDS4BizTextract(url='http://0.0.0.0:8081/ds4biz/textract/0.1/')
        self.e2t = Email2TextEmail(extractor)

    async def __call__(self, file: sanic.request.File, **kwargs):
        try:
            content = file.body
            if hasattr(content, "read"):
                text = self.e2t(email.message_from_binary_file(content))
            else:
                print('qui')
                te = self.e2t(email.message_from_bytes(content))
                print('qui2')
                text = te2text(te)
            yield te.__dict__
        except Exception as inst:
            logger.exception(inst)

conv = EML2text()

class Prova(RESTDS4BizTextract):
    def __init__(self):
        super().__init__(url=None)

    async def convert_file(self, accept='plain/text'):
        with open(self.filename, 'rb') as f:
            res = extract_file(File(type='', body=f.read(), name=self.filename), configs={})
            if accept == 'plain/text':
                return '\n'.join([el['text'] async for el in res])
            else:
                return [el async for el in res]

    def extract(self, filename):
        self.filename = filename
        return asyncio.run(self.convert_file())

#
# async def f():
#     with open("/home/roberta/Fwd_ restituzione degli atti firmati.eml", 'rb') as f:
#         async for el in conv(File(type='', body=f.read(), name='123.eml')):
#             pprint(el)


async def f2():
    with open("/home/roberta/example-page.png", 'rb') as f:
        res = extract_file(File(type='', body=f.read(), name='GNN.jpg'), configs={})
        return '\n'.join([el['text'] async for el in res])

res = asyncio.run(f2())
# print(res)
f = "/home/roberta/example-page.png"
# f = "/home/roberta/Fwd_ restituzione degli atti firmati.eml"
extractor = Convert(loop=asyncio.get_event_loop())
res = extractor.extract(f)
pprint(res)

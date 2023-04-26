import codecs
import email
import os
import subprocess
import tempfile
from zipfile import ZipFile

import rarfile
from loguru import logger
from sanic.request import File

from business.email_parser import Email2TextEmail2
from utils.eml_utils import te2text
from utils.process_utils import save2temp
from utils.resources_utils import get_resource

ENCODING = "latin"


class CompressedFileHandler():

    def __call__(self, file):
        raise Exception("Not implemented")


class CFHP7m(CompressedFileHandler):

    def __call__(self, file):
        file = save2temp(file)

        new_tmp = tempfile.NamedTemporaryFile(suffix=".pdf")

        subprocess.run(['openssl', 'smime', '-inform', 'DER', '-verify', '-noverify', '-in', file.name, '-out',
                        new_tmp.name], stdout=subprocess.PIPE)
        yield File(type='', body=open(new_tmp.name, 'rb').read(), name=file.name)



class CFHZip(CompressedFileHandler):

    def __call__(self, file):
        file = save2temp(file)
        zf = ZipFile(file.name)
        try:
            for fn in zf.infolist():
                if not fn.is_dir():
                    ext = os.path.splitext(fn.filename)[-1].lower()
                    new_tmp = tempfile.NamedTemporaryFile(suffix=ext)
                    yield File(type='', body=zf.read(fn), name=fn.filename)
        except Exception as inst:
            raise Exception("Error: extraction ZIP \n" + str(inst))
        finally:
            file.close()


class CFHRar(CompressedFileHandler):

    def __call__(self, file):
        rf = rarfile.RarFile(file.name)
        try:
            for fn in rf.infolist():
                logger.debug(f'Filename: {fn.filename}')
                ext = os.path.splitext(fn.filename)[-1].lower()
                new_tmp = tempfile.NamedTemporaryFile(suffix=ext)
                content = rf.read(fn)
                with open(new_tmp.name, 'wb') as f:
                    f.write(content)
                yield {'filename': fn.filename, 'file': new_tmp}
        except Exception as inst:
            logger.exception(inst)
            raise Exception("Error: extraction RAR \n" + str(inst))
        finally:
            file.close()


class CFHEml(CompressedFileHandler):

    def __init__(self):
        self.e2t = Email2TextEmail2(None)

    def __call__(self, file):

        content = open(file.name, 'rb').read()
        te = self.e2t(email.message_from_bytes(content))
        text = te2text(te)
        # yield dict(text=text, filename=file.name)
        for k,v in te.attachments.items():
            logger.debug(f'ATTACHMENT : {k}')
            yield File(type='', body=v, name=k)


class GenericFileHandler:
    def __call__(self, file):
        yield file


class HandlerFactory:

    def __init__(self, mapping=None):
        self.mapping = mapping or dict()

    def register(self, ext, value):
        self.mapping[ext] = value

    def get(self, ext):
        return self.mapping.get(ext, GenericFileHandler)()


HANDLER_FACTORY = HandlerFactory()
HANDLER_FACTORY.register('p7m', CFHP7m)
HANDLER_FACTORY.register('p7s', CFHP7m)
HANDLER_FACTORY.register('zip', CFHZip)
HANDLER_FACTORY.register('rar', CFHRar)
HANDLER_FACTORY.register('eml', CFHEml)


def file_handler(file):
    ext = file.name.split('.')[-1].lower()
    try:
        cfh = HANDLER_FACTORY.get(ext)
        for file_tmp in cfh(file):
            yield file_tmp

    except Exception as inst:
        raise inst
        # raise Exception('Extension not handled: {ext}'.format(ext=ext))


if __name__ == '__main__':
    fname = get_resource("ezyzip.zip", package="test.test_resources")
    file = open(fname, 'rb')
    # ext = os.path.splitext(fname)[-1].lower()
    # file_tmp = tempfile.NamedTemporaryFile(suffix=ext)
    # tmp = file.read()
    # with codecs.open(file_tmp.name, encoding=ENCODING, mode="wb") as fb:
    #     fb.write(tmp.decode(ENCODING))
    # res = file_handler(file_tmp)
    res = file_handler(file)
    print(list(res))

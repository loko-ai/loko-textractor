import codecs
import os
import subprocess
import tempfile
from zipfile import ZipFile

import rarfile
from sanic.request import File

from utils.process_utils import save2temp
from utils.resources_utils import get_resource

ENCODING = "latin"


class CompressedFileHandler():

    def __call__(self, file):
        raise Exception("Not implemented")


class CFHP7m(CompressedFileHandler):

    def __call__(self, file):
        new_tmp = tempfile.NamedTemporaryFile(suffix=".pdf")
        try:
            subprocess.run(['openssl', 'smime', '-inform', 'DER', '-verify', '-noverify', '-in', file.name, '-out',
                            new_tmp.name], stdout=subprocess.PIPE)
            yield {'file': new_tmp}
        except Exception as inst:
            raise Exception("Error: extraction P7M \n" + str(inst))


class CFHZip(CompressedFileHandler):

    def __call__(self, file):
        zf = ZipFile(file.name)
        try:
            for fn in zf.infolist():
                ext = os.path.splitext(fn.filename)[-1].lower()
                if not fn.is_dir():
                    ext = os.path.splitext(fn.filename)[-1].lower()
                    new_tmp = tempfile.NamedTemporaryFile(suffix=ext)
                    with codecs.open(new_tmp.name, encoding=ENCODING, mode="wb") as fb:
                        fb.write(zf.read(fn).decode(ENCODING))
                    yield {'filename': fn.filename, 'file': new_tmp}
        except Exception as inst:
            raise Exception("Error: extraction ZIP \n" + str(inst))
        finally:
            file.close()


class CFHRar(CompressedFileHandler):

    def __call__(self, file):
        rf = rarfile.RarFile(file.name)
        try:
            for fn in rf.infolist():
                ext = os.path.splitext(fn.filename)[-1].lower()
                new_tmp = tempfile.NamedTemporaryFile(suffix=ext)
                with open(new_tmp.name, 'wb') as f:
                    f.write(rf.read(fn))
                yield {'filename': fn.filename, 'file': new_tmp}
        except Exception as inst:
            raise Exception("Error: extraction RAR \n" + str(inst))
        finally:
            file.close()


class GenericFileHandler:
    def __call__(self, file):
        yield dict(file=file)


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


def file_handler(file):
    ofname = file.name
    file = save2temp(file)
    ext = file.name.split('.')[-1].lower()
    print(ext)
    try:
        cfh = HANDLER_FACTORY.get(ext)
        for file_tmp in cfh(file):
            fname = file_tmp.get('filename', file_tmp['file'].name)
            fname = fname if ext in ['zip', 'rar'] else ofname
            file = open(file_tmp['file'].name, 'rb').read()
            print(fname)
            yield File(name=fname, body=file, type='')
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

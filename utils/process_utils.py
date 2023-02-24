import codecs
import os
import tempfile

from PIL import Image
from sanic import request

from utils.resources_utils import get_resource

IMAGES_EXT = ["png", "jpg", "jpeg"]
BAW = "YES"
ENCODING = 'ISO-8859-1'

def save2temp(file: request.File):
    """

    :param file: input file to save
    :return file_tmp: temporary file
    """
    ext = os.path.splitext(file.name)[-1].lower()
    file_tmp = tempfile.NamedTemporaryFile(suffix=ext)
    ext = ext.replace('.','')
    tmp = file.body
    with codecs.open(file_tmp.name, encoding=ENCODING, mode="wb") as fb:
        fb.write(tmp.decode(ENCODING))

    if ext in IMAGES_EXT and BAW=="Y":
        image_file = image2imagebw(file_tmp.name)
        image_file.save(file_tmp.name)

    return file_tmp


def image2imagebw(fname):
    '''convert image in a grey scale image'''
    image_file = Image.open(fname)
    image_file = image_file.convert('L')
    return image_file


if __name__ == '__main__':
    fname = get_resource("aa.xls", package="test.test_resources")
    with open(fname, "rb") as f:
        print(save2temp(f))

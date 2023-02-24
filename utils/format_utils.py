import os

from config.app_config import SUPPORTED_EXT


def norm_ext(fname):
    r = os.path.splitext(fname)
    ext = ''.join(ch for ch in r[1] if ch.isalnum())
    if ext in SUPPORTED_EXT:
        return ".".join([r[0], ext])

    for e in SUPPORTED_EXT:
        if ext.startswith(e):
            ext = e

    return ".".join([r[0], ext])

def get_format(fname):

    # if hasattr(content,"read"):
    #     ext = magic.from_buffer(content.read(2048), mime=True)
    # else:
    #     ext = magic.from_buffer(io.BytesIO(content), mime=True)
    # return ext
    fname = norm_ext(fname)
    *rest, ext = fname.split(".")
    ext = ext.lower()
    return ext



if __name__ == '__main__':

    to_norm = ["jpg?=", "jpeg?=", "_pdf", "p7m?=", "aaf", "txt?=", "docx"]

    for el in to_norm:
        v = "alejandro." + el + "pdf"
        print(v, "-->", norm_ext(v))

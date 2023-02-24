import io

import fitz
from PIL import Image

from ds4biz_textractor.utils.logger_utils import logger


def manipulate_pdf_page(page: fitz.Page, dpi: int = None):
    img = page.get_pixmap(dpi=dpi)
    # img.save("img0_"+i+".jpg")
    data = img.tobytes("format")
    img = Image.open(io.BytesIO(data))
    logger.debug("actual dpi value: %s" % str(img.info['dpi']))
    # img.save("img1_" + str(i) + ".jpg")
    # print(page.rotation)
    img = img.rotate(360 - page.rotation, expand=True)
    # img.save("img3_"+str(i)+".jpg")
    logger.debug("image extracted and manipulated...")
    return img

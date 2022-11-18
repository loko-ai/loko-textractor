import asyncio
import sys

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image
from sanic.request import File

from ds4biz_textractor.utils.extract_utils import extract_file

wfname = '../../test/test_resources/DOC090519-09052019083949.pdf'


PATH = '/home/cecilia/Documenti/images/'

# async def main_body():
#     with open(wfname, 'rb') as f:
#         file = File(name = wfname.split('/')[-1], body = f.read(), type = '')
#     res = extract_file(file)
#     async for r in res:
#         print(r['text'])
#         print()
#         print()
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(asyncio.wait([main_body()]))


# with open(wfname, 'rb') as f:
#     file = f

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 3)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)

    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

doc = fitz.open("pdf", open(wfname, 'rb').read())
print(doc)
for i, page in enumerate(doc):
    text = page.getText()
    print(text)
    if not text:
        images = page.getImageList()

        print(images)

        pm = fitz.Pixmap(doc, images[0][0])  # prende la prima immagine

        size = [pm.width, pm.height]
        img = Image.frombytes("L", [pm.width, pm.height], pm.samples)

        img = img.rotate(360 - page.rotation, expand=True)

        img = img.convert('RGB')

        img = np.array(img)

        img = cv2.resize(img, None, fx=3, fy=3)

        cv2.imwrite(PATH+'img1.png', img)

        image = get_grayscale(img)
        # cv2.imshow('greyscale', image)
        cv2.imwrite(PATH+'greyscale.png', image)

        image = remove_noise(img)
        # cv2.imshow('remove noise', image)
        cv2.imwrite(PATH+'removenoise.png', image)

        #
        # image = thresholding(img)
        # cv2.imshow('thresholding', img)

        image = dilate(img)
        # cv2.imshow('dilate', image)
        cv2.imwrite(PATH+'dilate.png', image)

        image = erode(img)
        # cv2.imshow('erode', image)
        cv2.imwrite(PATH+'erode.png', image)

        image = opening(img)
        # cv2.imshow('opening', image)
        cv2.imwrite(PATH+'opening.png', image)

        image = canny(img)
        # cv2.imshow('canny', image)
        cv2.imwrite(PATH+'canny.png', image)

        img_new = remove_noise(img)
        img_new = erode(img_new)
        cv2.imwrite(PATH+'final.png', img_new)

        config = "--psm 6 --oem 1"# --user-words /home/cecilia/Documenti/images/vocab.txt"
        text = pytesseract.image_to_string(img_new, config=config, lang='ita')
        print(text)

        print()
        print()
        print('*'*20)
        print()
        print()

        text = pytesseract.image_to_string(img, config=config, lang='ita')
        print(text)

        # image = deskew(img)
        # cv2.imshow('deskew', image)

        # cv2.waitKey(0)

        # plt.imshow(img)
        # plt.show()

        # img = cv2.imread("book_page.jpg")

        # print(img.show())


# for i, page in enumerate(doc):
#     text = page.getText()
#
#     logger.info(f"Pagina {i}")
#     try:
#         if not text:  # da passare a tesseract
#             images = page.getImageList()
#
#             pm = fitz.Pixmap(doc, images[0][0])  # prende la prima immagine
#             logger.info(f"{images} {len(pm.samples)}")
#             size = [pm.width, pm.height]
#             img = Image.frombytes("L", [pm.width, pm.height], pm.samples)
#             img = img.rotate(360 - page.rotation, expand=True)
#
#             text = await loop.run_in_executor(POOL, functools.partial(pytesseract.image_to_string, lang="ita"),
#                                               img)
#             yield dict(i=i, text=text, filename = file.name )
#         else:
#             yield dict(i=i, text=text, filename = file.name)
#     except Exception as inst:
#         logging.exception(inst)
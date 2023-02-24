import asyncio
import os
import unittest
from datetime import datetime
from typing import List

import aiohttp
import requests

from utils.resources_utils import get_resource

ASYNC = True

BASE_URL = "http://localhost:8080/ds4biz/textract/0.1/extract"

PATH = get_resource(package="test.test_resources")


class TestFormats(unittest.TestCase):

    def get_files(self, exts: List[str]):
        fnames = [fn for fn in os.listdir(PATH) if not fn.startswith('__') and fn.split('.')[-1].lower() in exts]
        return fnames

    async def extract(self, fname):
        wfname = get_resource(fname, package="test.test_resources")
        start = datetime.now()
        files = {"file": open(wfname, "rb")}
        headers = {'accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.post(BASE_URL, data=files, headers=headers) as resp:
                print(resp.status)
                async for data, _ in resp.content.iter_chunks():
                    print(data)
                    print(_)
                res = await resp.text()
                print(res)
                end = datetime.now()
                print(fname, end - start, resp.status)
                self.assertEqual(resp.status, 200)

    def arequest(self, fnames: List[str]):
        start = datetime.now()
        futures = [self.extract(fname) for fname in fnames]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(futures))
        end = datetime.now()
        print(len(futures), 'documenti in', end - start)
        print()
        print()

    def request(self, fnames):
        for fname in fnames:
            wfname = get_resource(fname, package="test.test_resources")
            start = datetime.now()
            with open(wfname, 'rb') as f:
                resp = requests.post(BASE_URL, files={"file": f})
                end = datetime.now()
                print(fname, end - start, resp.status_code)
                self.assertEqual(resp.status_code, 200)

    def test_pdf_format(self):
        print()
        print()
        print('TEST PDF FORMAT')
        fnames = self.get_files(exts=['pdf'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_img_format(self):
        print()
        print()
        print('TEST IMG FORMAT')
        fnames = self.get_files(exts=['jpg', 'jpeg', 'png', 'tif'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_txt_format(self):
        fnames = self.get_files(exts=['txt'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_doc_format(self):
        fnames = self.get_files(exts=['doc'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_docx_format(self):
        print()
        print()
        print('TEST DOCX FORMAT')
        fnames = self.get_files(exts=['docx'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_eml_format(self):
        print()
        print()
        print('TEST EML FORMAT')
        fnames = self.get_files(exts=['eml'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_p7m_format(self):
        print()
        print()
        print('TEST P7M FORMAT')
        fnames = self.get_files(exts=['p7m', 'p7s'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_zip_format(self):
        print()
        print()
        print('TEST ZIP FORMAT')
        fnames = self.get_files(exts=["zip"])#'p7m', 'p7s'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)

    def test_rar_format(self):
        print()
        print()
        print('TEST RAR FORMAT')
        fnames = self.get_files(exts=['rar'])
        if ASYNC:
            self.arequest(fnames)
        else:
            self.request(fnames)


if __name__ == '__main__':
    unittest.main(verbosity=10)


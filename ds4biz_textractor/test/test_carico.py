import unittest
from datetime import datetime
import os

import aiohttp
import asyncio

from ds4biz_textractor.utils.resources_utils import get_resource

BASE_URL = "http://localhost:8080/ds4biz/textract/0.1/extract"

path = get_resource(package="test.test_resources")

exts = ['pdf', 'docx', 'tif', 'jpg', 'jpeg', 'png', 'eml'] # txt, doc
FNAMES = [fn for fn in os.listdir(path) if not fn.startswith('__') and fn.split('.')[-1] in exts]
# FNAMES = ['sentenza.pdf']*80


class TestCarico(unittest.TestCase):

    async def extract(self, fname):
        wfname = get_resource(fname, package="test.test_resources")
        start = datetime.now()
        files = {"file": open(wfname, "rb")}
        async with aiohttp.ClientSession() as session:
            async with session.post(BASE_URL, data=files) as resp:
                # print(resp.status)
                # async for data, _ in resp.content.iter_chunks():
                #     print(data)
                #     print(_)
                res = await resp.text()
                end = datetime.now()
                print(fname, end - start, resp.status)
                self.assertEqual(resp.status, 200)

    def test_parallel_requests(self):
        start = datetime.now()
        futures = [self.extract(fname) for fname in FNAMES]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(futures))
        end = datetime.now()
        print()
        print()
        print(len(futures), 'documenti in', end - start)





if __name__ == '__main__':
    unittest.main(verbosity=10)

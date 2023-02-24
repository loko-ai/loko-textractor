import asyncio

import aiohttp
import requests


BASE_URL = "http://localhost:8080/ds4biz/textract/0.1/extract"

wfname = '/home/cecilia/Scrivania/CeciliaMartinezOliva.pdf'
wfname = '../../test/test_resources/ezyzip.zip'


async def extract(fname, accept):
    files = {"file": open(fname, "rb")}
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL, data=files, headers=dict(accept=accept)) as resp:
            async for data, _ in resp.content.iter_chunks():
                print('########')
                print(data)


accept = 'application/json'
with open(wfname, 'rb') as f:
    resp = requests.post(BASE_URL, files={"file": f}, headers=dict(accept=accept))
print(accept)
print(resp.json())
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([extract(fname=wfname, accept=accept)]))

print()

accept = 'plain/text'
with open(wfname, 'rb') as f:
    resp = requests.post(BASE_URL, files={"file": f}, headers=dict(accept=accept))
print(accept)
print(repr(resp.json()))
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([extract(fname=wfname, accept=accept)]))
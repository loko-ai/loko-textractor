import asyncio

import aiohttp
import requests


async def extract(url, files):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=files, headers=dict(accept=ct)) as resp:
            print(resp.status)
            i = 0
            async for data, _ in resp.content.iter_chunks():
                print(i)
                print(data)
                print(_)
                if i==10:
                    break
                i+=1

fpath = '/home/cecilia/PycharmProjects/cartesio-lotto2-ee/cartesio-lotto2-ee/cartesio_lotto2_ee/test/resources/AllegatoTest1.pdf'
# fpath = "/home/roberta/Downloads/ilovepdf_merged (1).pdf"
url = 'http://0.0.0.0:8080/ds4biz/textract/0.1/extract'
file = dict(file=open(fpath, 'rb'))
ct = 'plain/text'
# ct = 'application/json'

### no stream ###
# resp = requests.post(url, files=file, headers=dict(accept=ct))
# if ct == 'application/json':
#     r = resp.json()
# else:
#     r = resp.text
# print(len(r))
# print(r)

### aiohttp stream ###
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.gather(extract(url, file)))

### requests stream ###
batchsize = 500*(2**10)
r = requests.post(url, files=file, headers=dict(accept=ct), stream=True)

pages = 0
for chunk in r.iter_content(batchsize):
    print(chunk)
    pages+=1
    if pages>10:
        break
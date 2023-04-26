import asyncio
import json
from io import StringIO
import aiohttp


async def extract(url, f, ct):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=dict(file=f, args=StringIO(json.dumps(dict(accept=ct))))) as resp:
            print(resp.status)
            i = 0
            async for data, _ in resp.content.iter_chunks():
                print(i)
                print(data)
                print(_)
                if i == 10:
                    break
                i += 1

fpath = '/home/cecilia/loko/projects/text_extraction_from_docs/data/cassazione.pdf'
url = 'http://0.0.0.0:9999/routes/loko-textractor/loko_extract'

# ct = 'plain/text'
# ct = 'application/json'
ct = 'application/jsonl'

with open(fpath, 'rb') as f:

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(extract(url, f, ct)))

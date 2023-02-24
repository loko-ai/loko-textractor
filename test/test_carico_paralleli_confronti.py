import asyncio
import concurrent
import os
import random
import sys
from datetime import datetime
import requests

BASE_URL_NEW = "http://localhost:8080/ds4biz/textract/0.1/extract"
BASE_URL_OLD = "http://localhost:8080/ds4biz/textract/0.2/extract"

NAMES = ['ds4biz-textractor:0.1.0-dev', 'ds4biz-textract:0.2.2-dev']
NAMES = ['ds4biz-textractor:0.1.0-dev']
# URLS = [BASE_URL_NEW, BASE_URL_OLD]
URLS = [BASE_URL_NEW]

def extract(fname, url):
    try:
        with open(fname, 'rb') as f:
            resp = requests.post(url, files={"file": f})
        print(fname, resp.status_code)
        if not resp.json():
            print('ATTENZIONE!!', fname)
            return None
        if len(resp.json()['text'])<100:
            print('ATTENZIONE!!', fname)
            print(resp.json())
        return resp.json()
    except:
        print('ATTENZIONE!!', fname)
        return None

BASE_PATH = '/home/cecilia/Documenti/pdfs/train_non_PEC/progetto_lavoro'


def test_parallel_requests(fnames, url):
    start = datetime.now()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(extract, fname, url) for fname in fnames]
    end = datetime.now()
    print()
    print()
    print(len(futures), 'documenti in', end - start)

random.seed(25)
fnames = os.listdir(BASE_PATH)
random.shuffle(fnames)

# sys.exit(0)
n = 100
print('NFILES:', len(fnames[:n]))
fnames = [os.path.join(BASE_PATH,fname) for fname in fnames[:n]]

test_parallel_requests(fnames, URLS[0])
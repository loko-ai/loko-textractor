import os
import time
from datetime import datetime
import requests

BASE_URL_NEW = "http://localhost:8080/ds4biz/textract/0.1/extract"
BASE_URL_OLD = "http://localhost:8080/ds4biz/textract/0.2/extract"

NAMES = ['ds4biz-textractor:0.1.0-dev', 'ds4biz-textract:0.2.2-dev']
NAMES = ['ds4biz-textractor:0.1.0-dev']
URLS = [BASE_URL_NEW, BASE_URL_OLD]
URLS = [BASE_URL_NEW]

def extract(fname, url):
    try:
        with open(fname, 'rb') as f:
            resp = requests.post(url, files={"file": f})
        print(resp.text)
        if not resp.json():
            print(fname)
        return resp.json()
    except:
        print(fname)
        return None

BASE_PATH = '/home/cecilia/Documenti/pdfs/train_non_PEC/progetto_lavoro'

n_docs = [100]

for n in n_docs:
    print('###TEST DI CARICO %s DOCUMENTS START###'%n)
    for tname, url in zip(NAMES, URLS):
        start = datetime.now()
        for i,fname in enumerate(os.listdir(BASE_PATH)[:n]):
            wfname = os.path.join(BASE_PATH, fname)
            # print(i, wfname)
            if (i+1)%10==0:
                print('%s: %s documents processed'%(tname, i+1))
            extract(wfname, url)
            # time.sleep(3)
        end = datetime.now()
        print('ENDED IN %s'%(end-start))

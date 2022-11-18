import re
from datetime import datetime

import requests

from ds4biz_textractor.utils.resources_utils import get_resource

BASE_URL_NEW = "http://localhost:8082/ds4biz/textract/0.1/extract"
BASE_URL_OLD = "http://localhost:8080/ds4biz/textract/0.2/extract"


def request(fname, url):
    wfname = get_resource(fname, package="test.test_resources")
    start = datetime.now()
    with open(wfname, 'rb') as f:
        resp = requests.post(url, files={"file": f})
        end = datetime.now()
        print(fname, end - start, resp.status_code)
    return resp.json()

res_new = request('sentenza.pdf', BASE_URL_NEW)['text']
res_old = request('sentenza.pdf', BASE_URL_OLD)['text']

print('TEXTRACTOR LENGTH', len(res_new))
print('TEXTRACT'
      ' LENGTH', len(res_old))
res_new = re.sub('\n+', '\n', res_new)
res_old = re.sub('\n+', '\n', res_old)
olds = res_old.split('\n')
news = res_new.split('\n')
olds = [o.strip() for o in olds if len(o.strip())>0]
news = [n.strip() for n in news if len(n.strip())>0]

for i,new in enumerate(news):
    print('TEXTRACTOR', new)
    print('TEXTRACT', olds[i])
    print()

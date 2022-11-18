import requests

BASE_URL = "http://localhost:8080/ds4biz/textract/0.1/extract"
wfname = '../../test/test_resources/readable.pdf'
wfname = '../../test/test_resources/sentenza.pdf.p7m'
wfname = '../../test/test_resources/ezyzip.zip'
# wfname = '../../test/test_resources/Europass.rar'

accept = 'application/json'
with open(wfname, 'rb') as f:
    resp = requests.post(BASE_URL, files={"file": f}, headers=dict(accept=accept))
print(accept)
print(resp.json())
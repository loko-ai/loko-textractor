import requests

fpath = '/home/cecilia/PycharmProjects/cartesio-lotto2-ee/cartesio-lotto2-ee/cartesio_lotto2_ee/test/resources/AllegatoTest1.pdf'
# fpath = "/home/roberta/Downloads/ilovepdf_merged (1).pdf"
url = 'http://0.0.0.0:8080/ds4biz/textract/0.1/hocr'
file = dict(file=open(fpath, 'rb'))
# ct = 'text/html'
# ct = 'application/json'
ct = 'application/pdf'

### no stream ###
resp = requests.post(url, files=file, headers=dict(accept=ct))
if ct != 'application/pdf':
    r = resp.json()
else:
    r = resp.content

print(len(r))
print(r)

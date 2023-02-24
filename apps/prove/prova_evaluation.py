import asyncio

from sanic.request import File

from utils.extract_utils import extract_file
from utils.ocr_evaluation_utils import documents_performance

path = '/home/robertaparisi/Documenti/report.xlsx'

async def main_body():
    annot_files = '../../test/test_resources/docswithannotations/doc/annot_file.zip'
    doc_files = '../../test/test_resources/docswithannotations/doc/ocr_file.zip'

    with open(annot_files, 'rb') as f:
        annot = File(name = annot_files, body = f.read(), type = '')
    with open(doc_files, 'rb') as f:
        file = File(name = doc_files, body = f.read(), type = '')
    annotation = extract_file(annot)
    file = extract_file(file)
    res = await documents_performance(file, annotation, report=True, output=path)
    print(res)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([main_body()]))
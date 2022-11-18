import warnings
from ast import literal_eval
from io import BytesIO

from loko_extensions.business.decorators import extract_value_args

# from ds4biz_textractor.business.converters import HOCR
from ds4biz_textractor.config.app_config import PREPROCESSING_PATH, ANALYZER_PATH, POSTPROCESSING_PATH, \
    PORT
from ds4biz_textractor.dao.file_system_dao import JSONFSDAO, TXTFSDAO
from ds4biz_textractor.model.data_models import EvaluateResponse, PreprocessingRequest, AnalyzerRequest, \
    PostprocessingRequest
from ds4biz_textractor.utils.configurations_utils import get_configurations_files, get_type_path, \
    save_users_file_from_txt
from ds4biz_textractor.utils.extract_utils import extract_file
from ds4biz_textractor.utils.hocr_utils import hocr_extract_file
from ds4biz_textractor.utils.logger_utils import logger
from ds4biz_textractor.utils.ocr_evaluation_utils import documents_performance

warnings.filterwarnings("ignore")
import asyncio

from sanic import Blueprint, response
from sanic import Sanic
from sanic.response import json, raw
from sanic_openapi import swagger_blueprint, doc

from ds4biz_textractor.utils.json_utils import stream_json
from ds4biz_textractor.utils.pom_utils import get_pom_major_minor

logger.debug("start initializing...")

name = "ds4biz-textract"
app = Sanic(name)
swagger_blueprint.url_prefix = "/api"

bp = Blueprint("default", url_prefix=f"ds4biz/textract/{get_pom_major_minor()}")
app.config["API_VERSION"] = get_pom_major_minor()
app.config["API_TITLE"] = name
app.blueprint(swagger_blueprint)

from sanic.response import text


# @app.exception(Exception)
# async def generic_exception(request, exception):
#     j = dict(error=str(exception))
#     logging.debug(j)
#     if isinstance(exception, NotFound):
#         return response.json(j, status=404)
#     return response.json(j)


def text_resp(data):
    # return data
    logger.debug(data)
    return ''.join([el['text'] for el in data])


def json_resp(data):
    # return dict(text=data)
    return data


CONVERTER = dict()
CONVERTER['application/json'] = json_resp
CONVERTER['plain/text'] = text_resp
CONVERTER['*/*'] = json_resp


def response_converter(data, ct):
    data = CONVERTER[ct](data)
    return data


def stream_resp(obj):
    async def ret(response):
        async for el in stream_json(obj):
            await response.send(el)
            await asyncio.sleep(0.001)

    return ret


### EXTRACT

@bp.post("/extract")
@doc.summary('')
@doc.tag('extract services')
@doc.consumes(doc.String(name="accept", choices=["application/json", "plain/text"],
                         description="If plain is selected the entire ocr-doc will be returned, otherwise the response will be a json which separates each page. Default='application/json'"),
              location="header")
@doc.consumes(doc.String(name="postprocessing_configs"), location="query")
@doc.consumes(doc.String(name="analyzer_configs"), location="query")
@doc.consumes(doc.String(name="preprocessing_configs"), location="query")
@doc.consumes(doc.Boolean(name="force_ocr_extraction", description="Available only for .pdf files. Default=False"),
              location="query")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
async def convert(request):
    # start = time.time()
    configs = get_configurations_files(request.args)
    logger.debug("selected config: %s", configs)

    file = request.files.get('file')
    accept_ct = request.headers.get("accept", 'application/json')
    if accept_ct == "*/*":
        accept_ct = 'application/json'

    force_extraction = eval(request.args.get("force_ocr_extraction", "false").capitalize())
    res = extract_file(file, force_extraction, configs=configs)

    # ret = response_converter(StreamString((el['text'] async for el in res)), accept_ct)
    ret = response_converter([el async for el in res], accept_ct)
    response = await request.respond()
    # end=time.time()
    # print("time: "+ str(end-start))
    await stream_resp(ret)(response)
    # return stream(stream_resp(ret), content_type=accept_ct)


@bp.post("/hocr")
@doc.description(
    'Content Negotiation:<br>application/json->bounding boxes(default)<br>application/pdf->searchable pdf<br>text/html->html tags')
@doc.tag('extract services')
@doc.consumes(doc.String(name="accept", choices=["application/pdf", "application/json", "text/html"]),
              location="header")
@doc.consumes(doc.String(name="postprocessing_configs"), location="query")
@doc.consumes(doc.String(name="analyzer_configs"), location="query")
@doc.consumes(doc.String(name="preprocessing_configs"), location="query")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
async def hocr(request):
    configs = get_configurations_files(request.args)
    logger.debug("configs: %s", configs)
    accept = request.headers.get("accept", 'application/pdf').split("/")[-1]
    file = request.files.get('file')
    logger.debug("HOCR on file %s" % file.name)
    output = await hocr_extract_file(file=file, output=accept, configs=configs)
    # output = hocr(file.body, ct=magic.from_buffer(file.body, mime=True))
    # print(output.getvalue())
    # ret = response_converter([el async for el in output], accept)
    print(output)
    if accept == "pdf":
        original_ext = file.name.split('.')[-1].lower()
        if original_ext != ".pdf":
            headers = {'Content-Disposition': 'attachment; filename="{}.pdf"'.format(file.name)}
        else:
            headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file.name)}
        return raw(output.getvalue(), headers=headers)
    print(json(output))
    return json(output)


### EVALUATE
@bp.post("/evaluate")
@doc.tag('extract services')
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data")
@doc.consumes(doc.File(name="annotation"), location="formData", content_type="multipart/form-data")
@doc.consumes(doc.Boolean(name="report"), location="query")
async def evaluate(request):
    file = request.files.get('file')
    ann = request.files.get('annotation')
    report = request.args.get('report')
    report = literal_eval(report.title())
    file = extract_file(file)
    ann = extract_file(ann)
    output = BytesIO() if report else None
    res = await documents_performance(file, ann, report, output)
    if report:
        output.seek(0)
        body = output.getvalue()
        headers = {'Content-Disposition': 'attachment; filename="{}"'.format('OCR_evaluation.xlsx')}
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response.raw(body=body, headers=headers, content_type=content_type)

    res = dict(text=EvaluateResponse(**res['text']).__dict__,
               tokens=EvaluateResponse(**res['tokens']).__dict__)
    return json(res)


### PREPROCESSING
preprocessing_params = '''
<b>name:</b> preprocessing name
<b>resize:</b> resize image'''


@bp.post("/preprocessing/<name>")
@doc.tag('preprocessing configs')
@doc.summary("Save an object in 'preprocessing'")
@doc.description(preprocessing_params)
@doc.consumes(doc.Float(name="zoom_level"), location="query")
@doc.consumes(doc.String(name="interpolation_mode"), location="query")
@doc.consumes(doc.Integer(name="dpi"), location="query")
@doc.consumes(doc.String(name="name"), location="path")
# self.resize_dim = resize_dim
async def save_preprocessing(request, name):
    logger.debug("saving pre-processing %s" % (name))
    logger.debug("preprocessing_")
    data = PreprocessingRequest(**request.args).__dict__
    logger.debug("pre-processing initialized")
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    json_fs_dao.save(data, name)
    logger.debug("pre-processing saved")
    return text("preprocessing configuration saved as '%s'" % name)


@bp.get("/preprocessing/<name>")
@doc.tag('preprocessing configs')
@doc.summary("Display object info from 'preprocessing'")
@doc.consumes(doc.String(name="name"), location="path")
async def preprocessing_info(request, name):
    logger.debug("asking preprocessing %s info" % name)
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    content = json_fs_dao.get_by_id(name)
    return json(content)


@bp.delete("/preprocessing/<name>")
@doc.tag('preprocessing configs')
@doc.summary("Delete an object from 'preprocessing'")
@doc.consumes(doc.String(name="name"), location="path")
async def delete_preprocessing(request, name):
    logger.debug("delete preprocessing %s" % (name))
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    json_fs_dao.remove(name)
    return text("preprocessing configuration '%s' deleted" % name)


@bp.get("/preprocessing")
@doc.tag('preprocessing configs')
@doc.summary("List objects in 'preprocessing'")
async def list_preprocessings(request):
    logger.debug("listing preprocessing object..")
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    return json(json_fs_dao.all())


### ANALYZER
analyzer_params = '''
<b>name:</b> analyzer name
<b>vocab_file:</b> vocabulary file name
<b>patterns_file:</b> patterns file name
<b>oem:</b> OCR engine mode
<dd>\n
0: legacy engine only
1: neural nets LSTM engine only (default)
2: legacy + LSTM engines
3: default, based on what is available
</dd>
\n
<b>psm:</b> page segmentation mode
<dd>\n
0: orientation and script detection (OSD) only
1: automatic page segmentation with OSD (default)
2: automatic page segmentation, but no OSD, or OCR
3: fully automatic page segmentation, but no OSD
4: assume a single column of text of variable sizes
5: assume a single uniform block of vertically aligned text
6: assume a single uniform block of text
7: treat the image as a single text line
8: treat the image as a single word
9: treat the image as a single word in a circle
10: treat the image as a single character
11: sparse text. Find as much text as possible in no particular order
12: sparse text with OSD
13: raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific
</dd>
\n
<b>lang:</b> language, set to none for automatically detection
<b>whitelist:</b> subset of characters to detect
<b>blacklist:</b> subset of characters to exclude
'''


@bp.post("/analyzer/<name>")
@doc.tag('analyzer configs')
@doc.summary("Save an object in 'analyzer'")
@doc.description(analyzer_params)
@doc.consumes(doc.String(name="blacklist"), location="query")
@doc.consumes(doc.String(name="whitelist"), location="query")
@doc.consumes(doc.String(name="lang"), location="query")
@doc.consumes(doc.Integer(name="psm"), location="query", required=True)
@doc.consumes(doc.Integer(name="oem"), location="query", required=True)
@doc.consumes(doc.String(name="patterns_file"), location="query")
@doc.consumes(doc.String(name="vocab_file"), location="query")
@doc.consumes(doc.String(name="name"), location="path")
async def save_analyzer(request, name):
    logger.debug("saving analyzer %s" % name)
    # args = request.args
    # print("args", args)
    # # if
    # if "vocab_file" in args:
    #     vocab_file = args["vocab_file"]
    #     if "/" in vocab_file:
    #         vocab_file = save_users_file_from_txt(filepath=vocab_file[0], type="vocabulary", name=name)
    #     else:
    #         vocab_file = vocab_file[0]
    #         print(vocab_file)
    #
    # if "patterns_file" in args:
    #     patterns_file = args["patterns_file"]
    #     if "/" in patterns_file:
    #         patterns_file = save_users_file_from_txt(filepath=patterns_file[0], type="vocabulary", name=name)

    data = AnalyzerRequest(**request.args).__dict__
    logger.debug("analyzer initialized")
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    json_fs_dao.save(data, name)
    logger.debug("analyzer saved")
    return text("analyzer configuration saved as '%s'" % name)


#     # data = request.args['data']
#     # data = '\n'.join(data[0].split(','))
#     txt_fs_dao.save(data, name)
#     logger.debug("file saved")
#     return text("%s type file saved as '%s'" % (type, name))

@bp.get("/analyzer/<name>")
@doc.tag('analyzer configs')
@doc.summary("Display object info from 'analyzer'")
@doc.consumes(doc.String(name="name"), location="path")
async def analyzer_info(request, name):
    logger.debug("asking analyzer %s info" % (name))
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    content = json_fs_dao.get_by_id(name)
    return json(content)


@bp.delete("/analyzer/<name>")
@doc.tag('analyzer configs')
@doc.summary("Delete an object from 'analyzer'")
@doc.consumes(doc.String(name="name"), location="path")
async def delete_analyzer(request, name):
    logger.debug("deleting analyzer %s" % (name))
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    json_fs_dao.remove(name)
    return text("analyzer configuration '%s' deleted" % name)


@bp.get("/analyzer")
@doc.tag('analyzer configs')
@doc.summary("List objects in 'analyzer'")
async def list_analyzers(request):
    logger.debug("listing analyzer object...")
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    return json(json_fs_dao.all())


### POSTPROCESSING
@bp.post("/postprocessing/<name>")
@doc.tag('postprocessing configs')
@doc.summary("Save an object in 'postprocessing'")
@doc.consumes(doc.String(name="name"), location="path")
@doc.consumes(doc.String(name="name"), location="path")
async def save_postprocessing(request, name):
    logger.debug("saving post-processing %s" % name)
    data = PostprocessingRequest(**request.args).__dict__
    logger.debug("post-processing initialized")
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    json_fs_dao.save(data, name)
    logger.debug("post-processing saved")
    return text("postprocessing configuration saved as '%s'" % name)


@bp.get("/postprocessing/<name>")
@doc.tag('postprocessing configs')
@doc.summary("Display object info from 'postprocessing'")
@doc.consumes(doc.String(name="name"), location="path")
async def postprocessing_info(request, name):
    logger.debug("asking post-processing %s info" % (name))
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    content = json_fs_dao.get_by_id(name)
    return json(content)


@bp.delete("/postprocessing/<name>")
@doc.tag('postprocessing configs')
@doc.summary("Delete an object from 'postprocessing'")
@doc.consumes(doc.String(name="name"), location="path")
async def delete_postprocessing(request, name):
    logger.debug("deleting post-processing %s" % (name))
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    json_fs_dao.remove(name)
    return text("postprocessing configuration '%s' deleted" % name)


@bp.get("/postprocessing")
@doc.tag('postprocessing configs')
@doc.summary("List objects in 'postprocessing'")
async def list_postprocessings(request):
    logger.debug("listing post-processing object...")
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    return json(json_fs_dao.all())


files_params = '''
<b>name:</b> vocabulary/patterns name
<b>type:</b> vocabulary or patterns'''


@bp.post("/files/<type>/<name>")
@doc.tag('vocabulary and patterns')
@doc.summary("Save an object in 'vocabulary' or 'patterns'")
@doc.description(files_params)
@doc.consumes(doc.List(name="data"), required=True)
@doc.consumes(doc.String(name="name"), location="path")
@doc.consumes(doc.String(name="type", choices=["vocabulary", "patterns"]), location="path")
async def save_file(request, type, name):
    logger.debug("saving file %s (type %s)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    data = request.args['data']
    data = '\n'.join(data[0].split(','))
    txt_fs_dao.save(data, name)
    logger.debug("file saved")
    return text("%s type file saved as '%s'" % (type, name))


@bp.get("/files/<type>/<name>")
@doc.tag('vocabulary and patterns')
@doc.description(files_params)
@doc.summary("Display object info from 'vocabulary' or 'patterns'")
@doc.consumes(doc.String(name="name"), location="path")
@doc.consumes(doc.String(name="type", choices=["vocabulary", "patterns"]), location="path")
async def file_info(request, type, name):
    logger.debug("asking info on %s (%s file)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    content = txt_fs_dao.get_by_id(name)
    content = content.split('\n')
    logger.debug("content: %s" % content)
    return json(content)


@bp.delete("/files/<type>/<name>")
@doc.tag('vocabulary and patterns')
@doc.description(files_params)
@doc.summary("Delete an object from 'vocabulary' or 'patterns'")
@doc.consumes(doc.String(name="name"), location="path")
@doc.consumes(doc.String(name="type", choices=["vocabulary", "patterns"]), location="path")
async def delete_file(request, type, name):
    logger.debug("deleting file %s (%s)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    txt_fs_dao.remove(name)
    return text("%s '%s' deleted" % (type, name))


@bp.get("/files/<type>")
@doc.tag('vocabulary and patterns')
@doc.summary("List objects in 'vocabulary' or 'patterns'")
@doc.description("<b>type:</b> vocabulary or patterns")
@doc.consumes(doc.String(name="type", choices=["vocabulary", "patterns"]), location="path")
async def list_files(request, type):
    logger.debug("listing %s file..." % type)
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    return json(txt_fs_dao.all())


@app.post("/loko_extract")
@extract_value_args(file=True)
async def loko_extract(file, args):
    configs = get_configurations_files(args)
    logger.debug("selected config: %s", configs)
    if isinstance(file, list):
        file = file[0]
    accept_ct = 'application/json'

    force_extraction = eval(args.get("force_ocr_extraction", "false").capitalize())
    res = extract_file(file, force_extraction, configs=configs)

    # ret = response_converter(StreamString((el['text'] async for el in res)), accept_ct)
    data = []
    async for el in res:
        data.append(el)

    ret = response_converter(data, accept_ct)
    # response = await request.respond()
    # end=time.time()
    # print("time: "+ str(end-start))
    return json(ret)


app.blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, auto_reload=True)

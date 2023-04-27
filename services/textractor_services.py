import json
from ast import literal_eval
from io import BytesIO

from loguru import logger
from loko_client.business.fs_client import AsyncFSClient
from loko_extensions.business.decorators import extract_value_args

from config.app_config import PREPROCESSING_PATH, ANALYZER_PATH, POSTPROCESSING_PATH, \
    PORT, GATEWAY, VOCABULARY_PATH, PATTERNS_PATH
from dao.file_system_dao import JSONFSDAO, TXTFSDAO
from model.data_models import EvaluateResponse, PreprocessingRequest, AnalyzerRequest, \
    PostprocessingRequest
import sanic
from sanic.exceptions import NotFound
from sanic_ext import Config
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Parameter
from sanic_ext.extensions.openapi.types import String
from utils.configurations_utils import get_configurations_files, get_type_path
from utils.extract_utils import extract_file
from utils.hocr_utils import hocr_extract_file
from utils.ocr_evaluation_utils import documents_performance

from sanic import Blueprint, response
from sanic import Sanic

from utils.json_utils import stream_json
from utils.pom_utils import get_pom_major_minor

logger.debug("start initializing...")

loko_cli = AsyncFSClient(GATEWAY)

name = "ds4biz-textract"
app = Sanic(name)
app.extend(config=Config(oas_url_prefix='/api', oas_ui_default='swagger',
                         swagger_ui_configuration=dict(DocExpansion=None)))

bp = Blueprint("default", url_prefix=f"ds4biz/textract/{get_pom_major_minor()}")
app.config["API_VERSION"] = get_pom_major_minor()
app.config["API_TITLE"] = name


def file(name='file'):
    def tmp(f):
        content = {"multipart/form-data": {"schema": {"type": "object", "properties": {name: {"type": "string", "format": "binary"}}}}}
        return openapi.body(content, required=True)(f)
    return tmp


@app.listener("before_server_start")
async def before_server_start(app: Sanic, loop):
    app.ctx.loop=loop

@app.exception(Exception)
async def generic_exception(request, exception):
    try:
        e = str(exception)
        j = dict(error=e)

        status_code = getattr(exception, "status_code", None) or 500
        if isinstance(exception, NotFound):
            logger.error(NotFound)
            return sanic.response.json(j, status=404, headers={"Access-Control-Allow-Origin": "*"})
        logger.exception(e)

        return sanic.response.json(j, status=status_code, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as inst:
        logger.exception(inst)




def stream_resp(obj):
    async def ret(response):
        async for el in obj:
            await response.write(el)

    return ret


### EXTRACT

@bp.post("/extract")
@openapi.summary(' ')
@openapi.tag('extract services')
@openapi.response(content={"application/json": {}, "plain/text": {}},
                  description="If plain is selected the entire ocr-doc will be returned, otherwise the response will be a json which separates each page. Default='application/json'")
@openapi.parameter(name="postprocessing_configs", location="query")
@openapi.parameter(name="analyzer_configs", location="query")
@openapi.parameter(name="preprocessing_configs", location="query")
@openapi.parameter(name="force_ocr_extraction", description="Available only for .pdf files. Default=False",
                   location="query", schema=bool)
@file()
async def convert(request):

    configs = get_configurations_files(request.args)
    logger.debug("selected config: %s", configs)

    file = request.files.get('file')
    accept_ct = request.headers.get("accept", 'application/json')
    if accept_ct == "*/*":
        accept_ct = 'application/json'

    logger.debug(f'Filename: {file.name}')

    force_extraction = eval(request.args.get("force_ocr_extraction", "false").capitalize())
    logger.debug(force_extraction)
    res = extract_file(file, force_extraction, configs=configs)
    if accept_ct=='plain/text':
        response = await request.respond(content_type='plain/text; charset=utf-8')
        async for page in res:
            await response.send(page['text'])
        await response.eof()
        return
    if accept_ct == 'application/jsonl':
        async def gen():
            async for page in res:
                yield json.dumps(page)+'\n'
        return sanic.response.ResponseStream(stream_resp(gen()), headers={'content-type': 'application/jsonl'})
    ### if accept is not one of the above return content-type: application/json ###
    return sanic.response.ResponseStream(stream_resp(stream_json(res)), headers={'content-type': 'application/json'})


@bp.post("/hocr")
@openapi.summary(' ')
@openapi.description(
    'Content Negotiation:<br>application/json->bounding boxes(default)<br>application/pdf->searchable pdf<br>text/html->html tags')
@openapi.tag('extract services')
@openapi.response(content={"application/pdf": {}, "application/json": {}, "text/html": {}})
@openapi.parameter(name="postprocessing_configs", location="query")
@openapi.parameter(name="analyzer_configs", location="query")
@openapi.parameter(name="preprocessing_configs", location="query")
@file()
async def hocr(request):
    configs = get_configurations_files(request.args)
    logger.debug("configs: %s", configs)
    accept = request.headers.get("accept", 'application/pdf')
    file = request.files.get('file')
    logger.debug("HOCR on file %s" % file.name)
    output = await hocr_extract_file(file=file, output=accept, configs=configs)
    # output = hocr(file.body, ct=magic.from_buffer(file.body, mime=True))
    # print(output.getvalue())
    # ret = response_converter([el async for el in output], accept)
    if accept == "application/pdf":
        original_ext = file.name.split('.')[-1].lower()
        if original_ext != ".pdf":
            headers = {'Content-Disposition': 'attachment; filename="{}.pdf"'.format(file.name)}
        else:
            headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file.name)}
        return sanic.response.raw(output.getvalue(), headers=headers)

    return sanic.response.json(output)


### EVALUATE
@bp.post("/evaluate")
@openapi.tag('extract services')
@openapi.summary(' ')
@file(name='file')
@file(name='annotation')
@openapi.parameter(name="report", schema=bool, location="query")
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
    return sanic.response.json(res)


### PREPROCESSING
preprocessing_params = '''
<b>name:</b> preprocessing name
<b>resize:</b> resize image'''


@bp.post("/preprocessing/<name>")
@openapi.tag('preprocessing configs')
@openapi.summary("Save an object in 'preprocessing'")
@openapi.description(preprocessing_params)
@openapi.parameter(name="zoom_level", schema=float, location="query")
@openapi.parameter(name="interpolation_mode", location="query")
@openapi.parameter(name="dpi", schema=int, location="query")
@openapi.parameter(name="name", location="path")
# self.resize_dim = resize_dim
async def save_preprocessing(request, name):
    logger.debug("saving pre-processing %s" % (name))
    logger.debug("preprocessing_")
    data = PreprocessingRequest(**request.args).__dict__
    logger.debug("pre-processing initialized")
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    json_fs_dao.save(data, name)
    logger.debug("pre-processing saved")
    return sanic.response.text("preprocessing configuration saved as '%s'" % name)


@bp.get("/preprocessing/<name>")
@openapi.tag('preprocessing configs')
@openapi.summary("Display object info from 'preprocessing'")
@openapi.parameter(name="name", location="path")
async def preprocessing_info(request, name):
    logger.debug("asking preprocessing %s info" % name)
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    content = json_fs_dao.get_by_id(name)
    return sanic.response.json(content)


@bp.delete("/preprocessing/<name>")
@openapi.tag('preprocessing configs')
@openapi.summary("Delete an object from 'preprocessing'")
@openapi.parameter(name="name", location="path")
async def delete_preprocessing(request, name):
    logger.debug("delete preprocessing %s" % (name))
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    json_fs_dao.remove(name)
    return sanic.response.text("preprocessing configuration '%s' deleted" % name)


@bp.get("/preprocessing")
@openapi.tag('preprocessing configs')
@openapi.summary("List objects in 'preprocessing'")
async def list_preprocessings(request):
    logger.debug("listing preprocessing object..")
    json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
    return sanic.response.json(json_fs_dao.all())


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
@openapi.tag('analyzer configs')
@openapi.summary("Save an object in 'analyzer'")
@openapi.description(analyzer_params)
@openapi.parameter(name="blacklist", location="query")
@openapi.parameter(name="whitelist", location="query")
@openapi.parameter(name="lang", location="query")
@openapi.parameter(name="psm", schema=int, location="query", required=True)
@openapi.parameter(name="oem", schema=int, location="query", required=True)
@openapi.parameter(name="patterns_file", location="query")
@openapi.parameter(name="vocab_file", location="query")
@openapi.parameter(name="name", location="path")
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
    return sanic.response.text("analyzer configuration saved as '%s'" % name)


#     # data = request.args['data']
#     # data = '\n'.join(data[0].split(','))
#     txt_fs_dao.save(data, name)
#     logger.debug("file saved")
#     return text("%s type file saved as '%s'" % (type, name))

@bp.get("/analyzer/<name>")
@openapi.tag('analyzer configs')
@openapi.summary("Display object info from 'analyzer'")
@openapi.parameter(name="name", location="path")
async def analyzer_info(request, name):
    logger.debug("asking analyzer %s info" % (name))
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    content = json_fs_dao.get_by_id(name)
    return sanic.response.json(content)


@bp.delete("/analyzer/<name>")
@openapi.tag('analyzer configs')
@openapi.summary("Delete an object from 'analyzer'")
@openapi.parameter(name="name", location="path")
async def delete_analyzer(request, name):
    logger.debug("deleting analyzer %s" % (name))
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    json_fs_dao.remove(name)
    return sanic.response.text("analyzer configuration '%s' deleted" % name)


@bp.get("/analyzer")
@openapi.tag('analyzer configs')
@openapi.summary("List objects in 'analyzer'")
async def list_analyzers(request):
    logger.debug("listing analyzer object...")
    json_fs_dao = JSONFSDAO(ANALYZER_PATH)
    return sanic.response.json(json_fs_dao.all())


### POSTPROCESSING
@bp.post("/postprocessing/<name>")
@openapi.tag('postprocessing configs')
@openapi.summary("Save an object in 'postprocessing'")
@openapi.parameter(name="name", location="path")
async def save_postprocessing(request, name):
    logger.debug("saving post-processing %s" % name)
    data = PostprocessingRequest(**request.args).__dict__
    logger.debug("post-processing initialized")
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    json_fs_dao.save(data, name)
    logger.debug("post-processing saved")
    return sanic.response.text("postprocessing configuration saved as '%s'" % name)


@bp.get("/postprocessing/<name>")
@openapi.tag('postprocessing configs')
@openapi.summary("Display object info from 'postprocessing'")
@openapi.parameter(name="name", location="path")
async def postprocessing_info(request, name):
    logger.debug("asking post-processing %s info" % (name))
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    content = json_fs_dao.get_by_id(name)
    return sanic.response.json(content)


@bp.delete("/postprocessing/<name>")
@openapi.tag('postprocessing configs')
@openapi.summary("Delete an object from 'postprocessing'")
@openapi.parameter(name="name", location="path")
async def delete_postprocessing(request, name):
    logger.debug("deleting post-processing %s" % (name))
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    json_fs_dao.remove(name)
    return sanic.response.text("postprocessing configuration '%s' deleted" % name)


@bp.get("/postprocessing")
@openapi.tag('postprocessing configs')
@openapi.summary("List objects in 'postprocessing'")
async def list_postprocessings(request):
    logger.debug("listing post-processing object...")
    json_fs_dao = JSONFSDAO(POSTPROCESSING_PATH)
    return sanic.response.json(json_fs_dao.all())


files_params = '''
<b>name:</b> vocabulary/patterns name
<b>type:</b> vocabulary or patterns'''


@bp.post("/files/<type>/<name>")
@openapi.tag('vocabulary and patterns')
@openapi.summary("Save an object in 'vocabulary' or 'patterns'")
@openapi.description(files_params)
@openapi.parameter(name="data", required=True)
@openapi.parameter(name="name", location="path")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
async def save_file(request, type, name):
    logger.debug("saving file %s (type %s)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    data = request.args['data']
    data = '\n'.join(data[0].split(','))
    txt_fs_dao.save(data, name)
    logger.debug("file saved")
    return sanic.response.text("%s type file saved as '%s'" % (type, name))


@bp.get("/files/<type>/<name>")
@openapi.tag('vocabulary and patterns')
@openapi.description(files_params)
@openapi.summary("Display object info from 'vocabulary' or 'patterns'")
@openapi.parameter(name="name", location="path")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
async def file_info(request, type, name):
    logger.debug("asking info on %s (%s file)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    content = txt_fs_dao.get_by_id(name)
    content = content.split('\n')
    logger.debug("content: %s" % content)
    return sanic.response.json(content)


@bp.delete("/files/<type>/<name>")
@openapi.tag('vocabulary and patterns')
@openapi.description(files_params)
@openapi.summary("Delete an object from 'vocabulary' or 'patterns'")
@openapi.parameter(name="name", location="path")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
async def delete_file(request, type, name):
    logger.debug("deleting file %s (%s)" % (name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    txt_fs_dao.remove(name)
    return sanic.response.text("%s '%s' deleted" % (type, name))


@bp.get("/files/<type>")
@openapi.tag('vocabulary and patterns')
@openapi.summary("List objects in 'vocabulary' or 'patterns'")
@openapi.description("<b>type:</b> vocabulary or patterns")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
async def list_files(request, type):
    logger.debug("listing %s file..." % type)
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    return sanic.response.json(txt_fs_dao.all())


@app.post("/loko_extract")
@openapi.tag('loko')
@openapi.summary(' ')
@extract_value_args(file=True)
async def loko_extract(file, args):

    accept_ct = args.get("accept", "application/json")
    analyzer = args.get("analyzer")
    pre_processing = args.get("preprocessing")
    force_ocr = args.get("force_ocr")

    logger.debug(f'Filename: {file[0].name}')

    if analyzer:
        json_fs_dao = JSONFSDAO(ANALYZER_PATH)
        if analyzer not in list(json_fs_dao.all()):
            logger.warning(
                'Analyzer {anal} not anymore available. Extraction will be performed without considering '
                'it.'.format(
                    anal=analyzer))
            analyzer = None

    if pre_processing:

        json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)

        if pre_processing not in list(json_fs_dao.all()):
            logger.warning(
                "Pre-processing {preproc} not anymore available. Extraction will be performed without considering it.".format(
                    preproc=pre_processing))
            pre_processing = None

    params = dict(force_ocr=str(force_ocr).lower(), analyzer_configs=analyzer,
                  preprocessing_configs=pre_processing,
                  # postprocessing_configs=post_processing
                  )

    configs = get_configurations_files(params)
    logger.debug(f"selected config: {configs}")
    if isinstance(file, list):
        file = file[0]
    logger.info(f'Filename: {file.name}')

    force_extraction = eval(params.get("force_ocr_extraction", "false").capitalize())
    res = extract_file(file, force_extraction, configs=configs)

    if accept_ct == 'plain/text':
        async def gen():
            async for page in res:
                yield page['text']

        return sanic.response.ResponseStream(stream_resp(gen()), headers={'content-type': 'plain/text; charset=utf-8'})

    if accept_ct == 'application/jsonl':
        async def gen():
            async for page in res:
                yield json.dumps(page) + '\n'

        return sanic.response.ResponseStream(stream_resp(gen()), headers={'content-type': 'application/jsonl'})

    ### if accept is not one of the above return content-type: application/json ###
    return sanic.response.ResponseStream(stream_resp(stream_json(res)), headers={'content-type': 'application/json'})

# @bp.post("/hocr")
# @doc.description(
#     'Content Negotiation:<br>application/json->bounding boxes(default)<br>application/pdf->searchable pdf<br>text/html->html tags')
# @doc.tag('extract services')
# @doc.consumes(doc.String(name="accept", choices=["application/pdf", "application/json", "text/html"]),
#               location="header")
# @doc.consumes(doc.String(name="postprocessing_configs"), location="query")
# @doc.consumes(doc.String(name="analyzer_configs"), location="query")
# @doc.consumes(doc.String(name="preprocessing_configs"), location="query")
# @doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)

@app.post("/loko_hocr")
@openapi.tag('loko')
@openapi.summary(' ')
@extract_value_args(file=True)
async def hocr(file, args):

    accept_ct = args.get("accept_hocr", "application/json")
    analyzer = args.get("analyzer")
    pre_processing = args.get("preprocessing")
    force_ocr = args.get("force_ocr")

    if analyzer:
        json_fs_dao = JSONFSDAO(ANALYZER_PATH)
        if analyzer not in list(json_fs_dao.all()):
            logger.warning(
                'Analyzer {anal} not anymore available. Extraction will be performed without considering '
                'it.'.format(
                    anal=analyzer))
            analyzer = None

    if pre_processing:

        json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)

        if pre_processing not in list(json_fs_dao.all()):
            logger.warning(
                "Pre-processing {preproc} not anymore available. Extraction will be performed without considering it.".format(
                    preproc=pre_processing))
            pre_processing = None

    params = dict(force_ocr=str(force_ocr).lower(), analyzer_configs=analyzer,
                  preprocessing_configs=pre_processing,
                  # postprocessing_configs=post_processing
                  )

    configs = get_configurations_files(params)
    logger.debug("selected config: %s", configs)

    if isinstance(file, list):
        file = file[0]

    logger.debug("HOCR on file %s" % file.name)

    output = await hocr_extract_file(file=file, output=accept_ct, configs=configs)
    # output = hocr(file.body, ct=magic.from_buffer(file.body, mime=True))
    # print(output.getvalue())
    # ret = response_converter([el async for el in output], accept)

    if accept_ct == "application/pdf":
        original_ext = file.name.split('.')[-1].lower()
        if original_ext != ".pdf":
            headers = {'Content-Disposition': 'attachment; filename="{}.pdf"'.format(file.name)}
        else:
            headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file.name)}
        return sanic.response.raw(output.getvalue(), headers=headers)

    return sanic.response.json(output)


@app.post("/loko_settings")
@openapi.tag('loko')
@openapi.summary(' ')
@extract_value_args()
async def settings2(value, args):

    settings_type = args.get("settings_type")



    if settings_type == "Pre-Processing":

        dpi = int(float(args.get("dpi")))
        name = args.get("new_preprocessing_name")
        zoom_level = args.get("zoom_level")
        zoom_level = float(zoom_level) if zoom_level else None
        interpolation_mode = args.get("interpolation_mode")
        interpl_mode = int(interpolation_mode.split(":")[0]) if interpolation_mode else None

        logger.debug("creating pre-processing...")

        params = dict(dpi=dpi,
                      zoom_level=zoom_level,
                      interpolation_mode=interpl_mode)

        logger.debug("saving pre-processing %s" % (name))
        logger.debug("preprocessing_")
        data = PreprocessingRequest(**params).__dict__
        logger.debug("pre-processing initialized")
        json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
        json_fs_dao.save(data, name)
        logger.debug("pre-processing saved")

        return sanic.response.json("pre-processing configuration saved as '%s'" % name)


    elif settings_type == "Analyzer":

        vocab_name = None
        patterns_name = None
        oem_type = args.get("oem_type")
        psm_type = args.get("psm_type")
        name = args.get("new_analyzer_name")
        whitelist = args.get("whitelist")
        blacklist = args.get("blacklist")
        lang = args.get("lang")
        patterns_file = args.get("patterns_file")
        vocab_file = args.get("vocab_file")




        logger.debug("creating analyzer...")
        oem = int(oem_type.split(":")[0])
        psm = int(psm_type.split(":")[0])
        lang = lang if lang != "auto" else None
        if vocab_file != "":
            logger.debug("creating vocabulary file")
            vocab_name = "vocab_" + name + "_anal"
            v_data = loko_cli.read(vocab_file["path"])
            v_data = ','.join(v_data.split('\n'))
            logger.debug("saving file %s (type %s)" % (name, type))
            path = VOCABULARY_PATH
            txt_fs_dao = TXTFSDAO(path)
            data = v_data
            data = '\n'.join(data[0].split(','))
            txt_fs_dao.save(data, name)
            logger.debug("file saved")



        if patterns_file != "":
            logger.debug("creating patterns file")
            patterns_name = "patterns_" + name + "_anal"
            p_data = loko_cli.read(patterns_file["path"])
            p_data = ','.join(p_data.split('\n'))
            path = PATTERNS_PATH
            txt_fs_dao = TXTFSDAO(path)
            data = p_data
            data = '\n'.join(data[0].split(','))
            txt_fs_dao.save(data, name)
            logger.debug("file saved")

        params = dict(oem=oem, psm=psm, lang=lang, whitelist=whitelist,
                      blacklist=blacklist, vocab_file=vocab_name, patterns_file=patterns_name)
        params = {k: v for k, v in params.items() if v != "" and v != None}
        print("PARAMS", params)
        logger.debug(params)
        data = AnalyzerRequest(**params).__dict__
        logger.debug("analyzer initialized")
        json_fs_dao = JSONFSDAO(ANALYZER_PATH)
        json_fs_dao.save(data, name)
        logger.debug("analyzer saved")

        return sanic.response.json("analyzer configuration saved as '%s'" % name)

@app.post("/loko_delete_settings")
@openapi.tag('loko')
@openapi.summary(' ')
@extract_value_args()
async def settings(value, args):

    logger.debug(("ARGS",args))

    aname = args.get("analyzer_name_delete")
    pname = args.get("preproc_name_delete")

    ret_anal = ""
    ret_preproc = ""

    if aname:
        logger.debug("analyzer to delete: %s" % aname)
        json_fs_dao = JSONFSDAO(ANALYZER_PATH)


        if aname in list(json_fs_dao.all()):
            json_fs_dao.remove(aname)
            logger.debug(ret_anal)
            vocab_name = "vocab_" + aname + "_anal"

            txt_fs_dao = TXTFSDAO(VOCABULARY_PATH)

            if vocab_name in list(txt_fs_dao.all()):
                txt_fs_dao.remove(vocab_name)
                logger.debug(vocab_name)

            patterns_name = "patterns_" + aname + "_anal"

            txt_fs_dao = TXTFSDAO(PATTERNS_PATH)

            if patterns_name in list(txt_fs_dao.all()):
                txt_fs_dao.remove(patterns_name)
                logger.debug(patterns_name)
            ret_anal="analyzer deleted {}".format(aname)
        else:
            ret_anal = "analyzer configuration '{anal}' already deleted".format(anal=aname)

    if pname:

        json_fs_dao = JSONFSDAO(PREPROCESSING_PATH)
        if pname in list(json_fs_dao.all()) :
            json_fs_dao.remove(pname)
            ret_preproc = "preprocessing deleted {}".format(pname)
        else:
            ret_preproc = "preprocessing configuration '{}' already deleted".format(
                pname)

    if not aname and not pname:
        return sanic.response.json("No Configuration to delete specified... Select at least one analyzer/preprocessor")
    ret = "None"
    if ret_anal != "":
        if ret_preproc != "":
            ret = ret_anal + "; " + ret_preproc
        else:
            ret = ret_anal
    else:
        if ret_preproc != "":
            ret = ret_preproc

    return sanic.response.json(ret)


app.blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, single_process=True)

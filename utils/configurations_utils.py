from ds4biz_textractor.config.app_config import PREPROCESSING_PATH, ANALYZER_PATH, POSTPROCESSING_PATH, VOCABULARY_PATH, \
    PATTERNS_PATH
from ds4biz_textractor.dao.file_system_dao import JSONFSDAO, TXTFSDAO
from ds4biz_textractor.utils.logger_utils import logger

PATHS_MAPPING = dict(preprocessing=PREPROCESSING_PATH,
                     analyzer=ANALYZER_PATH,
                     postprocessing=POSTPROCESSING_PATH)

def get_configurations_files(args: dict):
    res = {}
    for config, path in PATHS_MAPPING.items():
        config_name = args.get(config+'_configs')
        if config_name:
            json_fs_dao = JSONFSDAO(path)
            config_name = config_name
            if not config_name in json_fs_dao.all():
                raise Exception("'%s' %s configuration does not exist!")
            else:
                res[config+'_configs'] = json_fs_dao.get_by_id(config_name)
    return res


def save_users_file_from_txt(filepath, type, name):
    logger.debug("saving external file %s as volume file %s (type %s)" % (filepath, name, type))
    path = get_type_path(type)
    txt_fs_dao = TXTFSDAO(path)
    with open(filepath, "r") as f:
        data = f.read()
    txt_fs_dao.save(data, name)
    logger.debug("file saved")
    return "%s type file saved as '%s'" % (type, name)

def get_type_path(type: str):
    types = ["vocabulary", "patterns"]
    if type not in types:
        raise Exception('type must be in %s' % str(types))
    return VOCABULARY_PATH if type == 'vocabulary' else PATTERNS_PATH
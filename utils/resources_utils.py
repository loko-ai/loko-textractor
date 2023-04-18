import json

import pkg_resources
from loguru import logger


def get_resource(fname: str = "", package: str = "resources"):
    fullname = pkg_resources.resource_filename("ds4biz_textractor." + package,
                                               fname)  # f"resources/{fname}")  # @Undefined
    return fullname


def get_secret(secret_name: str):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            value = secret_file.read()
            value = json.loads(value)
    except Exception as inst:
        logger.warn(f"can't find secrets with name {secret_name}")
        value = {}
    finally:
        return value

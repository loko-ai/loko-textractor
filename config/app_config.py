import os

from loguru import logger
from utils.config_utils import EnvInit

logger.info("starting creating config...")

SUPPORTED_EXT = ["jpg", "pdf", "csv", "doc", "docx", "eml", "epub", "gif", "htm", "html",
                 "json", "log", "mp3", "msg", "odt", "ogg", "pptx", "ps", "psv", "png", "jpg", "jpeg",
                 "rtf", "tff", "tif", "tiff", "tsv", "txt", "wav", "xls", "xlsx", "p7m",
                 "p7s"]

e = EnvInit()

PORT = e.get("PORT", 8080)
REPO_PATH = "../repo"
PREPROCESSING_PATH = os.path.join(REPO_PATH, "preprocessing")
ANALYZER_PATH = os.path.join(REPO_PATH, "analyzer")
POSTPROCESSING_PATH = os.path.join(REPO_PATH, "postprocessing")
PATTERNS_PATH = os.path.join(REPO_PATH, "patterns")
VOCABULARY_PATH = os.path.join(REPO_PATH, "vocabulary")
PROCESS_WORKERS = e.get("PROCESS_WORKERS", 4)
os.makedirs(PREPROCESSING_PATH, exist_ok=True)
os.makedirs(ANALYZER_PATH, exist_ok=True)
os.makedirs(POSTPROCESSING_PATH, exist_ok=True)
os.makedirs(PATTERNS_PATH, exist_ok=True)
os.makedirs(VOCABULARY_PATH, exist_ok=True)
logger.info("done creating config...")
GATEWAY = os.environ.get("GATEWAY", 'http://localhost:9999')
GATEWAY = f"{GATEWAY}/routes"

DPI_DEFAULT = int(os.environ.get('DPI_DEFAULT', '200'))
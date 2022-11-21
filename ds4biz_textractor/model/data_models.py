from typing import List

from ds4biz_textractor.utils.logger_utils import logger


class PreprocessingRequest:
    def __init__(self, zoom_level: float = None, resize_dim: tuple = None, interpolation_mode: int = None, dpi: int = None):
        self.resize_zoom = zoom_level
        # self.resize_dim = resize_dim
        self.interpolation_mode = interpolation_mode
        self.dpi = dpi
        logger.debug("preproocessing configs: %s" % self.__dict__)


class AnalyzerRequest:
    def __init__(self,
                 vocab_file: str = None,
                 patterns_file: str = None,
                 lang: str = None,
                 psm: int = None,
                 oem: int = None,
                 whitelist: str = None,
                 blacklist: str = None):
        self.vocab_file = vocab_file
        self.patterns_file = patterns_file
        self.lang = lang
        self.psm = psm
        self.oem = oem
        self.whitelist = whitelist
        self.blacklist = blacklist


class PostprocessingRequest:
    def __init__(self):
        pass


class SingleEvaluateResponse:
    def __init__(self, min: float, max: float, mean: float):
        self.min = float(min)
        self.max = float(max)
        self.mean = float(mean)


class EvaluateResponse:
    def __init__(self, distance: SingleEvaluateResponse, ratio: SingleEvaluateResponse):
        self.distance = distance
        self.ratio = ratio


class BB:
    def __init__(self, text, top, left, w, h, line):
        self.text = text
        self.top = top
        self.left = left
        self.w = w
        self.h = h
        self.line = line

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def merge(self, other):
        return BB(self.text + " " + other.text, self.top, self.left, self.w + other.w, self.h + other.h, self.line)

    def end(self):
        return self.left + self.w

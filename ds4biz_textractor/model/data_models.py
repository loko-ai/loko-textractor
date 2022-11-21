from typing import List

from ds4biz_textractor.utils.logger_utils import logger


class PreprocessingRequest:
    def __init__(self, zoom_level: List[str] = None, resize_dim: tuple = None, interpolation_mode: List[str] = None, dpi: List[str] = None):
        self.resize_zoom = float(zoom_level[0]) if zoom_level else None
        # self.resize_dim = resize_dim
        self.interpolation_mode = int(interpolation_mode[0]) if interpolation_mode else None
        self.dpi = int(dpi[0]) if dpi else None
        logger.debug("preproocessing configs: %s" % self.__dict__)


class AnalyzerRequest:
    def __init__(self,
                 vocab_file: List[str] = None,
                 patterns_file: List[str] = None,
                 lang: List[str] = None,
                 psm: List[str] = None,
                 oem: List[str] = None,
                 whitelist: List[str] = None,
                 blacklist: List[str] = None):
        self.vocab_file = vocab_file[0] if vocab_file else None
        self.patterns_file = patterns_file[0] if patterns_file else None
        self.lang = lang[0] if lang else None
        self.psm = int(psm[0]) if psm else None
        self.oem = int(oem[0]) if oem else None
        self.whitelist = whitelist[0] if whitelist else None
        self.blacklist = blacklist[0] if blacklist else None


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

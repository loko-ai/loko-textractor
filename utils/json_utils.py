import json
import typing

from utils.logger_utils import logger


class StreamString:
    def __init__(self,parts):
        self.parts=parts

async def stream_json(obj,):
    if isinstance(obj, StreamString):
        yield '"'
        async for part in obj.parts:
            yield json.dumps(part)[1:-1]
        yield '"'
        return

    if isinstance(obj, dict):
        yield "{"
        for i,(k,v) in enumerate(obj.items()):
            yield json.dumps(k)
            yield ":"
            async for el in stream_json(v):
                yield el
            if i!=len(obj)-1:
                yield ","
        yield "}"
    elif isinstance(obj, (list,tuple,range,typing.Generator)):
        yield "["
        start=True

        for v in obj:
            if not start:
                yield ","
            else:
                start=False
            async for el in stream_json(v):
                yield el
        yield "]" 
    elif isinstance(obj, typing.AsyncGenerator):
        logger.debug("async")
        yield "["
        start=True

        async for v in obj:
            if not start:
                yield ","
            else:
                start=False
            async for el in stream_json(v):
                yield el
                
        yield "]"
                
    else:
        yield json.dumps(obj)



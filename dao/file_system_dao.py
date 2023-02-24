import json
import os
from pathlib import Path


class FileSystemDAO:

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self.path = path

    def save(self, obj, name):
        raise Exception("not implemented")

    def all(self):
        return os.listdir(self.path)

    def get_by_id(self, name):
        raise Exception("not implemented")

    def remove(self, name):
        raise Exception("not implemented")


class JSONFSDAO(FileSystemDAO):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def save(self, obj, blueprint_identifier):
        fname = blueprint_identifier
        with open(self.path / fname , "w") as jf:
            json.dump(obj, jf, indent = 2)

    def get_by_id(self, blueprint_identifier):
        fname = blueprint_identifier
        with open(self.path / fname, "r") as jf:
            j = json.load(jf)
        return j

    def remove(self, blueprint_identifier):
        fname = blueprint_identifier
        os.remove(self.path / fname)


class TXTFSDAO(FileSystemDAO):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def save(self, obj, file_name):
        with open(self.path / file_name , 'w') as f:
            f.write(obj)

    def get_by_id(self, file_name):
        fname = file_name
        with open(self.path / fname, 'r') as f:
            content = f.read()
        return content

    def remove(self, file_name):
        fname = file_name
        os.remove(self.path / fname)


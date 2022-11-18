import os
import ast
import json
import inspect
import functools
from typing import Dict
from inspect import Parameter
from abc import abstractmethod


def multiple_keys(d, keys):
    ret = d
    for k in keys:
        ret = ret[k]
    return ret


def find_file(name: str, path=".", recursive=True):
    """It returns the absolute path of a file. If recursive is True it searches in all the parents directories"""
    p = os.path.join(path, name)
    if os.path.exists(p):
        return p
    else:
        if recursive and path != "/":
            return find_file(name, os.path.dirname(os.path.abspath(path)))
        else:
            raise FileNotFoundError("File %s not found (in parent directories)" % name)


class Observable(object):

    def __init__(self, *observers):
        self.observers = list(observers)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify(self, msg):
        for o in self.observer:
            try:
                o(msg)
            except Exception as inst:
                logger.exception(inst)


def guess_convert(s):
    if s is None:
        return None
    try:
        value = ast.literal_eval(s)
    except Exception:
        return s
    else:
        return value


class Init(object):
    def __getattr__(self, k):
        return self.get(k, None)

    @abstractmethod
    def get(self, k, default=None):
        pass


class DictInit(Init):
    def __init__(self, data):
        self.data = data

    def get(self, k, default=None):
        try:
            return multiple_keys(self.data, k.split("."))
        except:
            return default


class EnvInit(Init):
    def __init__(self, conv=guess_convert):
        self.conv = conv

    def get(self, k, default=None):
        temp = os.environ.get(k, default)
        if self.conv:
            temp = self.conv(temp)
        return temp


class JsonInit(Init):
    def __init__(self, path):
        self.path = path
        self.data = {}
        self._reload()

    def _reload(self):
        if os.path.exists(self.path):
            with open(self.path) as o:
                self.data = json.load(o)

    def get(self, k, default=None):
        try:
            return multiple_keys(self.data, k.split("."))
        except:
            return default


class PropertiesInit:
    def __init__(self, path, default):
        self.path = path
        self.default = default

    def __getattr__(self, k):
        pass


class CompositeInit(Init):
    def __init__(self, *configs):
        self.configs = configs

    def get(self, k, default=None):
        for c in self.configs:
            temp = c.get(k)
            if temp:
                return temp
        return None


class Configurator:
    def __init__(self, initializer):
        self.initializer = initializer
        self.data = {}
        self.descriptions = {}
        self.notifier = Observable()

    def set(self, key, value):
        if key in self.data:
            self.data[key] = value
            self.notifier((key, value))
        else:
            raise Exception("%s key is not allowed" % key)

    def observe(self, key, fun):
        self.data[key] = None
        self.notifier.add(fun)
        self.set(key, self.initializer.get(key))

    def get(self, key):
        return self.data.get(key)

    def bind(self, name, function):
        args = set()
        for p in inspect.signature(function).parameters.values():
            key = name + "." + p.name
            self.descriptions[name] = getattr(function, "__doc__", "")
            self.data[key] = self.initializer.get(key)
            if not self.data[key] and p.default != Parameter.empty:
                self.data[key] = p.default
            args.add(p.name)

        @functools.wraps(function)
        def temp(**kwargs):
            for k in args:
                if kwargs.get(k) is None:
                    key = name + "." + k
                    kwargs[k] = self.get(key)
            return function(**kwargs)

        return temp

    def __call__(self, name):
        def temp(f):
            return self.bind(name, f)

        return temp

    def dump(self, path):
        with open(path, "w") as o:
            json.dump(self.data, o, indent=2)

    def add_config_services(self, app, path):
        def setvalues(obj: Dict) -> Dict:
            for k, v in obj.items():
                self.set(k, v)
            return self.data

        def get() -> Dict:
            return self.data

        app.add_service(path, get, "GET")
        app.add_service(path, setvalues, "POST")


def default_configurator(path="config/config.json"):
    try:
        path = find_file(path)
        return Configurator(CompositeInit(EnvInit(), JsonInit(path)))
    except Exception as inst:
        return Configurator(CompositeInit(EnvInit()))


if __name__ == "__main__":
    # configs=Configs(EnvConfig())
    # p=ConfigProfile(JsonConfig("prova.json"),EnvConfig())
    # print(p.CIAO)
    # os.environ['tt.PATH']="Ciccio"

    e = default_configurator()


    # e.b=50
    # e.PYTHONPATH=100

    @e("tt")
    def f(a, b, PATH):
        return PATH, a + b


    e.dump("temp.json")
    print(f(b=20))

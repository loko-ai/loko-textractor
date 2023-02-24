from model.data_models import BB


class RDao:
    def __init__(self, data):
        self.header = data[0]
        self.data = data[1:]

    def all(self):
        for el in self.data:
            try:
                left, top, w, h = [int(x) for x in el[6:10]]
                line = int(el[4])
                if el[-1].strip():
                    yield BB(el[-1].strip(), top, left, w, h, line)
            except:
                pass
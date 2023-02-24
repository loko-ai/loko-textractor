import io

from ds4biz_format_parsers.model.emails import TextEmail


def te2text(te:TextEmail):
    text = io.StringIO()
    text.write(te.subject+"\n")
    text.write("\n".join([el["content"] for el in te.body_parts]))
    text.seek(0)
    return text.read()
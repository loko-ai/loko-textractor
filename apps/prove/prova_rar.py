import os

import rarfile
from loguru import logger

file = open('/home/cecilia/PycharmProjects/ds4biz-textractor/ds4biz_textractor/test/test_resources/Europass.rar', 'rb')

rf = rarfile.RarFile(file.name)
# try:
for fn in rf.infolist():
    ext = os.path.splitext(fn.filename)[-1].lower()
    print(rf.read(fn))
    with open(fn.filename, 'wb') as f:
        f.write(rf.read(fn))
        # new_tmp = tempfile.NamedTemporaryFile(suffix=ext)
        # with open(new_tmp.name, 'wb') as f:
        #     f.write(rf.read(fn))
        # yield {'filename': fn.filename, 'file': new_tmp}
# except Exception as inst:
#     logger.exception(inst)
#     raise Exception("Error: extraction RAR \n" + str(inst))
# finally:
#     file.close()
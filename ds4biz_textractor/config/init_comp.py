from loko_extensions.model.components import Component, save_extensions, Input

c = Component(name="Textract", inputs=[Input(id="file", service="loko_extract")])

save_extensions([c])

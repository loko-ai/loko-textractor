from loko_extensions.model.components import Component, save_extensions, Input, Arg, AsyncSelect, Dynamic, Select, \
    Output

textractor_doc = '''### Description
The TEXTRACT component allows you to use OCR (and HOCR) technologies to extract textual content - from machine-readable documents - images or mixed content. One of TEXTRACT's embedded technologies is Tesseract 4, which offers the possibility to improve the process of recognition of characters and words through the use of an LSTM neural network (as default). If you want, you can also create your own settings and modify both the OCR engine and the pre-processing that must be applied to the input files.

### Input


TEXTRACT has three different input:
- OCR Extraction
- Custom Settings
- Delete Settings
- HOCR Extraction

**OCR Extraction:** generally, a FileReader component must be linked to this input, and the service will directly 
extract the text from the input file. You can set a custom **Analyzer** and **Preprocessing** and choose to receive plain text ("plain/text") representation, 
opt for a JSON format ("application/json") that treats each page separately, or select a streamed JSON format ("application/jsonl"). 
This choice is made in the “Accept” field. 
Accepted file extension: jpeg, docx, pdf, txt, jpg, png, eml.


**Custom Settings:** a trigger must be linked to this input, and using the designed parameters it's possible to create an analyzer or a pre-processing setting. The analyzer will change the OCR parameter,  whilst the pre-processing will change the way in which the file will be "seen" by the OCR engine. Once a setting is created, in order to be used in an extraction you need to specify it in the OCR Extraction parameters.


**Delete Settings:** if you want to delete an already created settings you can link a trigger to this input and specify which settings you want to delete. Warning: this action is permanent. 

**HOCR Extraction:** it receives the same input of the **OCR Extraction**, generally using a FileReader component. 
You can choose to set a custom analyzer and preprocessing to improve the document extraction. The  “Accept” field allows
 to receive the output as "application/json", "text/html" or "application/pdf". 

### Output
The output of the extraction service is a json composed of the key“ text ”and the text extracted from the submitted document as a value.

**OCR Extraction:** the output of this service depends on the type of “accept” chosen: 



- In case *“plain/text”* is chosen, the output will be a plain text which will contains the text extracted from the submitted document. You can see an example below:


```json
"Lorem ipsum Lorem ipsum"
```

- If instead you selected *“application/json”* as accepted value, your output will be a list of jsons. Each json will have the key “filename”, with the name of the examined file as value, and the keys “page” and “text” for each page present in the document examined. The “page” key will have as value an integer number, representing the position (the numeration starts from 0), and the “text” key the extracted text for the relative page. Here an example:

```json
[{ "page": 0, 
"text": "Lorem ipsum Lorem ipsum",
"filename": "file.extension"}],
[{"page": 1, 
 "text": "Lorem ipsum Lorem ipsum", 
 "filename": "file.extension"}],
[{"page": 2, 
 "text": "Lorem ipsum Lorem ipsum",
 "filename": "file.extension"}]
}
```

- The *“application/jsonl”* option returns the same output of the *“application/json”* one but pages are immediately returned when they are extracted.

**HOCR Extraction:** as seen for the OCR, the output of this service depends on the type of “accept” chosen: 


- If “application/json” is selected, the output will consist of a list of JSON objects, each containing the keys “filename,” "content," and "page". The "filename" key will hold the name of the examined file as its value. The "content" key's value will be a list of dictionaries, where each dictionary contains the text and the relative position coordinates. Specifically, the keys contained within each dictionary are "text", "top", "left", "w", "h", and "line". The "page" key will store the relative page number (starting from 0). An example is provided below: 



```json
[{"page":0,
"content":[
    {"text":"Monde","top":596,"left":87,"w":126,"h":26,"line":6},
    {"text":"2°","top":592,"left":190,"w":27,"h":35,"line":6},
    {"text":"ma","top":591,"left":234,"w":63,"h":23,"line":6},
    {"text":"RATA","top":591,"left":417,"w":126,"h":27,"line":6}],
"filename":"filename"},
{ "page":1, 
"content":[
    "text":"Monde","top":596,"left":87,"w":126,"h":26,"line":6},
    {"text":"2°","top":592,"left":190,"w":27,"h":35,"line":6},
    {"text":"ma","top":591,"left":234,"w":63,"h":23,"line":6},
    {"text":"RATA","top":591,"left":417,"w":126,"h":27,"line":6}],
"filename":"filename"},
...
]
```



- If, otherwise, “text/html” is selected, the output format is the same as for "application/json", but the value of the "content" key will be the extracted content in HTML format. Example:


```json
[{"page":0,
"content":"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n <head>\n  <title></title>\n ...",
"filename":"filename"},
{"page":1,
"content":"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n <head>\n  <title></title>\n ...",
"filename":"filename"},
...
]
```


- Finally you can opt for *“application/pdf”*, which will return a pdf file as output.



**Settings:** this output will only be a message which declares the setting creation.



**Delete Settings:** this output will only be a message which declares the setting creation. 


'''

group_ocr_extraction = "OCR Extraction"
group_hocr_extraction = "HOCR Extraction"
group_custom_settings = "Custom Settings"
group_delete_settings = "Delete Settings"

accept_hocr = Select(name="accept_hocr", label="Accept",
                     options=["application/json", "text/html", "application/pdf"],
                     helper="Select an output format, default='application/json'",
                     description="format and content type of the output",
                     value="application/json",
                     group=group_hocr_extraction)

analyzer_hocr = AsyncSelect("analyzer_hocr", label="Analyzer",
                       url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/analyzer",
                       helper="Select an analyzer, if not set the default analyzer settings will be used",
                       description="An analyzer object is compose of different configurations to run the tesseract engine",
                       group=group_hocr_extraction)

pre_processing_hocr = AsyncSelect("preprocessing_hocr", label="Preprocessing",
                             url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/preprocessing",
                             helper="Select a preprocessing, if not set no pre-processing will be done",
                             description="A preprocessing object is compose of different configurations to prepare the input image",
                             group=group_hocr_extraction)

####
force_ocr = Arg("force_ocr", label="Force OCR", type="boolean",
                description="If True, even if the document is machine readable the OCR engine will be used",
                group=group_ocr_extraction, value=False)

analyzer = AsyncSelect("analyzer", label="Analyzer",
                       url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/analyzer",
                       helper="Select an analyzer, if not set the default analyzer settings will be used",
                       description="An analyzer object is compose of different configurations to run the tesseract engine",
                       group=group_ocr_extraction)

pre_processing = AsyncSelect("preprocessing", label="Preprocessing",
                             url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/preprocessing",
                             helper="Select a preprocessing, if not set no pre-processing will be done",
                             description="A preprocessing object is compose of different configurations to prepare the input image",
                             group=group_ocr_extraction)

accept = Select(name="accept", label="Accept",
                options=["application/json", "plain/text", "application/jsonl"],
                helper="Select an output format, default='plain/text'",
                description="format and content type of the output",
                value="application/json",
                group=group_ocr_extraction)
####

settings_type = Select(name="settings_type", label="Settings Type",
                       options=["Analyzer", "Pre-Processing"],  # , "Post-Processing"],
                       group=group_custom_settings,
                       description="You can choose between Analyzer or Preprocessing object in order to create a new custom configuration",
                       helper="Select configuration type"
                       )

new_analyzer_name = Dynamic(name="new_analyzer_name", label="Name",
                            dynamicType="text",
                            parent="settings_type",
                            group="Custom Settings",
                            condition='{parent}==="Analyzer"',
                            helper="Name of the new analyzer")

oem_type = Dynamic(name="oem_type", label="OEM",
                   # options=[0, 1, 2, 3],
                   options=["0: legacy engine only",
                            "1: neural nets LSTM engine only",
                            "2: legacy + LSTM engines",
                            "3: default, based on what is available"],
                   dynamicType="select",
                   parent="settings_type",
                   group="Custom Settings",
                   condition='{parent}==="Analyzer"',
                   helper="OCR Engine Mode to use ",
                   value="1: neural nets LSTM engine only")

psm_type = Dynamic(name="psm_type", label="PSM",
                   # options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                   options=["0: orientation and script detection (OSD) only",
                            "1: automatic page segmentation with OSD",
                            "2: automatic page segmentation, but no OSD, or OCR",
                            "3: fully automatic page segmentation, but no OSD",
                            "4: assume a single column of text of variable sizes",
                            "5: assume a single uniform block of vertically aligned text",
                            "6: assume a single uniform block of text",
                            "7: treat the image as a single text line",
                            "8: treat the image as a single word",
                            "9: treat the image as a single word in a circle",
                            "10: treat the image as a single character",
                            "11: sparse text. Find as much text as possible in no particular order",
                            "12: sparse text with OSD",
                            "13: raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific"],
                   dynamicType="select",
                   parent="settings_type",
                   group="Custom Settings",
                   condition='{parent}==="Analyzer"',
                   helper="Page Segmentation Mode to use",
                   value="1: automatic page segmentation with OSD")

lang = Dynamic(name="lang", label="Language",
               options=["auto", "ita", "eng"],
               dynamicType="select",
               parent="settings_type",
               group="Custom Settings",
               condition='{parent}==="Analyzer"',
               helper="If auto the language will be detected, otherwise you can select italian or english.",
               value="auto")

whitelist = Dynamic(name="whitelist", label="Character Whitelist ",
                    dynamicType="text",
                    parent="settings_type",
                    group="Custom Settings",
                    condition='{parent}==="Analyzer"',
                    helper="Inser characters",
                    description="The only characters that the OCR engine is allowed to recognize. All the characters must be write without separator"
                    )

blacklist = Dynamic(name="blacklist", label="Character Blacklist ",
                    dynamicType="text",
                    parent="settings_type",
                    group="Custom Settings",
                    condition='{parent}==="Analyzer"',
                    helper="Inser characters",
                    description="Characters that must never be included in the results. All the characters must be write without separator")

vocab_file = Dynamic(name="vocab_file", label="Vocabulary File Name",  # cambiare in File
                     dynamicType="files",
                     parent="settings_type",
                     group="Custom Settings",
                     condition='{parent}==="Analyzer"',
                     helper="Select the vocabulary file",
                     description="vocabulary file list of tokens that helps the token recognition process")

patterns_file = Dynamic(name="patterns_file", label="Patterns File Name",
                        dynamicType="files",
                        parent="settings_type",
                        group="Custom Settings",
                        condition='{parent}==="Analyzer"',
                        helper="Select the patterns file",
                        description="Patterns file that helps the token recognition process")

new_preprocessing_name = Dynamic(name="new_preprocessing_name", label="Name",
                                 dynamicType="text",
                                 parent="settings_type",
                                 group="Custom Settings",
                                 condition='{parent}==="Pre-Processing"',
                                 helper="Name of the pre-processing custom settings")

dpi = Dynamic(name="dpi", label="DPI",
              dynamicType="number",
              parent="settings_type",
              group="Custom Settings",
              condition='{parent}==="Pre-Processing"',
              helper="DPI value to use when processing files",
              value="200"
              )

zoom = Dynamic(name="zoom", label="Apply Zoom",
               dynamicType="boolean",
               parent="settings_type",
               group="Custom Settings",
               condition='{parent}==="Pre-Processing"',
               )
zoom_level = Dynamic(name="zoom_level", label="Zoom Level",
                     dynamicType="number",
                     parent="zoom",
                     group="Custom Settings",
                     condition='{parent}===true',
                     helper="If the zoom rate level is set to a lower value than 1.0 the image will be shrinked, otherwise the image will be enlarged",
                     value="1.3")
interpolation_mode = Dynamic(name="interpolation_mode", label="Interpolation Mode",
                             options=["0: INTER_NEAREST",
                                      "1: INTER_LINEAR",
                                      "2: INTER_CUBIC",
                                      "3: INTER_AREA",
                                      "4: INTER_LANCZOS4",
                                      "7: INTER_MAX",
                                      "8: WARP_FILL_OUTLIERS",
                                      "16: WARP_INVERSE_MAP"],
                             dynamicType="select",
                             parent="zoom",
                             group="Custom Settings",
                             condition='{parent}===true',
                             helper="Interpolation algorithm",
                             description="In case of Zoom-In the image will generally look best with INTER_CUBIC mode (slow) or INTER_LINEAR (faster but still looks good);"
                                         " In case of Zoom-Out the mode INTER_AREA generally works better",
                             value="1: INTER_LINEAR")

analyzer_name_delete = AsyncSelect(name="analyzer_name_delete", label="Analyzer Settings Name",
                                   # parent="settings_type",
                                   url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/analyzer",
                                   group="Delete Settings",
                                   helper="Name of the custom settings you want to delete")

preproc_name_delete = AsyncSelect(name="preproc_name_delete", label="Pre-Processing Settings Name",
                                  # parent="settings_type",
                                  url="http://localhost:9999/routes/loko-textractor/ds4biz/textract/0.1/preprocessing",
                                  group="Delete Settings",
                                  # condition='{settings_type_d}==="Analyzer"',
                                  helper="Name of the custom settings you want to delete")

####

args = [force_ocr, analyzer, pre_processing, accept, settings_type, new_analyzer_name, oem_type, psm_type, lang,
        whitelist, blacklist,
        vocab_file, patterns_file, new_preprocessing_name, dpi, zoom, zoom_level, interpolation_mode,
        analyzer_name_delete, preproc_name_delete, analyzer_hocr, pre_processing_hocr, accept_hocr]

inputs = [Input(id="ocr_extraction", service="loko_extract", to="ocr_extraction"),
          Input(id="hocr_extraction", service="loko_hocr", to="hocr_extraction"),
          Input(id="settings", service="loko_settings", to="settings"),
          Input(id="delete_settings", service="loko_delete_settings", to="delete_settings")]
outputs = [Output(id="ocr_extraction"), Output(id="hocr_extraction"), Output(id="settings"),
           Output(id="delete_settings")]
c = Component(name="Textract", inputs=inputs, outputs=outputs, args=args, description=textractor_doc,
              icon="RiBubbleChartLine")

save_extensions([c])

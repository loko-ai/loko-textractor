<html><p><a href="https://loko-ai.com/" target="_blank" rel="noopener"> <img style="vertical-align: middle;" src="https://user-images.githubusercontent.com/30443495/196493267-c328669c-10af-4670-bbfa-e3029e7fb874.png" width="8%" align="left" /> </a></p>
<h1>Loko - Textractor</h1><br></html>


 **Textractor** is a Loko extension which enables the use of OCR technologies to extract textual content - from 
 machine-readable documents - images or mixed type content. 
 
One of the embedded technologies of Textractor is Tesseract 4 which offers the possibility to improve the process of 
character and word recognition through the use of an LSTM neural network (as default). 

You can also create your own settings and modify both the OCR engine and the pre-processing that must be applied to the 
input files.

You can drag and drop the component and use it in your flow:

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/232799223-be7a7999-25d7-4cad-8a2c-63736ca4db8a.png" width="80%" /></p>

### OCR Extraction

Generally, a **FileReader** component must be linked to this input and the service will directly extract the text from 
the input file. You can set a custom **Analyzer** and **Preprocessing** and decide if you need the output as plain text 
("plain/text") or in a json format ("application/json") which will treat each page seperately by selecting in the 
**Accept** field the format which suits you the most: this parameter changes your 
output type. Accepted file extension: pdf, txt, jpg, jpeg, png, tif, eml, p7m, rar, zip, docx. 

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/232800113-dca8fd74-1ef6-4b92-8245-a47d6858666b.png" width="80%" /></p>

### hOCR Extraction

You can use hOCR to include bounding boxes information to your output. The output format options are: 
"application/json", "text/html".

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/232806746-10ab7af8-56c7-423d-a0a7-7a1d0fcbf765.png" width="80%" /></p>

### Settings

A **Trigger** component must be linked to this input. Using the designed parameters it's possible to create an analyzer or a 
pre-processing setting. The analyzer will change the OCR parameter whilst the pre-processing will change the way in 
which the file will be "seen" by the OCR engine. Once a setting is created, you need to specify it in the OCR 
Extraction parameters in order to be used in an extraction. 

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/232810811-65cc009c-9ae3-43f4-9211-f5f24e490610.png" width="80%" /></p>

### Delete settings

If you want to delete an already created setting you can link a **Trigger** component to this input and specify which 
settings you want to delete.

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/232812266-dbd47786-8852-481e-be94-c6dc73a9c273.png" width="80%" /></p>



## Configuration

In the file *config.json* you can configure environment variables and volumes: 

```
{
  "main": {
    "volumes": [
      "/var/opt/loko/loko-textractor:/plugin/repo"
    ],
    "environment": {
      "DPI_DEFAULT": 200,
      "PROCESS_WORKERS": 1,
      "SANIC_REQUEST_MAX_SIZE": 500000000,
      "SANIC_REQUEST_TIMEOUT": 3600,
      "SANIC_RESPONSE_TIMEOUT": 3600
    }
  }
}
```
FROM python:3.10-slim as builder
ARG user
ARG password
RUN apt-get update --fix-missing && apt-get install -y gcc tesseract-ocr wget libmagic-dev ffmpeg libsm6 libxext6 && rm -rf /var/cache/apt
RUN rm /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/ita.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
ADD requirements.lock /
RUN pip install --upgrade -r /requirements.lock
RUN python -m nltk.downloader punkt
ADD . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
WORKDIR /plugin/services
ENV OMP_THREAD_LIMIT=1
ENV SANIC_REQUEST_TIMEOUT=300
ENV SANIC_ACCESS_LOG=False
ENV PROCESS_WORKERS=1
ENV SANIC_REQUEST_MAX_SIZE=500000000
## request timeout 1h
ENV SANIC_REQUEST_TIMEOUT=3600
## response timeout 1h
ENV SANIC_RESPONSE_TIMEOUT=3600
EXPOSE 8080
ENV PYTHONBUFFERED=1
CMD python -u textractor_services.py
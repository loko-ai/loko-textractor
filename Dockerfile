FROM python:3.10-slim as builder
ARG user
ARG password
# RUN apt update && apt install -y tesseract-ocr wget
RUN apt-get update --fix-missing && apt-get install -y gcc tesseract-ocr wget libmagic-dev ffmpeg libsm6 libxext6 && rm -rf /var/cache/apt
RUN rm /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/ita.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
ADD requirements.lock /
RUN pip install --upgrade -r /requirements.lock
RUN python -m nltk.downloader punkt
# RUN pip install gunicorn uvicorn && ln -s /usr/local/bin/gunicorn /usr/bin/gunicorn && ln -s /usr/local/bin/uvicorn /usr/bin/uvicorn
# FROM python:3.7-slim
# COPY --from=builder /root/.local /root/.local
ADD . /ds4biz-textractor
ENV PYTHONPATH=$PYTHONPATH:/ds4biz-textractor:/root/.local/lib/python3.7/site-packages
WORKDIR /ds4biz-textractor/ds4biz_textractor/services
ENV OMP_THREAD_LIMIT=1
ENV SANIC_REQUEST_TIMEOUT=300
# ENV REQUEST_TIMEOUT=300
ENV SANIC_ACCESS_LOG=False
ENV WORKERS=1
ENV PROCESS_WORKERS=1
EXPOSE 8080
## request max size 500MB
ENV SANIC_REQUEST_MAX_SIZE=500000000
## request timeout 1h
ENV SANIC_REQUEST_TIMEOUT=3600
## response timeout 1h
ENV SANIC_RESPONSE_TIMEOUT=3600
EXPOSE 8080
CMD python -m sanic ds4biz_textractor.services.textractor_services.app --host=0.0.0.0 --port=8080 --workers=$WORKERS
# CMD gunicorn ds4biz_textractor.services.textractor_services:app -b 0.0.0.0:8080 -w $WORKERS --timeout $REQUEST_TIMEOUT -k uvicorn.workers.UvicornWorker

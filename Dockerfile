ARG BUILD_LANG=python
ARG BUILD_LANG_VER=3.10.7
ARG BUILD_TAG=slim-buster

ARG BUILD_IMAGE_TAGNAME=${BUILD_LANG}:${BUILD_LANG_VER}-${BUILD_TAG}

FROM $BUILD_IMAGE_TAGNAME

ENV APPHOME=/apps
ENV REQ_TXT=requirements.txt

RUN mkdir -p ${APPHOME} && chmod 777 ${APPHOME}
COPY . ${APPHOME}/
WORKDIR ${APPHOME}

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install ffmpeg -y && \
    pip3 install -r $REQ_TXT

VOLUME ${APPHOME}

CMD ls && alembic upgrade head ; python3 -u main.py

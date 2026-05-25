ARG BUILD_LANG=python
ARG BUILD_LANG_VER=3.13.13
ARG BUILD_TAG=slim

ARG BUILD_IMAGE_TAGNAME=${BUILD_LANG}:${BUILD_LANG_VER}-${BUILD_TAG}

FROM $BUILD_IMAGE_TAGNAME

ENV APPHOME=/apps
ENV REQ_TXT=requirements.txt
ENV PLUGIN_REQ_TXT=plugin-requirements.txt

RUN mkdir -p ${APPHOME} && chmod 777 ${APPHOME}
COPY . ${APPHOME}/
WORKDIR ${APPHOME}

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install ffmpeg -y && \
    pip3 install -r $REQ_TXT

RUN if [ -f $PLUGIN_REQ_TXT ]; then \
        echo "Running plugin requirements..."; \
        pip3 install -r $PLUGIN_REQ_TXT; \
    else \
        echo "Plugin requirements does not exist. Skipping."; \
    fi

VOLUME ${APPHOME}

CMD alembic upgrade head ; python3 -u main.py

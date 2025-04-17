ARG BUILD_LANG=python
ARG BUILD_LANG_VER=3.10.7
ARG BUILD_TAG=slim-buster

ARG BUILD_IMAGE_TAGNAME=${BUILD_LANG}:${BUILD_LANG_VER}-${BUILD_TAG}

FROM $BUILD_IMAGE_TAGNAME

ENV APPHOME=/apps
ENV REQ_TXT=requirements.txt
ENV USE_SQLITE=false

RUN mkdir -p $APPHOME
COPY . $APPHOME
WORKDIR $APPHOME

RUN apt-get update && \
    apt-get install ffmpeg -y && \
    pip3 install -r $REQ_TXT

RUN if [ "$USE_SQLITE" = "true" ]; then apt-get install sqlite3=3.* libsqlite3-dev -y && /usr/bin/sqlite3 magi.db ; fi

VOLUME [ APPHOME ]

CMD [ "alembic", "upgrade", "head", ";", "python3", "-u", "./main.py" ]

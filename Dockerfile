FROM ubuntu:18.04

MAINTAINER Yazdan

ENV DOCKYARD_SRC=. DOCKYARD_SRVHOME=/srv

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    python3 python3-pip python3-dev libmysqlclient-dev git libpq-dev && rm -rf /var/lib/apt/lists/*

RUN mkdir $DOCKYARD_SRVHOME/media static logs

VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

COPY . $DOCKYARD_SRVHOME

RUN pip3 install --no-cache-dir --upgrade pip setuptools && pip install --no-cache-dir ez_setup \
    && pip3 install --no-cache-dir -r $DOCKYARD_SRVHOME/requirements.txt

EXPOSE 8080

WORKDIR $DOCKYARD_SRVHOME
COPY ./docker-entrypoint.sh /
RUN ["chmod", "+x", "/docker-entrypoint.sh"]
ENTRYPOINT ["/docker-entrypoint.sh"]

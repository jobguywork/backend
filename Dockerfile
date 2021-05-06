FROM ubuntu:18.04

MAINTAINER Yazdan


ENV DOCKYARD_SRC=.

ENV DOCKYARD_SRVHOME=/srv

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y git

# WORKDIR $DOCKYARD_SRVHOME
RUN mkdir $DOCKYARD_SRVHOME/media static logs

VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

COPY . $DOCKYARD_SRVHOME

RUN pip3 install -r $DOCKYARD_SRVHOME/requirements.txt

EXPOSE 8080

WORKDIR $DOCKYARD_SRVHOME
COPY ./docker-entrypoint.sh /
RUN ["chmod", "+x", "/docker-entrypoint.sh"]
ENTRYPOINT ["/docker-entrypoint.sh"]
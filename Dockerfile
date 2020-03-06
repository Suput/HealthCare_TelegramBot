FROM ubuntu:16.04

COPY requirements.txt /

RUN apt-get update && \
    apt-get install -y sudo python3  python3-pip  python3-dev

RUN pip3 install -r /requirements.txt

RUN sudo apt-get -y update

RUN sudo apt-get -y upgrade

COPY app/ /app

WORKDIR /app

CMD [ "./run.sh" ]
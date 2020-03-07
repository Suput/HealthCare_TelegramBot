FROM python:3

COPY ./requirements.txt /app/requirements.txt
COPY ./bot.py /app/bot.py

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD python bot.py

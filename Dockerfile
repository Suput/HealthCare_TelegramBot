FROM python:3

WORKDIR /app

COPY ./requirements.txt /

RUN pip install -r requirements.txt

COPY ./app/bot.py /

CMD python bot.py

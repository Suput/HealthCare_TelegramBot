FROM python:3

COPY requirements.txt /app/
COPY bot.py /app/

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD python bot.py

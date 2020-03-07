FROM python:3

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# COPY app/bot.py /

CMD python app/bot.py

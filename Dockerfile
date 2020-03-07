FROM python:3

WORKDIR /app

COPY HealthCare_TelegramBot/requirements.txt /

RUN pip install -r requirements.txt

COPY HealthCare_TelegramBot/app/bot.py /

CMD python bot.py

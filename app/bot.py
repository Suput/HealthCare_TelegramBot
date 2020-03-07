from telegram.ext import MessageHandler, Filters, Updater
import logging
from signal import signal, SIGINT
import requests
from datetime import datetime as dt
from hashlib import sha256
from json import dumps, load
from re import match


BOT_TOKEN = None
URL = None


def get_token():
    global BOT_TOKEN
    if BOT_TOKEN is None:
        with open("appsettings.json") as f:
            res = load(f)
            BOT_TOKEN = res["token"]
    return BOT_TOKEN


def get_url():
    global URL
    if URL is None:
        with open("appsettings.json") as f:
            res = load(f)
            URL = res["url"]
    return URL


def check_input(text: str):
    parsed_text = match(r"^[0-9]{2,3}/[0-9]{2,3} [0-9]{2,3}$", text)
    if parsed_text is None:
        return False
    return True


def save_info(update, context):
    logger.info("Data recieved: " + update.message.text)
    if not check_input(update.message.text):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error parsing value"
        )
        logger.warning("Error parsing value\n")
        return
    data = update.message.text.split()
    data = [
        int(data[0].split("/")[0]),
        int(data[0].split("/")[1]),
        int(data[1])
    ]
    logger.info("Data parsed: " + data)
    time_now = str(dt.now().isoformat())
    # with open("data.txt", "a") as f:
    #     f.write(f"{data[0]},{data[1]},{data[2]},{time_now}\n")

    # Make request
    url = get_url() + "/api/user"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "TelegramUserId": update.effective_user.id,
        "Sys": data[0],
        "Dia": data[1],
        "Pulse": data[2],
        "DateTime": time_now,
        "Token": str(sha256(get_token().encode()).hexdigest())
    }

    request = requests.post(
        url=url,
        data=dumps(data),
        headers=headers
    )
    logger.info(request.text)
    logger.info(request.status_code)

    if request.status_code != 200:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error while saving data"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ok"
        )
    return


updater = Updater(token=get_token(), use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler(Filters.text, save_info))

# logger configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Ctrl+C handler
def catch_ctrl_c(signal, frame):
    logger.info("Stopping Bot!")
    updater.stop()
    updater.is_idle = False
    logger.info("Bot stopped!")


signal(SIGINT, catch_ctrl_c)

updater.start_polling()
logger.info("Bot started!")
updater.idle()
logger.info("Bot stopped!")

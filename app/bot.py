from telegram.ext import MessageHandler, Filters, Updater, CommandHandler
import logging
from signal import signal, SIGINT
import requests
from datetime import datetime as dt
from hashlib import sha256
from json import dumps, load, loads
from re import match
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


BOT_TOKEN = None
URL = None


def get_token():
    global BOT_TOKEN
    if BOT_TOKEN is None:
        with open("appsettings.json") as f:
            res = load(f)
            BOT_TOKEN = res["token"]
    return BOT_TOKEN


def get_sha_token():
    return str(sha256(get_token().encode()).hexdigest())


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


def draw_image(syss, dias, pulses):
    image = Image.new("RGB", (600, 600), (230, 230, 230))
    draw = ImageDraw.Draw(image)

    font16 = ImageFont.truetype("font.ttf", size=16)
    font11 = ImageFont.truetype("font.ttf", size=11)

    BLUE_COLOR = (0, 0, 240)
    PINK_COLOR = (240, 20, 100)

    PULSE_LINE = 540
    draw.text((0, PULSE_LINE - 17), "pulse", BLUE_COLOR, font=font16)
    draw.text((580, PULSE_LINE - 17), "60", BLUE_COLOR, font=font16)
    draw.line((0, PULSE_LINE, 600, PULSE_LINE), BLUE_COLOR, width=1)

    DIA_LINE = 350
    draw.text((0, DIA_LINE - 17), "dia", BLUE_COLOR, font=font16)
    draw.text((580, DIA_LINE - 17), "80", BLUE_COLOR, font=font16)
    draw.line((0, DIA_LINE, 600, DIA_LINE), BLUE_COLOR, width=1)

    SYS_LINE = 170
    draw.text((0, SYS_LINE - 17), "sys", BLUE_COLOR, font=font16)
    draw.text((575, SYS_LINE - 17), "120", BLUE_COLOR, font=font16)
    draw.line((0, SYS_LINE, 600, SYS_LINE), BLUE_COLOR, width=1)

    step = 600 // len(syss)
    k = 0

    for i in range(0, 600, step):
        next_index = min(k + 1, len(syss) - 1)

        coords = (i, PULSE_LINE + 60 - pulses[k], i + step, PULSE_LINE + 60 - pulses[next_index])
        draw.text((coords[0], coords[1]), str(pulses[k]), PINK_COLOR, font=font11)
        draw.line(coords, fill=PINK_COLOR, width=2)

        coords = (i, DIA_LINE + 80 - dias[k], i + step, DIA_LINE + 80 - dias[next_index])
        draw.text((coords[0], coords[1]), str(dias[k]), PINK_COLOR , font=font11)
        draw.line(coords, fill=PINK_COLOR, width=2)

        coords = (i, SYS_LINE + 120 - syss[k], i + step, SYS_LINE + 120 - syss[next_index])
        draw.text((coords[0], coords[1]), str(syss[k]), PINK_COLOR, font=font11)
        draw.line(coords, fill=PINK_COLOR, width=2)

        k += 1

    bio = BytesIO()
    bio.name = "image.jpg"
    image.save(bio, "jpeg")
    bio.seek(0)
    return bio # image.save("app\\test.png", "PNG")


def save_info(update, context):
    logger.info("User sends info to bot")
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
    logger.info("Data parsed: " + ", ".join([str(elem) for elem in data]))
    time_now = str(dt.now().isoformat())

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
        "Token": get_sha_token()
    }

    request = requests.post(
        url=url,
        data=dumps(data),
        headers=headers
    )
    logger.info("Request text - " + request.text)
    logger.info("Request status code - " + str(request.status_code))

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


def get_info(update, context):
    url = get_url() + "/api/user/" + str(update.effective_user.id)
    url += "/" + get_sha_token()
    response = requests.get(url=url)

    logger.info("Bot receives info from back")
    logger.info("Response text - " + response.text)
    logger.info("Status code - " + str(response.status_code))
    
    if response.status_code != 200:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error while getting data"
        )
        return

    data = loads(response.text)
    answer = "Среднее систолическое: " + "{:.2f}".format(data['averageSys']) + '\n'
    answer += "Среднее диастолическое: " + "{:.2f}".format(data['averageDia']) + '\n'
    answer += "Средний пульс: " + "{:.2f}".format(data['averagePulse']) + '\n'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer
    )

    logger.info("Send image")
    image = draw_image(data['syss'], data['dias'], data['pulses'])
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image
    )


updater = Updater(token=get_token(), use_context=True)
dispatcher = updater.dispatcher

# Handlers
dispatcher.add_handler(CommandHandler("get_info", get_info))
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

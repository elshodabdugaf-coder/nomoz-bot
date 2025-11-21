import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"

def get_times(lat, lon):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
    data = requests.get(url).json()
    return data["data"]["timings"]

def start(update, context):
    update.message.reply_text("Lokatsiya yuboring (📍).")

def location(update, context):
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    times = get_times(lat, lon)

    msg = "Bugungi namoz vaqtlari:\n"
    for k, v in times.items():
        msg += f"{k}: {v}\n"

    update.message.reply_text(msg)

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.location, location))

updater.start_polling()
updater.idle()

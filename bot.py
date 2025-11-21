import requests
import datetime
import time
import threading
from telegram import Bot
from telegram.ext import Updater, CommandHandler

TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"
CHAT_ID = None  # user /start bosganida saqlanadi
bot = Bot(token=TOKEN)

# Namoz vaqtlarini olish funksiyasi
def get_times():
    url = "https://islomapi.uz/api/present/day?region=Toshkent"
    data = requests.get(url).json()
    return data["times"]

namoz_times = get_times()

# Namoz vaqtida xabar yuborish
def check_namoz_times():
    global namoz_times
    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        for name, vakt in namoz_times.items():
            if vakt == now and CHAT_ID:
                bot.send_message(chat_id=CHAT_ID, text=f"⏰ {name} namozi vaqti kirdi!")

        time.sleep(30)

# Har kuni 00:00 da vaqtlarni yangilash
def update_daily():
    global namoz_times
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now == "00:00":
            namoz_times = get_times()
            if CHAT_ID:
                bot.send_message(chat_id=CHAT_ID, text="🗓 Bugungi namoz vaqtlar:\n" + format_times())

        time.sleep(30)

# Formatlash
def format_times():
    t = namoz_times
    return (
        f"Bomdod: {t['tong_saharlik']}\n"
        f"Quyosh: {t['quyosh']}\n"
        f"Peshin: {t['peshin']}\n"
        f"Asr: {t['asr']}\n"
        f"Shom: {t['shom_iftor']}\n"
        f"Xufton: {t['hufton']}"
    )

# /start komandasi
def start(update, context):
    global CHAT_ID
    CHAT_ID = update.message.chat_id
    context.bot.send_message(
        chat_id=CHAT_ID,
        text="Assalomu alaykum! Namoz vaqtlarini kuzatib boraman.\n\n" + format_times()
    )

# Botni ishga tushirish
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    threading.Thread(target=check_namoz_times, daemon=True).start()
    threading.Thread(target=update_daily, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
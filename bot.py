import telebot
from telebot import types
import requests
import threading
import time
from datetime import datetime

BOT_TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"   # <<< TOKEN SHU YERGA KIRITILADI
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}   # {chat_id: {"region": "Tashkent"}}


# ---------- Namoz vaqtlarini olish funksiyasi ----------
def get_namoz_times(region):
    url = f"https://islomapi.uz/api/present/day?region={region}"
    r = requests.get(url).json()
    return r["times"]


# ---------- /start komandasi ----------
@bot.message_handler(commands=['start'])
def start(msg):
    text = (
        "🕌 Assalomu alaykum!\n\n"
        "Men *namoz vaqtlarini eslatib turuvchi botman*.\n"
        "Quyida lokatsiya yuborish tugmasi chiqadi 👇\n"
        "Shu orqali qaysi shaharda ekaningizni bilib sizga namoz vaqtlarini eslata olaman."
    )
    
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)
    kb.add(btn)
    
    bot.send_message(msg.chat.id, text, reply_markup=kb, parse_mode="Markdown")


# ---------- Lokatsiya qabul qilish ----------
@bot.message_handler(content_types=['location'])
def get_location(msg):
    lat = msg.location.latitude
    lon = msg.location.longitude

    # joylashuv orqali shaharni aniqlash
    url = f"https://geocode.xyz/{lat},{lon}?json=1"
    data = requests.get(url).json()

    try:
        region = data["city"]
    except:
        region = "Tashkent"

    user_data[msg.chat.id] = {"region": region}

    times = get_namoz_times(region)

    result = (
        f"🏙 Hudud: {region}\n\n"
        f"Bomdod: {times['tong_saharlik']}\n"
        f"Quyosh: {times['quyosh']}\n"
        f"Peshin: {times['peshin']}\n"
        f"Asr: {times['asr']}\n"
        f"Shom: {times['shom_iftor']}\n"
        f"Xufton: {times['hufton']}\n\n"
        "✔️ Eslatmalar yoqildi!"
    )

    bot.send_message(msg.chat.id, result)


# ---------- Eslatma yuborish funksiyasi ----------
def send_daily_updates():
    while True:
        now = datetime.now().strftime("%H:%M")

        for chat_id, info in user_data.items():
            region = info["region"]
            times = get_namoz_times(region)

            # 00:00 da yangilangan vaqt
            if now == "00:00":
                bot.send_message(chat_id, "🔄 Namoz vaqtlari yangilandi!")
                txt = (
                    f"🏙 Hudud: {region}\n\n"
                    f"Bomdod: {times['tong_saharlik']}\n"
                    f"Quyosh: {times['quyosh']}\n"
                    f"Peshin: {times['peshin']}\n"
                    f"Asr: {times['asr']}\n"
                    f"Shom: {times['shom_iftor']}\n"
                    f"Xufton: {times['hufton']}"
                )
                bot.send_message(chat_id, txt)

            # Namoz eslatmalari
            if now == times['tong_saharlik']:
                bot.send_message(chat_id, "🌅 Bomdod vaqti bo‘ldi!")

            if now == times['peshin']:
                bot.send_message(chat_id, "🌞 Peshin vaqti bo‘ldi!")

            if now == times['asr']:
                bot.send_message(chat_id, "🌤 Asr vaqti bo‘ldi!")

            if now == times['shom_iftor']:
                bot.send_message(chat_id, "🌇 Shom vaqti bo‘ldi!")

            if now == times['hufton']:
                bot.send_message(chat_id, "🌙 Xufton vaqti bo‘ldi!")

        time.sleep(30)  # 30 soniyada bir tekshiradi



# ---------- Eslatma funksiyasini fon rejimida ishga tushiramiz ----------
threading.Thread(target=send_daily_updates, daemon=True).start()


# ---------- Botni ishga tushirish ----------
bot.polling(none_stop=True)
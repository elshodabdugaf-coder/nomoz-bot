import telebot
from telebot import types
import requests
import threading
import time
from datetime import datetime

BOT_TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"   # <<< TOKENNI SHU YERGA YOZASIZ
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}   # {chat_id: {"lat": ..., "lon": ..., "times": {...}}}


# ---------- Namoz vaqtlarini aniq olish (latitude / longitude orqali) ----------
def get_namoz_times_by_coords(lat, lon):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
    r = requests.get(url).json()
    t = r["data"]["timings"]

    return {
        "bomdod": t["Fajr"],
        "quyosh": t["Sunrise"],
        "peshin": t["Dhuhr"],
        "asr": t["Asr"],
        "shom": t["Maghrib"],
        "xufton": t["Isha"]
    }


# ---------- /start komandasi ----------
@bot.message_handler(commands=['start'])
def start(msg):
    text = (
        "🕌 Assalomu alaykum!\n\n"
        "Men namoz vaqtlarini *aniq eslatib turuvchi* botman.\n"
        "👇 Quyidagi tugma orqali lokatsiya yuboring."
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

    times = get_namoz_times_by_coords(lat, lon)

    user_data[msg.chat.id] = {
        "lat": lat,
        "lon": lon,
        "times": times
    }

    result = (
        f"📍 Sizning hududingiz bo‘yicha namoz vaqtlari:\n\n"
        f"Bomdod: {times['bomdod']}\n"
        f"Quyosh: {times['quyosh']}\n"
        f"Peshin: {times['peshin']}\n"
        f"Asr: {times['asr']}\n"
        f"Shom: {times['shom']}\n"
        f"Xufton: {times['xufton']}\n\n"
        "✔️ Eslatmalar yoqilgan!"
    )

    bot.send_message(msg.chat.id, result)


# ---------- Eslatma yuborish funksiyasi ----------
def send_daily_updates():
    while True:
        now = datetime.now().strftime("%H:%M")

        for chat_id, info in user_data.items():

            lat = info["lat"]
            lon = info["lon"]

            # yangilangan vaqtlarni olish
            times = get_namoz_times_by_coords(lat, lon)
            user_data[chat_id]["times"] = times

            # 00:00 da kunlik yangilash
            if now == "00:00":
                bot.send_message(chat_id, "🔄 Bugungi namoz vaqtlari yangilandi!")
                txt = (
                    f"Bomdod: {times['bomdod']}\n"
                    f"Quyosh: {times['quyosh']}\n"
                    f"Peshin: {times['peshin']}\n"
                    f"Asr: {times['asr']}\n"
                    f"Shom: {times['shom']}\n"
                    f"Xufton: {times['xufton']}"
                )
                bot.send_message(chat_id, txt)

            # Namoz eslatmalari
            if now == times["bomdod"]:
                bot.send_message(chat_id, "🌅 Bomdod vaqti bo‘ldi!")

            if now == times["peshin"]:
                bot.send_message(chat_id, "🌞 Peshin vaqti bo‘ldi!")

            if now == times["asr"]:
                bot.send_message(chat_id, "🌤 Asr vaqti bo‘ldi!")

            if now == times["shom"]:
                bot.send_message(chat_id, "🌇 Shom vaqti bo‘ldi!")

            if now == times["xufton"]:
                bot.send_message(chat_id, "🌙 Xufton vaqti bo‘ldi!")

        time.sleep(30)  # har 30 soniyada tekshiradi


# ---------- Eslatma funksiyasini fon rejimida ishga tushiramiz ----------
threading.Thread(target=send_daily_updates, daemon=True).start()


# ---------- Botni ishga tushirish ----------
bot.polling(none_stop=True)
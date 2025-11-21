import telebot
from telebot import types
import requests
import threading
import time
from datetime import datetime

BOT_TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

# --- API tan oladigan shaharlarni moslashtirish ---
def normalize_region(city):
    city = city.lower()

    mapping = {
        "tashkent": "Toshkent",
        "toshkent": "Toshkent",
        "namangan": "Namangan",
        "andijan": "Andijon",
        "andijon": "Andijon",
        "bukhara": "Buxoro",
        "buxoro": "Buxoro",
        "samarkand": "Samarqand",
        "samarkand city": "Samarqand",
        "fargona": "Farg'ona",
        "fergana": "Farg'ona",
        "jizzakh": "Jizzax",
        "jizzax": "Jizzax",
        "navoiy": "Navoiy",
        "navoi": "Navoiy",
        "sirdaryo": "Sirdaryo",
        "sirdarya": "Sirdaryo",
        "surxondaryo": "Surxondaryo",
        "surkhandarya": "Surxondaryo",
        "qashqadaryo": "Qashqadaryo",
        "kashkadarya": "Qashqadaryo",
        "xorazm": "Xorazm",
        "khorezm": "Xorazm",
        "qoraqalpogiston": "Qoraqalpog'iston",
        "karakalpakstan": "Qoraqalpog'iston",
    }

    if city in mapping:
        return mapping[city]

    return None


# --- Namoz vaqtlarini olish ---
def get_namoz_times(region):
    url = f"https://islomapi.uz/api/present/day?region={region}"
    r = requests.get(url).json()

    if "times" not in r:
        return None

    return r["times"]


# --- /start ---
@bot.message_handler(commands=['start'])
def start(msg):
    txt = (
        "🕌 Assalomu alaykum!\n\n"
        "Men *namoz vaqtlarini eslatib turuvchi botman*.\n"
        "Quyida lokatsiya tugmasi chiqarildi👇"
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)
    kb.add(btn)

    bot.send_message(msg.chat.id, txt, reply_markup=kb, parse_mode="Markdown")


# --- Lokatsiya qabul qilish ---
@bot.message_handler(content_types=['location'])
def get_location(msg):
    lat = msg.location.latitude
    lon = msg.location.longitude

    geo_url = f"https://geocode.xyz/{lat},{lon}?json=1"
    geo = requests.get(geo_url).json()

    raw_city = geo.get("city")

    # 1) Geocode shahar qaytarmasa
    if not raw_city:
        bot.send_message(msg.chat.id, "⚠️ Shahar aniqlanmadi. Tizim Tashkentni qo‘lladi.")
        region = "Toshkent"
    else:
        # 2) Shahar nomini normallashtiramiz
        region = normalize_region(raw_city)

        # 3) API tanimasa, fallback
        if region is None:
            bot.send_message(msg.chat.id, f"⚠️ “{raw_city}” API tomonidan tanilmadi.\n"
                                          "Hudud sifatida Toshkent o‘rnatildi.")
            region = "Toshkent"

    user_data[msg.chat.id] = {"region": region}

    times = get_namoz_times(region)

    text = (
        f"🏙 Hudud: {region}\n\n"
        f"Bomdod: {times['tong_saharlik']}\n"
        f"Quyosh: {times['quyosh']}\n"
        f"Peshin: {times['peshin']}\n"
        f"Asr: {times['asr']}\n"
        f"Shom: {times['shom_iftor']}\n"
        f"Xufton: {times['hufton']}\n\n"
        "✔️ Eslatmalar yoqildi!"
    )

    bot.send_message(msg.chat.id, text)


# --- Har kuni eslatma ---
def send_daily_updates():
    while True:
        now = datetime.now().strftime("%H:%M")

        for chat_id, info in user_data.items():
            region = info["region"]
            times = get_namoz_times(region)

            if not times:
                continue

            if now == "00:00":
                bot.send_message(chat_id, "🔄 Namoz vaqtlari yangilandi!")

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

        time.sleep(30)


threading.Thread(target=send_daily_updates, daemon=True).start()
bot.polling(none_stop=True)
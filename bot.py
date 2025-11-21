import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests
import datetime
import asyncio

# ============================
#  BU YERGA TOKENINGIZNI YOZING
# ============================
BOT_TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"
# ============================


logging.basicConfig(level=logging.INFO)


# --- Namoz vaqtini olish funksiyasi ---
def get_prayer_times(lat, lon):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
    data = requests.get(url).json()
    return data["data"]["timings"]


# --- Start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("📍 Lokatsiya yuborish", request_location=True)
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

    await update.message.reply_text(
        "Assalomu alaykum!\nNamoz vaqtlarini olish uchun lokatsiya yuboring.",
        reply_markup=markup
    )


# --- Lokatsiya kelganda ---
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    lon = update.message.location.longitude

    context.user_data["lat"] = lat
    context.user_data["lon"] = lon

    times = get_prayer_times(lat, lon)

    msg = (
        "🕌 *Bugungi Namoz Vaqtlari:*\n\n"
        f"Bomdod: {times['Fajr']}\n"
        f"Quyosh: {times['Sunrise']}\n"
        f"Peshin: {times['Dhuhr']}\n"
        f"Asr: {times['Asr']}\n"
        f"Shom: {times['Maghrib']}\n"
        f"Xufton: {times['Isha']}"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")
    await update.message.reply_text("⏳ Vaqtlar 00:00 da avtomatik yangilanadi.")


# --- Har kuni 00:00 da avtomatik yuborish ---
async def send_daily_times(context: ContextTypes.DEFAULT_TYPE):

    for chat_id, data in context.application.user_data.items():
        if "lat" not in data or "lon" not in data:
            continue

        lat = data["lat"]
        lon = data["lon"]

        times = get_prayer_times(lat, lon)

        msg = (
            "🕌 *Yangi kun — yangilangan namoz vaqtlari:*\n\n"
            f"Bomdod: {times['Fajr']}\n"
            f"Quyosh: {times['Sunrise']}\n"
            f"Peshin: {times['Dhuhr']}\n"
            f"Asr: {times['Asr']}\n"
            f"Shom: {times['Maghrib']}\n"
            f"Xufton: {times['Isha']}"
        )

        try:
            await context.bot.send_message(chat_id=int(chat_id), text=msg, parse_mode="Markdown")
        except:
            pass


# --- Asosiy ishga tushirish ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    # Har kuni 00:00 da yangilash
    app.job_queue.run_daily(
        send_daily_times,
        time=datetime.time(0, 0, 0)  # 00:00
    )

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
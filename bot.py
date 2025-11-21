from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import datetime

TOKEN = "6282966969:AAFskjGj-doRRZDunEkP2_pmw0ZtqBS2_ms"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]]

    await update.message.reply_text(
        "Assalom-u Alaykum va Rohmatulloh 😊\n"
        "Men sizga namoz vaqtlarini eslatib turuvchi telegram botman.\n"
        "Menga joylashuvingizni 📍 yuboring, men bugungi namoz vaqtlarini aytaman.",
        reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True)
    )

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    lon = update.message.location.longitude

    url = f"https://api.aladhan.com/v1/timings/{datetime.date.today()}?latitude={lat}&longitude={lon}&method=2"
    data = requests.get(url).json()

    times = data["data"]["timings"]

    msg = (
        f"📅 Bugungi namoz vaqtlari:\n\n"
        f"Bomdod: {times['Fajr']}\n"
        f"Peshin: {times['Dhuhr']}\n"
        f"Asr: {times['Asr']}\n"
        f"Shom: {times['Maghrib']}\n"
        f"Xufton: {times['Isha']}"
    )

    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
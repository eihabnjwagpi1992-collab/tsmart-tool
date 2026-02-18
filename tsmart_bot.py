import os
import random
import string

import telebot
from dotenv import load_dotenv
from telebot import types

# تحميل الإعدادات من ملف .env
load_dotenv()

# إعداد توكن البوت الخاص بك
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# محاكاة قاعدة بيانات بسيطة
db = {"users": {"admin": {"credits": 100, "status": "Active"}}, "generated_keys": []}


def generate_pro_key(length=12):
    return "TSMART-PRO-" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 My Credits")
    btn2 = types.KeyboardButton("🔑 Gen Pro License (1 Year)")
    btn3 = types.KeyboardButton("💸 Deduct Credits")
    btn4 = types.KeyboardButton("📱 System Status")
    btn5 = types.KeyboardButton("🛠 Support")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    welcome_text = (
        "🚀 *Tsmart Tool PRO Admin Bot*\n\n"
        "Welcome! You can now manage your professional mobile repair tool.\n\n"
        "💡 *New:* Use the button below to generate 1-Year Pro Licenses."
    )
    bot.send_message(
        message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown"
    )


@bot.message_handler(func=lambda message: message.text == "🔑 Gen Pro License (1 Year)")
def handle_generate_pro_key(message):
    new_key = generate_pro_key()
    db["generated_keys"].append(new_key)
    bot.reply_to(
        message,
        f"✅ *New 1-Year Pro License Generated:*\n`{new_key}`\n\n_This key will activate the MTK Pro and Xiaomi modules._",
        parse_mode="Markdown",
    )


@bot.message_handler(func=lambda message: message.text == "📊 My Credits")
def check_credits(message):
    credits = db["users"]["admin"]["credits"]
    bot.reply_to(message, f"💰 *Admin Credits:* `{credits}`", parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "📱 System Status")
def device_status(message):
    status_text = (
        "🔍 *Tsmart Pro Monitor:*\n"
        "━━━━━━━━━━━━━━━\n"
        "📡 *Server:* Online ✅\n"
        "🛠 *MTK Module:* Integrated\n"
        "🔐 *Auth Server:* Ready\n"
        "📈 *Total Users:* 1 (Admin)"
    )
    bot.send_message(message.chat.id, status_text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "🛠 Support")
def support(message):
    bot.reply_to(
        message,
        "👨‍💻 *Tsmart Support:*\nContact: @YourAdminUsername",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    print("Tsmart Pro Admin Bot is starting...")
    bot.infinity_polling()

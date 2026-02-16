import telebot
from telebot import types
import random
import string

# إعداد توكن البوت الخاص بك
BOT_TOKEN = '7983630628:AAGQgzpeU0-Iut2gmOMSS4rCF1mXZNNCD8c'
bot = telebot.TeleBot(BOT_TOKEN)

# محاكاة قاعدة بيانات (في الواقع يفضل استخدام SQLite)
db = {
    "users": {
        "admin": {"credits": 100, "status": "Active", "keys": []}
    },
    "generated_keys": []
}

def generate_key(length=12):
    return 'TSMART-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 My Credits')
    btn2 = types.KeyboardButton('🔑 Generate New Key')
    btn3 = types.KeyboardButton('💸 Deduct Credits')
    btn4 = types.KeyboardButton('📱 Device Status')
    btn5 = types.KeyboardButton('🛠 Support')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    welcome_text = (
        "🚀 *Tsmart Tool Admin Bot*\n\n"
        "Welcome! You can now manage your repair tool directly from Telegram.\n\n"
        "💡 *Quick Tip:* Use the buttons below to control credits and keys."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '📊 My Credits')
def check_credits(message):
    credits = db["users"]["admin"]["credits"]
    bot.reply_to(message, f"💰 *Current Balance:* `{credits}` Credits", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🔑 Generate New Key')
def handle_generate_key(message):
    new_key = generate_key()
    db["generated_keys"].append(new_key)
    bot.reply_to(message, f"✅ *New Key Generated:*\n`{new_key}`\n\n_Share this key with the user to activate the tool._", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '💸 Deduct Credits')
def handle_deduct(message):
    msg = bot.reply_to(message, "🔢 Enter amount to deduct from Admin:")
    bot.register_next_step_handler(msg, process_deduction)

def process_deduction(message):
    try:
        amount = int(message.text)
        if amount > db["users"]["admin"]["credits"]:
            bot.reply_to(message, "❌ Insufficient credits!")
        else:
            db["users"]["admin"]["credits"] -= amount
            bot.reply_to(message, f"✅ Successfully deducted `{amount}` credits.\nRemaining: `{db['users']['admin']['credits']}`", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Please enter a valid number.")

@bot.message_handler(func=lambda message: message.text == '📱 Device Status')
def device_status(message):
    status_text = (
        "🔍 *System Monitor:*\n"
        "━━━━━━━━━━━━━━━\n"
        "📡 *Server:* Online ✅\n"
        "📱 *Device:* Connected (Xiaomi)\n"
        "⚡ *Mode:* Fastboot\n"
        "🛠 *Last Action:* FRP Bypass Success"
    )
    bot.send_message(message.chat.id, status_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🛠 Support')
def support(message):
    bot.reply_to(message, "👨‍💻 *Tsmart Support:*\nContact: @YourAdminUsername\nWebsite: tsmart-tool.com", parse_mode="Markdown")

if __name__ == "__main__":
    print("Tsmart Admin Bot is starting with your token...")
    bot.infinity_polling()

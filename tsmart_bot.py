
import os
import random
import string
import hashlib
from datetime import datetime

import telebot
from dotenv import load_dotenv
from telebot import types

from database_manager import DatabaseManager

# تحميل الإعدادات من ملف .env
load_dotenv()

# إعداد توكن البوت الخاص بك ومعرف المسؤول
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) # تأكد من تحويله إلى عدد صحيح
bot = telebot.TeleBot(BOT_TOKEN)

db_manager = DatabaseManager()

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for i in range(length))


@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton("➕ إنشاء مستخدم جديد")
        btn2 = types.KeyboardButton("🔑 توليد ترخيص لمستخدم")
        btn3 = types.KeyboardButton("📋 عرض المستخدمين والتراخيص")
        btn4 = types.KeyboardButton("❌ إلغاء تفعيل ترخيص")
        btn5 = types.KeyboardButton("🗑 حذف ترخيص")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        welcome_text = (
            "🚀 *Tsmart Tool PRO Admin Bot*\n\n"
            "أهلاً بك! يمكنك الآن إدارة المستخدمين والتراخيص لأداة صيانة الهواتف المحمولة."
        )
        bot.send_message(
            message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "أنت لست مسؤولاً. لا يمكنك استخدام هذا البوت.")


# --- إنشاء مستخدم جديد ---
@bot.message_handler(func=lambda message: message.text == "➕ إنشاء مستخدم جديد" and message.chat.id == ADMIN_ID)
def handle_create_user_prompt(message):
    bot.reply_to(message, "الرجاء إرسال البريد الإلكتروني للمستخدم الجديد.")
    bot.register_next_step_handler(message, get_user_email_for_creation)

def get_user_email_for_creation(message):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        bot.reply_to(message, "بريد إلكتروني غير صالح. الرجاء إدخال بريد إلكتروني صحيح.")
        return
    
    # Check if user already exists
    existing_user = db_manager.get_user_by_email(email)
    if existing_user:
        bot.reply_to(message, f"المستخدم ذو البريد الإلكتروني {email} موجود بالفعل.")
        return

    # Generate a random password for the new user
    password = generate_random_password()
    user, msg = db_manager.create_user(email, password)

    if user:
        bot.reply_to(message, f"✅ تم إنشاء المستخدم بنجاح:\nالبريد الإلكتروني: `{email}`\nكلمة المرور: `{password}`\n\n*الرجاء تزويد المستخدم بكلمة المرور هذه.*", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ حدث خطأ أثناء إنشاء المستخدم: {msg}")


# --- توليد ترخيص لمستخدم ---
@bot.message_handler(func=lambda message: message.text == "🔑 توليد ترخيص لمستخدم" and message.chat.id == ADMIN_ID)
def handle_generate_license_prompt(message):
    bot.reply_to(message, "الرجاء إرسال البريد الإلكتروني للمستخدم الذي تريد توليد ترخيص له.")
    bot.register_next_step_handler(message, get_user_email_for_license)

def get_user_email_for_license(message):
    email = message.text.strip()
    user = db_manager.get_user_by_email(email)
    if not user:
        bot.reply_to(message, "المستخدم غير موجود. الرجاء التأكد من البريد الإلكتروني.")
        return
    
    bot.reply_to(message, "الرجاء اختيار مدة الترخيص: (3 أشهر / 6 أشهر / 12 شهر)")
    bot.register_next_step_handler(message, get_license_duration, user.id)

def get_license_duration(message, user_id):
    duration_text = message.text.strip()
    duration_months = 0
    if "3" in duration_text:
        duration_months = 3
    elif "6" in duration_text:
        duration_months = 6
    elif "12" in duration_text:
        duration_months = 12
    else:
        bot.reply_to(message, "مدة غير صالحة. الرجاء اختيار 3 أو 6 أو 12 شهر.")
        return

    try:
        new_license = db_manager.create_license_for_user(user_id, duration_months)
        bot.reply_to(
            message,
            f"""✅ تم توليد ترخيص جديد للمستخدم:\nالمفتاح: `{new_license.key}`\nالمدة: {duration_months} أشهر\nتاريخ الانتهاء: {new_license.expires_at.strftime("%Y-%m-%d")}""",
            parse_mode="Markdown",
        )
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء توليد الترخيص: {e}")


# --- عرض المستخدمين والتراخيص ---
@bot.message_handler(func=lambda message: message.text == "📋 عرض المستخدمين والتراخيص" and message.chat.id == ADMIN_ID)
def handle_view_users_and_licenses(message):
    users = db_manager.get_all_users()
    if not users:
        bot.reply_to(message, "لا توجد حسابات مستخدمين في قاعدة البيانات.")
        return

    response_text = """*قائمة المستخدمين والتراخيص:*
-----------------------------------
"""
    for user in users:
        response_text += f"""*المستخدم:* `{user.email}`\n"""
        if user.licenses:
            for lic in user.licenses:
                status = "نشط" if lic.is_active and lic.expires_at > datetime.utcnow() else "غير نشط"
                used_on = f"على HWID: {lic.hwid}" if lic.is_used else "غير مستخدم"
                response_text += f"""  - المفتاح: `{lic.key}`\n    الحالة: {status}\n    تاريخ الانتهاء: {lic.expires_at.strftime("%Y-%m-%d")}\n    {used_on}\n"""
        else:
            response_text += """  (لا توجد تراخيص لهذا المستخدم)\n"""
        response_text += """-----------------------------------
"""
    bot.send_message(message.chat.id, response_text, parse_mode="Markdown")


# --- إلغاء تفعيل ترخيص ---
@bot.message_handler(func=lambda message: message.text == "❌ إلغاء تفعيل ترخيص" and message.chat.id == ADMIN_ID)
def handle_deactivate_license_prompt(message):
    bot.reply_to(message, "الرجاء إرسال مفتاح الترخيص الذي تريد إلغاء تفعيله.")
    bot.register_next_step_handler(message, deactivate_license_step)

def deactivate_license_step(message):
    license_key = message.text.strip()
    success = db_manager.deactivate_license(license_key)
    if success:
        bot.reply_to(message, f"✅ تم إلغاء تفعيل الترخيص `{license_key}` بنجاح.")
    else:
        bot.reply_to(message, f"❌ لم يتم العثور على الترخيص `{license_key}` أو حدث خطأ.")


# --- حذف ترخيص ---
@bot.message_handler(func=lambda message: message.text == "🗑 حذف ترخيص" and message.chat.id == ADMIN_ID)
def handle_delete_license_prompt(message):
    bot.reply_to(message, "الرجاء إرسال مفتاح الترخيص الذي تريد حذفه.")
    bot.register_next_step_handler(message, delete_license_step)

def delete_license_step(message):
    license_key = message.text.strip()
    success = db_manager.delete_license(license_key)
    if success:
        bot.reply_to(message, f"✅ تم حذف الترخيص `{license_key}` بنجاح.")
    else:
        bot.reply_to(message, f"❌ لم يتم العثور على الترخيص `{license_key}` أو حدث خطأ.")


if __name__ == "__main__":
    print("Tsmart Pro Admin Bot is starting...")
    bot.infinity_polling()

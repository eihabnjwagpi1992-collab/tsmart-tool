import logging
import random
import string
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- إعدادات البوت (Configuration) ---

# 1. التوكن الخاص بك
BOT_TOKEN "7983630628:AAGQgzpeU0-Iut2gmOMSS4rCF1mXZNNCD8c"

# 2. آيدي الأدمن (حسابك الشخصي للتحكم الكامل)
ADMIN_ID = 7175591691  

# --- قاعدة البيانات (حفظ المفاتيح والمستخدمين) ---
DB_FILE = "tsp_bot_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {"keys": [], "users": {}, "logs": []}
    return {"keys": [], "users": {}, "logs": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- مولد السيريلات (Key Generator) ---
def generate_key(months):
    # يولد مفتاح عشوائي مكون من أحرف وأرقام احترافي
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"TSP-{months}M-{rand_str}"

# --- معالجات الأوامر (Handlers) ---

# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو الأدمن (أنت فقط)
    if str(user_id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ عذراً، هذا البوت خاص بمدير أداة TSP TOOL PRO فقط.")
        return

    # لوحة التحكم (أزرار تفاعلية)
    keyboard = [
        [InlineKeyboardButton("🔑 توليد مفتاح (3 شهور)", callback_query_data='gen_3')],
        [InlineKeyboardButton("🔑 توليد مفتاح (6 شهور)", callback_query_data='gen_6')],
        [InlineKeyboardButton("🔑 توليد مفتاح (سنة كاملة)", callback_query_data='gen_12')],
        [InlineKeyboardButton("👥 عرض المستخدمين النشطين", callback_query_data='view_users')],
        [InlineKeyboardButton("📜 سجل نشاط الأجهزة", callback_query_data='view_logs')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f"👋 أهلاً بك في لوحة تحكم TSP TOOL PRO\n"
        f"👤 معرف المدير: `{ADMIN_ID}`\n\n"
        "🛠 **إدارة الاشتراكات والعمليات:**\n"
        "اختر العملية التي تريد تنفيذها من القائمة أدناه:"
    )
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

# معالج ضغط الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # حماية إضافية للأزرار للتأكد من المدير فقط
    if str(update.effective_user.id) != str(ADMIN_ID):
        return

    data = load_db()
    
    # معالجة توليد المفاتيح (3، 6، 12 شهر)
    if query.data.startswith('gen_'):
        months = query.data.split('_')[1]
        new_key = generate_key(months)
        
        # حفظ المفتاح في قاعدة البيانات كـ "غير مستخدم"
        data["keys"].append({
            "key": new_key, 
            "months": months, 
            "status": "unused", 
            "created_at": "Today"
        })
        save_db(data)
        
        msg = (
            f"✅ **تم توليد مفتاح تفعيل جديد!**\n\n"
            f"🔑 الكود: `{new_key}`\n"
            f"📅 المدة: {months} شهور\n\n"
            f"_يمكنك الضغط على الكود لنسخه وإرساله للمشترك_"
        )
        await query.edit_message_text(msg, parse_mode='Markdown')
        
    # عرض المستخدمين واشتراكاتهم
    elif query.data == 'view_users':
        if not data["users"]:
            await query.edit_message_text("📭 لا يوجد مستخدمين مسجلين حالياً.")
        else:
            users_str = "👥 **قائمة المستخدمين والاشتراكات:**\n\n"
            for hwid, info in data["users"].items():
                users_str += f"🔹 HWID: `{hwid}`\n📅 انتهاء: {info.get('expiry', 'غير محدد')}\n\n"
            await query.edit_message_text(users_str, parse_mode='Markdown')
        
    # عرض سجل العمليات التي تمت عبر الأداة
    elif query.data == 'view_logs':
        if not data["logs"]:
            await query.edit_message_text("📭 سجل العمليات فارغ حالياً.")
        else:
            logs_str = "📜 **آخر نشاطات الأجهزة (Logs):**\n\n"
            # عرض آخر 10 عمليات
            for log in data["logs"][-10:]:
                logs_str += f"🕒 {log.get('time', '')} | {log.get('hwid', '')} | {log.get('action', '')}\n"
            await query.edit_message_text(logs_str)

# --- تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 TSP TOOL Server Bot is STARTING...")
    
    # بناء التطبيق باستخدام التوكن المحدث
    app = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة المعالجات (أوامر وأزرار)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # بدء التشغيل الفعلي
    print(f"✅ Bot is Online for Admin: {ADMIN_ID}")
    app.run_polling()

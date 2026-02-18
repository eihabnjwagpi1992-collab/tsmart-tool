import logging
import random
import string
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
# Replace with your actual Bot Token from @BotFather
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_ID = "YOUR_ADMIN_TELEGRAM_ID"  # Replace with your ID to restrict access

# --- DATA PERSISTENCE ---
DB_FILE = "tsp_bot_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"keys": [], "users": {}, "logs": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- KEY GENERATOR ---
def generate_key(months):
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"TSP-{months}-{rand_str}"

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("Welcome to TSP TOOL Support. Please contact @Admin for license.")
        return

    keyboard = [
        [InlineKeyboardButton("Generate 3 Months Key", callback_query_data='gen_3')],
        [InlineKeyboardButton("Generate 6 Months Key", callback_query_data='gen_6')],
        [InlineKeyboardButton("Generate 1 Year Key", callback_query_data='gen_12')],
        [InlineKeyboardButton("View Active Users", callback_query_data='view_users')],
        [InlineKeyboardButton("View Logs", callback_query_data='view_logs')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("TSP TOOL Admin Panel:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if str(update.effective_user.id) != str(ADMIN_ID): return

    data = load_db()
    
    if query.data.startswith('gen_'):
        months = query.data.split('_')[1]
        new_key = generate_key(months)
        data["keys"].append({"key": new_key, "months": months, "status": "unused"})
        save_db(data)
        await query.edit_message_text(f"✅ New Key Generated ({months} Months):\n\n`{new_key}`", parse_mode='Markdown')
        
    elif query.data == 'view_users':
        users_str = "Active Users:\n"
        for hwid, info in data["users"].items():
            users_str += f"👤 HWID: {hwid} | Expiry: {info['expiry']}\n"
        await query.edit_message_text(users_str if len(data["users"]) > 0 else "No active users yet.")
        
    elif query.data == 'view_logs':
        logs_str = "Recent Activity:\n"
        for log in data["logs"][-10:]: # Last 10 logs
            logs_str += f"🕒 {log['time']} | {log['hwid']} | {log['action']}\n"
        await query.edit_message_text(logs_str if len(data["logs"]) > 0 else "No activity logs yet.")

# --- API FOR TOOL INTEGRATION (Simulated via JSON for now) ---
# In a real setup, this would be a Flask/FastAPI backend
def record_tool_activity(hwid, action):
    data = load_db()
    from datetime import datetime
    data["logs"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hwid": hwid,
        "action": action
    })
    save_db(data)

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Please set your BOT_TOKEN in tsp_bot.py")
    else:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        print("TSP Admin Bot Started...")
        app.run_polling()

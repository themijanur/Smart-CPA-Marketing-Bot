import telebot
import sqlite3
from telebot import types

# ===== CONFIG =====
TOKEN = "8180166210:AAE6_FAWXD3CVg3T7aNgkhJJ6Jtib2cAWYo"
ADMIN_ID = 810927009   # তোমার Telegram ID

bot = telebot.TeleBot(TOKEN)

# ===== DATABASE SETUP =====
conn = sqlite3.connect("numbers.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS numbers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
number TEXT UNIQUE,
used INTEGER DEFAULT 0
)
""")
conn.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📞 Get Number")
    bot.send_message(msg.chat.id, "Welcome!\nClick 📞 Get Number", reply_markup=kb)

# ===== BULK ADD NUMBERS (ADMIN ONLY) =====
@bot.message_handler(commands=['add'])
def add_numbers(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    data = msg.text.replace("/add", "").strip()
    numbers = data.splitlines()
    added = 0

    for num in numbers:
        try:
            cur.execute("INSERT INTO numbers(number) VALUES(?)", (num.strip(),))
            conn.commit()
            added += 1
        except:
            pass

    bot.send_message(msg.chat.id, f"✅ Added {added} numbers")

# ===== GET NUMBER =====
@bot.message_handler(func=lambda m: m.text == "📞 Get Number")
def get_number(msg):
    cur.execute("SELECT id,number FROM numbers WHERE used=0 LIMIT 1")
    row = cur.fetchone()

    if not row:
        bot.send_message(msg.chat.id, "❌ No numbers available")
        return

    num_id, number = row
    cur.execute("UPDATE numbers SET used=1 WHERE id=?", (num_id,))
    conn.commit()

    bot.send_message(msg.chat.id, f"📞 Your Number:\n{number}")

# ===== RUN =====
print("Bot Running...")
bot.infinity_polling()

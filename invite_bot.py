
import telebot
from telebot import types
import sqlite3

TOKEN = 'ضع_توكن_البوت_هنا'  # ← استبدل هذا بالتوكن الحقيقي من BotFather
bot = telebot.TeleBot(TOKEN)

# قاعدة البيانات
conn = sqlite3.connect('referral.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrals INTEGER DEFAULT 0,
    invited_by INTEGER
)''')
conn.commit()

# دالة التسجيل
def register_user(user_id, invited_by=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        if invited_by and invited_by != user_id:
            cursor.execute("INSERT INTO users (user_id, referrals, invited_by) VALUES (?, 0, ?)", (user_id, invited_by))
            cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (invited_by,))
        else:
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

# أمر /start
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    invited_by = int(args[1]) if len(args) > 1 else None
    register_user(message.from_user.id, invited_by)

    markup = types.InlineKeyboardMarkup()
    invite_btn = types.InlineKeyboardButton("📩 رابط الدعوة", url=f"https://t.me/{bot.get_me().username}?start={message.from_user.id}")
    markup.add(invite_btn)

    bot.send_message(message.chat.id, f"👋 مرحباً {message.from_user.first_name}!

✅ احصل على نقاط عند دعوة أصدقائك!
🎁 كل دعوة = 1 نقطة.

اضغط الزر للحصول على رابط الدعوة الخاص بك👇", reply_markup=markup)

# أمر /stats
@bot.message_handler(commands=['stats'])
def stats(message):
    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (message.from_user.id,))
    result = cursor.fetchone()
    count = result[0] if result else 0
    bot.send_message(message.chat.id, f"📊 لديك {count} دعوات ناجحة.")

bot.polling()

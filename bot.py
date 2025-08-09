# bot.py
import logging, threading, time
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from db import init_db, SessionLocal, set_setting, get_setting
from config import TELEGRAM_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, FLASK_PORT, FLASK_HOST, SECRET_KEY
from models import User, TopUp, GameLog, Challenge, Setting
from games import play_crash, play_blackjack, play_crystal, play_texas, play_dice, play_roulette

# logging
logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

# init DB
init_db()

bot = TeleBot(TELEGRAM_TOKEN, parse_mode=None)  # plain text messages — avoid HTML parse errors

def safe_send(chat_id, text):
    try:
        bot.send_message(chat_id, text, disable_web_page_preview=True)
    except Exception as e:
        logging.exception("Failed to send message: %s", e)

def ensure_user(tg_user):
    db = SessionLocal()
    u = db.query(User).filter_by(telegram_id=tg_user.id).first()
    if not u:
        u = User(telegram_id=tg_user.id, username=getattr(tg_user,"username",None), balance=500)
        db.add(u); db.commit(); db.refresh(u)
    res = {"id":u.id, "telegram_id":u.telegram_id, "username":u.username, "balance":u.balance, "banned":bool(u.banned)}
    db.close()
    return res

def change_balance(tg_id, delta):
    db = SessionLocal()
    u = db.query(User).filter_by(telegram_id=tg_id).first()
    if u:
        u.balance += int(delta)
        db.add(u); db.commit()
    db.close()

# keyboards
def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎮 الألعاب"), KeyboardButton("💳 طلب شحن"), KeyboardButton("💰 رصيدي"))
    kb.add(KeyboardButton("🚀 Crash"), KeyboardButton("🃏 Blackjack"), KeyboardButton("💎 Crystal"))
    kb.add(KeyboardButton("♠ Texas"), KeyboardButton("🎲 Dice"), KeyboardButton("🎡 Roulette"))
    return kb

@bot.message_handler(commands=["start","help"])
def start(m):
    ensure_user(m.from_user)
    safe_send(m.chat.id, "أهلاً! اضغط على الأزرار للعب أو اكتب أمر. مثال: `crash vs 20`")
    bot.send_message(m.chat.id, "قائمة:", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower()=="💰 رصيدي" or (m.text and m.text.strip().lower()=="/balance"))
def balance_cmd(m):
    u = ensure_user(m.from_user)
    safe_send(m.chat.id, f"💰 رصيدك: {u['balance']}")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("topup") or (m.text and m.text.strip().lower()=="💳 طلب شحن"))
def topup_cmd(m):
    parts = (m.text or "").strip().split()
    if len(parts) >= 2 and parts[1].isdigit():
        amount = int(parts[1])
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=m.from_user.id).first()
        if not user:
            user = User(telegram_id=m.from_user.id, username=m.from_user.username, balance=0)
            db.add(user); db.commit(); db.refresh(user)
        t = TopUp(user_id=user.id, amount=amount)
        db.add(t); db.commit(); db.close()
        safe_send(m.chat.id, "📩 طلب شحن أنشئ، سيقوم الأدمن بالمراجعة.")
        return
    # ask amount
    safe_send(m.chat.id, "اكتب: topup <amount>  أو أرسل رقم المبلغ الآن.")

# parsing "game vs stake" simple commands
@bot.message_handler(func=lambda m: True)
def generic(m):
    text = (m.text or "").strip()
    # parse like "crash vs 20"
    parts = text.split()
    if len(parts) >= 3 and parts[1].lower() == "vs" and parts[2].isdigit():
        game = parts[0].lower()
        stake = int(parts[2])
        user = ensure_user(m.from_user)
        if user["balance"] < stake:
            safe_send(m.chat.id, "رصيدك غير كافٍ.")
            return
        # deduct stake upfront
        change_balance(m.from_user.id, -stake)
        if game == "crash":
            ok,payout,r = play_crash(m.from_user.id, stake)
            if ok:
                change_balance(m.from_user.id, payout)
                safe_send(m.chat.id, f"🚀 فزت {payout} (r={r:.2f})")
            else:
                safe_send(m.chat.id, f"💥 خسرت {stake} (r={r:.2f})")
        elif game == "blackjack":
            ok,payout,r = play_blackjack(m.from_user.id, stake)
            if ok:
                change_balance(m.from_user.id, payout)
                safe_send(m.chat.id, f"🃏 فزت {payout} (r={r:.2f})")
            else:
                safe_send(m.chat.id, f"❌ خسرت {stake} (r={r:.2f})")
        elif game == "crystal":
            ok,payout,r = play_crystal(m.from_user.id, stake)
            if ok:
                change_balance(m.from_user.id, payout)
                safe_send(m.chat.id, f"💎 ربحت {payout} (r={r:.2f})")
            else:
                safe_send(m.chat.id, f"💨 خسرت {stake} (r={r:.2f})")
        elif game == "texas":
            ok,payout,r = play_texas(m.from_user.id, stake)
            if ok:
                change_balance(m.from_user.id, payout)
                safe_send(m.chat.id, f"♠️ ربحت {payout} (r={r:.2f})")
            else:
                safe_send(m.chat.id, f"💔 خسرت {stake} (r={r:.2f})")
        elif game == "dice":
            if len(parts) >= 4 and parts[3].isdigit():
                choice = int(parts[3])
                ok,payout,roll,r = play_dice(m.from_user.id, stake, choice)
                if ok:
                    change_balance(m.from_user.id, payout)
                    safe_send(m.chat.id, f"🎲 النتيجة {roll} — فزت {payout} (r={r:.2f})")
                else:
                    safe_send(m.chat.id, f"🎲 النتيجة {roll} — خسرت {stake} (r={r:.2f})")
            else:
                safe_send(m.chat.id, "صيغة dice vs <stake> <choice(1-6)>")
        elif game == "roulette":
            if len(parts) >= 4:
                bet = parts[3]
                ok,payout,spin,r = play_roulette(m.from_user.id, stake, bet)
                if ok:
                    change_balance(m.from_user.id, payout)
                    safe_send(m.chat.id, f"🎡 الدوران: {spin} — فزت {payout} (r={r:.2f})")
                else:
                    safe_send(m.chat.id, f"🎡 الدوران: {spin} — خسرت {stake} (r={r:.2f})")
            else:
                safe_send(m.chat.id, "صيغة roulette vs <stake> <bet> (red|black|odd|even|0-36)")
        else:
            safe_send(m.chat.id, "لعبة غير معروفة. مثال: crash vs 20")
    else:
        # simple help
        safe_send(m.chat.id, "أرسل أمرًا مثل: crash vs 20  أو اكتب /start للاعادة")

# start polling in background
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logging.exception("Polling failed: %s", e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
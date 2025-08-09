# =========================
# main.py - ملف التشغيل الرئيسي
# =========================
from flask import Flask, render_template, request, redirect, url_for, session
import telebot
from database import init_db, add_user, get_balance, update_balance, get_win_rate, set_win_rate
from games import game_plane, game_blackjack, game_crystal, game_texas, game_roulette

# ===== إعداد البوت =====
TOKEN = "7241954052:AAGjMs4Xzm5bzydQO0GsLj60EPfSbT6YvQ4"
ADMIN_USER = "admin"
ADMIN_PASS = "156156"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.secret_key = "secret123"

# ===== تهيئة قاعدة البيانات =====
init_db()

# ===== أوامر البوت =====
@bot.message_handler(commands=['start'])
def start_game(message):
    user_id = message.from_user.id
    add_user(user_id)
    bot.reply_to(message, f"👋 أهلاً بك في كازينو البوت!\n💰 رصيدك الحالي: {get_balance(user_id)}")

@bot.message_handler(commands=['plane'])
def play_plane(message):
    bot.reply_to(message, game_plane(message.from_user.id, 100))

@bot.message_handler(commands=['blackjack'])
def play_blackjack(message):
    bot.reply_to(message, game_blackjack(message.from_user.id, 100))

@bot.message_handler(commands=['crystal'])
def play_crystal(message):
    bot.reply_to(message, game_crystal(message.from_user.id, 100))

@bot.message_handler(commands=['texas'])
def play_texas(message):
    bot.reply_to(message, game_texas(message.from_user.id, 100))

@bot.message_handler(commands=['roulette'])
def play_roulette(message):
    bot.reply_to(message, game_roulette(message.from_user.id, 100, "🔴"))

# ===== لوحة تحكم الأدمن =====
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        set_win_rate(float(request.form["win_rate"]))
    return render_template("dashboard.html", win_rate=get_win_rate())

# ===== تشغيل البوت و Flask =====
import threading

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
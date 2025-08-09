# config.py
# ----------------
# مُدمج بالتوكن وبيانات الادمن كما طلبت
TELEGRAM_TOKEN = "7241954052:AAGjMs4Xzm5bzydQO0GsLj60EPfSbT6YvQ4"  # <-- توكنك المدمج
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "156156"   # <-- كود الأدمن المدمج
SECRET_KEY = "change_this_secret_now"
FLASK_HOST = "0.0.0.0"
# في Replit قد تحتاج PORT من env، ولكن الافتراضي هنا 8080
FLASK_PORT = int(__import__("os").environ.get("PORT", 8080))
DATABASE_URL = "sqlite:///./casino.db"
# افتراضيات win_rate (قابلة للتعديل من لوحة التحكم)
DEFAULT_WIN_RATES = {
    "crash": 20,       # percent
    "blackjack": 18,
    "crystal": 15,
    "texas": 17,
    "dice": 12,
    "roulette": 10
}
LOG_FILE = "casino.log"
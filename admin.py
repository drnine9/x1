# admin.py
from flask import Flask, request, redirect, url_for, render_template_string, session
from db import init_db, SessionLocal, get_setting, set_setting
from config import ADMIN_USERNAME, ADMIN_PASSWORD, FLASK_HOST, FLASK_PORT, SECRET_KEY
from models import User, TopUp, Setting
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY
init_db()

LOGIN_HTML = """
<h2>لوحة تحكم - تسجيل الدخول</h2>
<form method="post">
  اسم المستخدم: <input name="username" value="admin"><br>
  كلمة المرور: <input type="password" name="password"><br>
  <button type="submit">دخول</button>
</form>
"""

DASH_HTML = """
<h1>لوحة الادمن</h1>
<p>تعديل نسب الفوز لكل لعبة (نسبة بين 0-100)</p>
<form method="post" action="/set_rates">
{% for g in games %}
  {{g}}: <input name="{{g}}" value="{{rates[g]}}"><br>
{% endfor %}
<button type="submit">حفظ</button>
</form>

<h2>طلبات الشحن</h2>
{% for t in topups %}
  <div>#{{t.id}} - user: {{t.user_id}} - amount: {{t.amount}} - status: {{t.status}} 
  - <a href="/approve/{{t.id}}">قبول</a> | <a href="/reject/{{t.id}}">رفض</a></div>
{% else %}
  <p>لا توجد طلبات</p>
{% endfor %}
"""

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("username")==ADMIN_USERNAME and request.form.get("password")==ADMIN_PASSWORD:
            session["admin"]=True
            return redirect(url_for("dashboard"))
        return "بيانات خاطئة"
    return render_template_string(LOGIN_HTML)

@app.route("/dashboard")
@admin_required
def dashboard():
    db = SessionLocal()
    rates = {}
    games = ["crash","blackjack","crystal","texas","dice","roulette"]
    for g in games:
        s = db.query(Setting).filter_by(key=f"win_rate:{g}").first()
        rates[g] = s.value if s else "20"
    topups = db.query(TopUp).filter_by(status="pending").all()
    db.close()
    return render_template_string(DASH_HTML, games=games, rates=rates, topups=topups)

@app.route("/set_rates", methods=["POST"])
@admin_required
def set_rates():
    db = SessionLocal()
    games = ["crash","blackjack","crystal","texas","dice","roulette"]
    for g in games:
        v = request.form.get(g)
        if v is not None:
            s = db.query(Setting).filter_by(key=f"win_rate:{g}").first()
            if s:
                s.value = str(int(float(v)))
            else:
                s = Setting(key=f"win_rate:{g}", value=str(int(float(v))))
                db.add(s)
    db.commit(); db.close()
    return redirect(url_for("dashboard"))

@app.route("/approve/<int:tid>")
@admin_required
def approve_topup(tid):
    db = SessionLocal()
    t = db.query(TopUp).get(tid)
    if t and t.status=="pending":
        u = db.query(User).get(t.user_id)
        u.balance += t.amount
        t.status="approved"
        db.commit()
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/reject/<int:tid>")
@admin_required
def reject_topup(tid):
    db = SessionLocal()
    t = db.query(TopUp).get(tid)
    if t:
        t.status="rejected"
        db.commit()
    db.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)        تعديل النسبة (%): <input type="number" step="0.01" name="rate" value="{win_rate}">
        <input type="submit" value="تعديل">
    </form>
    <br><h3>طلبات الشحن</h3>
    <table border="1">
        <tr><th>رقم الطلب</th><th>المستخدم</th><th>المبلغ</th><th>الحالة</th><th>الإجراء</th></tr>
    """
    for req in requests_list:
        req_id, user_id, amount, status = req
        html += f"""
        <tr>
            <td>{req_id}</td>
            <td>{user_id}</td>
            <td>{amount}</td>
            <td>{status}</td>
            <td>
                <a href="/approve/{req_id}">قبول</a> | 
                <a href="/reject/{req_id}">رفض</a>
            </td>
        </tr>
        """
    html += "</table>"
    return html

# تعديل النسبة
@app.route("/set_win_rate", methods=["POST"])
def set_rate():
    if not session.get("admin"):
        return redirect(url_for("login"))
    try:
        new_rate = float(request.form.get("rate")) / 100
        set_win_rate(new_rate)
    except:
        pass
    return redirect(url_for("dashboard"))

# قبول شحن
@app.route("/approve/<int:req_id>")
def approve(req_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    update_topup_status(req_id, "approved")
    return redirect(url_for("dashboard"))

# رفض شحن
@app.route("/reject/<int:req_id>")
def reject(req_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    update_topup_status(req_id, "rejected")
    return redirect(url_for("dashboard"))

def run_panel():
    app.run(host=PANEL_HOST, port=PANEL_PORT)
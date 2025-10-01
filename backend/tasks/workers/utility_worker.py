# backend/tasks/workers/utility_worker.py
import smtplib
import math
import requests
from datetime import datetime, timedelta
import redis
from email.mime.text import MIMEText
from ...config import REDIS_URL, OPENWEATHER_API_KEY, EMAIL_USER, EMAIL_PASS 
from ..celery_app import celery_app 

# --- Global Redis State ---
_redis_client = None

def get_redis_client():
    """Initializes and returns the Redis client, ensuring it's only done once."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"FATAL Redis Connection Error in utility_worker: {e}")
            raise e
    return _redis_client

# -------------------- Reminder --------------------
@celery_app.task(name="tasks.set_reminder")
def set_reminder(message: str, minutes: int, user_id="default"):
    r = get_redis_client()
    trigger_time = datetime.now() + timedelta(minutes=minutes)
    reminder_id = f"reminder:{user_id}:{trigger_time.timestamp()}"
    r.hset(reminder_id, mapping={"time": trigger_time.isoformat(), "message": message})
    r.expireat(reminder_id, trigger_time)
    return f"⏰ Reminder set: '{message}' in {minutes} min"

@celery_app.task(name="tasks.check_reminders")
def check_reminders(user_id="default"):
    r = get_redis_client()
    keys = r.keys(f"reminder:{user_id}:*")
    now = datetime.now()
    due = []
    for k in keys:
        reminder = r.hgetall(k)
        reminder_time = datetime.fromisoformat(reminder["time"])
        if reminder_time <= now:
            due.append(reminder["message"])
            r.delete(k)
    if due:
        return f"🔔 Reminders: " + ", ".join(due)
    return None

# -------------------- Notes --------------------
@celery_app.task(name="tasks.add_note")
def add_note(note: str, user_id="default"):
    r = get_redis_client()
    note_id = f"note:{user_id}:{datetime.now().timestamp()}"
    r.set(note_id, note)
    return f"📝 Note saved: {note}"

@celery_app.task(name="tasks.get_notes")
def get_notes(user_id="default"):
    r = get_redis_client() # <-- The function failing to import
    keys = r.keys(f"note:{user_id}:*")
    notes = [r.get(k) for k in keys]
    if not notes:
        return "No notes found."
    return "📒 Notes:\n" + "\n".join(f"- {n}" for n in notes)

# -------------------- Weather --------------------
@celery_app.task(name="tasks.get_weather")
def get_weather(city: str):
    # Use config variable directly
    api_key = OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url).json()
    if res.get("cod") != 200:
        return f"❌ Could not fetch weather for {city}"
    temp = res["main"]["temp"]
    desc = res["weather"][0]["description"]
    return f"🌤️ Weather in {city}: {temp}°C, {desc}"

# -------------------- Web Search --------------------
@celery_app.task(name="tasks.web_search")
def web_search(query: str):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    res = requests.get(url).json()
    answer = res.get("AbstractText") or res.get("Heading") or "No direct answer found."
    return f"🔍 Search result: {answer}"

# -------------------- Email --------------------
@celery_app.task(name="tasks.send_email")
def send_email(to_email: str, subject: str, body: str):
    # Use config variables directly
    from_email = EMAIL_USER
    password = EMAIL_PASS
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        return f"📧 Email sent to {to_email}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"

# -------------------- Calculator --------------------
@celery_app.task(name="tasks.calculate")
def calculate(expression: str):
    try:
        # NOTE: eval is dangerous, but keeping original logic
        result = eval(expression, {"__builtins__": None, "math": math})
        return f"🧮 {expression} = {result}"
    except Exception:
        return "❌ Invalid math expression."
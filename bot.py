import os
import requests
from scraper import get_all_tenders

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HISTORY_FILE = "sent_history.txt"

def load_sent_history():
    """قراءة السجل لمنع تكرار الإرسال"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_sent_id(item_id):
    """حفظ المعرف في السجل"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{item_id}\n")

def send_telegram_message(text):
    """إرسال التنبيه إلى قناة التليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ في إرسال التليجرام: {e}")
        return False

def run_bot():
    sent_ids = load_sent_history()
    tenders = get_all_tenders()
    
    new_count = 0
    for tender in tenders:
        tender_id = tender["id"]
        if tender_id not in sent_ids:
            message = (
                f"🏥 <b>{tender['title']}</b>\n\n"
                f"📌 <b>المصدر:</b> {tender['source']}\n"
                f"🔗 <a href='{tender['link']}'>رابط التفاصيل والمصدر</a>"
            )
            if send_telegram_message(message):
                save_sent_id(tender_id)
                sent_ids.add(tender_id)
                new_count += 1
                
    print(f"تم تنفيذ البوت بنجاح. عدد التنبيهات الجديدة: {new_count}")

if __name__ == "__main__":
    run_bot()

import os
import requests

# استدعاء دالة السحب من ملف scraper.py
from scraper import fetch_tenders

# تعيين بيانات البوت والقناة
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID_HERE")

def send_telegram_message(message):
    """
    دالة لإرسال رسالة نصية إلى تليجرام
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("تم إرسال التنبيه إلى تليجرام بنجاح!")
        else:
            print(f"فشل الإرسال: {response.text}")
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال: {e}")

def main():
    # 1. جلب المناقصات باستخدام السكرابر
    target_url = "https://example.com"
    tenders = fetch_tenders(target_url)
    
    # 2. إرسال ملخص أو تنبيه للتليجرام
    if tenders:
        for tender in tenders:
            message = f"📢 **مناقصة جديدة!**\n\n{tender}"
            send_telegram_message(message)
    else:
        # رسالة تجريبية للتأكد من عمل البوت
        send_telegram_message(" البوت يعمل بنجاح، وجاري مراقبة المناقصات الجديدة!")

if name == "__main__":
    main()

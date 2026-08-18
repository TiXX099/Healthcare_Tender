import os
import asyncio
from telegram import Bot
from scraper import fetch_tenders

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHAT_ID")
HISTORY_FILE = "sent_history.txt"

def load_sent_history():
    """تحميل سجل الأخبار التي تم نشرها سابقاً"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(tender_text):
    """إضافة الخبر الجديد للسجل لمنع تكراره مستقبلاً"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(tender_text.replace("\n", " ") + "\n")

async def send_to_channel():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("خطأ: لم يتم ضبط التوكن أو معرّف القناة!")
        return

    bot = Bot(token=BOT_TOKEN)
    tenders = fetch_tenders()
    
    if not tenders:
        print("لا توجد مناقصات مطابقة حالياً.")
        return

    sent_history = load_sent_history()
    new_tenders_count = 0

    for tender in tenders:
        tender_clean = tender.replace("\n", " ")
        # فحص هل تم نشر الخبر سابقاً في القناة
        if tender_clean in sent_history:
            continue

        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=tender,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            save_to_history(tender)
            new_tenders_count += 1
            await asyncio.sleep(2)
        except Exception as e:
            print(f"خطأ أثناء النشر في القناة: {e}")

    print(f"✨ تم نشر {new_tenders_count} خبر جديد في القناة دون تكرار.")

def main():
    asyncio.run(send_to_channel())

if __name__ == "__main__":
    main()

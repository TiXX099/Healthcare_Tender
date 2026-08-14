import os
import asyncio
from telegram import Bot
from scraper import fetch_tenders

# يقرأ التوكن سواء كان اسمه BOT_TOKEN أو TELEGRAM_TOKEN في ملف الورك فلو
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_updates():
    if not BOT_TOKEN:
        print("خطأ: لم يتم العثور على التوكن!")
        return

    bot = Bot(token=BOT_TOKEN)
    tenders = fetch_tenders()
    
    if not tenders:
        print("لا توجد تحديثات جديدة.")
        return

    for tender in tenders:
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=tender,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            await asyncio.sleep(1)
        except Exception as e:
            print(f"خطأ أثناء الإرسال: {e}")

def main():
    asyncio.run(send_updates())

if __name__ == "__main__":
    main()

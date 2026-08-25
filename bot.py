"""
bot.py
------
يشغّل السكرابر، يفلتر الأخبار الجديدة (غير المُرسلة سابقًا)، ويرسلها إلى
قناة التليجرام عبر مكتبة python-telegram-bot (async).

المتغيرات المطلوبة في البيئة (Environment Variables):
    TELEGRAM_BOT_TOKEN   -> توكن البوت من BotFather
    TELEGRAM_CHANNEL_ID  -> معرف القناة، مثال: @my_channel أو -1001234567890
"""

import asyncio
import os

from telegram import Bot
from telegram.constants import ParseMode

from scraper import get_all_tenders

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
HISTORY_FILE = "sent_history.txt"


def load_sent_ids() -> set:
    """يقرأ ملف sent_history.txt (سطر لكل معرف/hash تم إرساله سابقًا)"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_sent_id(item_id: str) -> None:
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(item_id + "\n")


def build_message(item: dict) -> str:
    text = "📢 <b>مناقصة / خبر طبي جديد</b>\n\n"
    text += f"📝 {item['title']}\n"
    if item.get("source"):
        text += f"🏷️ المصدر: {item['source']}\n"
    text += f"\n🔗 {item['link']}"
    return text


async def send_new_tenders() -> None:
    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError(
            "لم يتم تعيين TELEGRAM_BOT_TOKEN أو TELEGRAM_CHANNEL_ID في متغيرات البيئة"
        )

    bot = Bot(token=BOT_TOKEN)
    sent_ids = load_sent_ids()

    print("🔎 جاري البحث عن أخبار مناقصات طبية جديدة...")
    all_items = get_all_tenders()
    new_items = [item for item in all_items if item["id"] not in sent_ids]

    print(f"📊 إجمالي العناصر: {len(all_items)} | جديدة: {len(new_items)}")

    sent_count = 0
    for item in new_items:
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=build_message(item),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            append_sent_id(item["id"])
            sent_count += 1
            await asyncio.sleep(1.5)  # تجنب حدود التليجرام لمعدل الإرسال
        except Exception as e:
            print(f"⚠️ خطأ أثناء إرسال عنصر: {e}")

    print(f"✅ تم إرسال {sent_count} خبر/مناقصة جديدة إلى القناة")


def main() -> None:
    asyncio.run(send_new_tenders())


if __name__ == "__main__":
    main()

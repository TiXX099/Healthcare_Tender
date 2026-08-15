import os
import json
import html
import asyncio
import logging
 
from telegram import Bot
from telegram.constants import ParseMode
 
from scraper import fetch_all_tenders
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("tenders_bot")
 
# يقرأ التوكن والآيدي بأي اسم متغير بيئة متاح
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
 
SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_tenders.json")
MAX_SEEN_HISTORY = 1000
 
 
# ---------------------------------------------------------------------------
# منع تكرار الإرسال
# ---------------------------------------------------------------------------
def load_seen_links() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError):
        log.warning("تعذر قراءة ملف السجل، سيتم البدء بسجل فارغ.")
        return set()
 
 
def save_seen_links(seen: set):
    trimmed = list(seen)[-MAX_SEEN_HISTORY:]
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False)
 
 
# ---------------------------------------------------------------------------
# تنسيق الرسالة
# ---------------------------------------------------------------------------
def format_message(tender: dict) -> str:
    """
    HTML بدل Markdown: تليجرام صارم جدًا مع رموز Markdown، وأي نجمة أو
    شرطة سفلية داخل عنوان المناقصة (شائعة بالعربي) تكسر الرسالة كاملة.
    HTML يحتاج فقط escape للنص العادي.
    """
    source = html.escape(tender["source"])
    title = html.escape(tender["title"])
    link = tender["link"]
 
    return (
        f"🏥 <b>{source}</b>\n"
        f"📌 {title}\n"
        f'🔗 <a href="{link}">فتح تفاصيل المنافسة</a>'
    )
 
 
# ---------------------------------------------------------------------------
# الإرسال
# ---------------------------------------------------------------------------
async def send_updates():
    if not BOT_TOKEN:
        log.error("لم يتم العثور على التوكن! تأكد من ضبط BOT_TOKEN.")
        return
    if not CHAT_ID:
        log.error("لم يتم العثور على CHAT_ID!")
        return
 
    bot = Bot(token=BOT_TOKEN)
 
    # fetch_all_tenders() ترجع list of dict، مو نصوص جاهزة —
    # هذا هو الفرق الجوهري عن النسخة القديمة اللي كانت تفترض tender = نص
    tenders = fetch_all_tenders()
 
    if not tenders:
        log.info("لا توجد مناقصات من أي مصدر حاليًا.")
        return
 
    seen = load_seen_links()
    new_tenders = [t for t in tenders if t["link"] not in seen]
 
    if not new_tenders:
        log.info("لا توجد تحديثات جديدة.")
        return
 
    log.info("عدد المناقصات الجديدة: %d", len(new_tenders))
 
    for tender in new_tenders:
        text = format_message(tender)
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            seen.add(tender["link"])
            log.info("تم الإرسال: %s", tender["title"][:60])
        except Exception as e:
            log.error("خطأ أثناء الإرسال: %s", e)
 
        await asyncio.sleep(1)
 
    save_seen_links(seen)

 
def main():
    asyncio.run(send_updates())
 
 
if __name__ == "__main__":
    main()
 

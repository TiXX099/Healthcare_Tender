import os
import asyncio
from html import escape
from telegram import Bot
from scraper import fetch_tenders


BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHAT_ID")

HISTORY_FILE = "sent_history.txt"


def load_sent_history():
    """
    تحميل روابط الأخبار التي سبق إرسالها.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return set(
                line.strip()
                for line in file
                if line.strip()
            )

    return set()


def save_to_history(link):
    """
    حفظ رابط الخبر لمنع تكراره مستقبلاً.
    """
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(link.strip() + "\n")


def format_message(tender):
    """
    تحويل بيانات المناقصة إلى رسالة Telegram احترافية.
    """

    title = escape(tender.get("title", "بدون عنوان"))
    link = tender.get("link", "")
    category = escape(
        tender.get("category", "🏥 قطاع صحي")
    )

    score = tender.get("score", 0)
    source = escape(
        tender.get("source", "Google News")
    )

    published_at = escape(
        tender.get("published_at", "")
    )

    # --------------------------------------------------------
    # تحديد مستوى الأهمية
    # --------------------------------------------------------

    if score >= 80:
        priority = "🔥 عالية الأهمية"
    elif score >= 60:
        priority = "🟢 ذات صلة"
    else:
        priority = "🟡 محتملة"

    # --------------------------------------------------------
    # إنشاء الرسالة
    # --------------------------------------------------------

    message = (
        "🏥 <b>فرصة صحية جديدة</b>\n\n"
        f"📌 <b>{title}</b>\n\n"
        f"📂 <b>التصنيف:</b> {category}\n"
        f"🎯 <b>درجة الصلة:</b> {score}/100\n"
        f"⚡ <b>الأولوية:</b> {priority}\n"
    )

    if published_at:
        message += f"🕐 <b>تاريخ النشر:</b> {published_at}\n"

    message += (
        f"📰 <b>المصدر:</b> {source}\n\n"
        f'🔗 <a href="{escape(link, quote=True)}">'
        "التفاصيل والمصدر"
        "</a>"
    )

    return message


async def send_to_channel():

    # --------------------------------------------------------
    # التحقق من Secrets
    # --------------------------------------------------------

    if not BOT_TOKEN or not CHANNEL_ID:
        print(
            "❌ خطأ: لم يتم ضبط BOT_TOKEN/TELEGRAM_TOKEN "
            "أو CHAT_ID في GitHub Secrets!"
        )
        return

    print("🚀 Starting Tender Bot...")

    # --------------------------------------------------------
    # إنشاء Bot
    # --------------------------------------------------------

    bot = Bot(token=BOT_TOKEN)

    # --------------------------------------------------------
    # جلب المناقصات
    # --------------------------------------------------------

    print("🔎 Fetching tenders...")

    tenders = fetch_tenders()

    if not tenders:
        print(
            "⚠️ لم يتم العثور على فرص جديدة مطابقة للشروط."
        )
        return

    print(
        f"📊 Found {len(tenders)} relevant opportunities."
    )

    # --------------------------------------------------------
    # تحميل سجل الروابط السابقة
    # --------------------------------------------------------

    sent_history = load_sent_history()

    new_count = 0
    duplicate_count = 0
    error_count = 0

    # --------------------------------------------------------
    # إرسال النتائج
    # --------------------------------------------------------

    for tender in tenders:

        link = tender.get("link", "").strip()

        if not link:
            print("⚠️ Skipping tender without link.")
            continue

        # ----------------------------------------------------
        # منع التكرار باستخدام الرابط
        # ----------------------------------------------------

        if link in sent_history:
            duplicate_count += 1
            print(
                f"⏭️ Already sent: {tender.get('title', '')}"
            )
            continue

        # ----------------------------------------------------
        # تجهيز الرسالة
        # ----------------------------------------------------

        message = format_message(tender)

        try:

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            # ------------------------------------------------
            # حفظ الرابط بعد نجاح الإرسال فقط
            # ------------------------------------------------

            save_to_history(link)
            sent_history.add(link)

            new_count += 1

            print(
                f"✅ Sent: {tender.get('title', '')}"
            )

            # عدم إرسال الرسائل بسرعة
            await asyncio.sleep(2)

        except Exception as error:

            error_count += 1

            print(
                f"❌ Telegram error: {error}"
            )

    # --------------------------------------------------------
    # ملخص التشغيل
    # --------------------------------------------------------

    print("\n" + "=" * 50)
    print("📊 BOT RUN SUMMARY")
    print("=" * 50)
    print(f"🔎 Total found: {len(tenders)}")
    print(f"✅ New sent: {new_count}")
    print(f"⏭️ Duplicates: {duplicate_count}")
    print(f"❌ Errors: {error_count}")
    print("=" * 50)


def main():
    asyncio.run(send_to_channel())


if __name__ == "__main__":
    main()

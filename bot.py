import os
import asyncio

from telegram import Bot
from scraper import fetch_tenders


BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
)

CHANNEL_ID = os.getenv("CHAT_ID")

HISTORY_FILE = "sent_history.txt"


# ============================================================
# قراءة سجل الأخبار المرسلة
# ============================================================

def load_sent_history():

    if not os.path.exists(HISTORY_FILE):
        return set()

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return set(
            line.strip()
            for line in f
            if line.strip()
        )


# ============================================================
# حفظ معرف الخبر
# ============================================================

def save_to_history(key):

    with open(
        HISTORY_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(key + "\n")


# ============================================================
# إنشاء مفتاح ثابت للخبر
# ============================================================

def get_history_key(tender):

    # الرابط هو أفضل معرف لمنع التكرار
    link = tender.get("link", "").strip()

    if link:
        return link

    # احتياطياً نستخدم العنوان
    title = tender.get(
        "title",
        ""
    ).strip()

    return title


# ============================================================
# إنشاء رسالة Telegram
# ============================================================

def format_message(tender):

    title = tender.get(
        "title",
        ""
    )

    link = tender.get(
        "link",
        ""
    )

    category = tender.get(
        "category",
        "توريدات صحية"
    )

    published_at = tender.get(
        "published_at",
        ""
    )

    source = tender.get(
        "source",
        ""
    )

    message = (
        "🏥 **فرصة صحية جديدة**\n\n"
        f"📌 {title}\n\n"
        f"📂 التصنيف: {category}\n"
    )

    if published_at:
        message += (
            f"🕐 تاريخ النشر: "
            f"{published_at}\n"
        )

    if source:
        message += (
            f"📰 المصدر: {source}\n"
        )

    message += (
        "\n🔗 [التفاصيل والمصدر]"
        f"({link})"
    )

    return message


# ============================================================
# إرسال الأخبار
# ============================================================

async def send_to_channel():

    print("=" * 60)
    print("🚀 HEALTHCARE TENDER BOT STARTED")
    print("=" * 60)

    # --------------------------------------------------------
    # التأكد من Secrets
    # --------------------------------------------------------

    if not BOT_TOKEN:

        print(
            "❌ BOT_TOKEN / TELEGRAM_TOKEN "
            "غير موجود"
        )

        return

    if not CHANNEL_ID:

        print(
            "❌ CHAT_ID غير موجود"
        )

        return

    print("✅ Telegram token found")
    print(
        f"✅ Channel ID: {CHANNEL_ID}"
    )

    # --------------------------------------------------------
    # جلب الأخبار
    # --------------------------------------------------------

    print("\n🔎 Fetching tenders...")

    tenders = fetch_tenders()

    print(
        f"\n📊 Scraper returned: "
        f"{len(tenders)}"
    )

    if not tenders:

        print(
            "⚠️ لا توجد فرص مقبولة حالياً."
        )

        return

    # --------------------------------------------------------
    # قراءة History
    # --------------------------------------------------------

    sent_history = load_sent_history()

    print(
        f"📚 History contains: "
        f"{len(sent_history)} items"
    )

    # --------------------------------------------------------
    # تشغيل البوت
    # --------------------------------------------------------

    bot = Bot(
        token=BOT_TOKEN
    )

    new_count = 0

    for tender in tenders:

        title = tender.get(
            "title",
            ""
        )

        link = tender.get(
            "link",
            ""
        )

        history_key = get_history_key(
            tender
        )

        print("\n--------------------------------")
        print(
            f"📌 Checking: {title}"
        )

        # ----------------------------------------------------
        # منع التكرار
        # ----------------------------------------------------

        if history_key in sent_history:

            print(
                "🔁 SKIPPED: Already sent"
            )

            continue

        # ----------------------------------------------------
        # إنشاء الرسالة
        # ----------------------------------------------------

        message = format_message(
            tender
        )

        try:

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

            # حفظ الرابط مباشرة بعد نجاح الإرسال
            save_to_history(
                history_key
            )

            sent_history.add(
                history_key
            )

            new_count += 1

            print(
                "✅ SENT SUCCESSFULLY"
            )

            # تأخير بسيط بين الرسائل
            await asyncio.sleep(2)

        except Exception as error:

            print(
                f"❌ TELEGRAM ERROR: "
                f"{error}"
            )

    # --------------------------------------------------------
    # النتيجة النهائية
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        f"✅ NEW MESSAGES SENT: "
        f"{new_count}"
    )

    print("=" * 60)


# ============================================================
# Main
# ============================================================

def main():

    asyncio.run(
        send_to_channel()
    )


if __name__ == "__main__":

    main()

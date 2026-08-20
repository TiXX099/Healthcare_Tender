import os
import asyncio
import re
import hashlib

from telegram import Bot
from scraper import fetch_tenders, normalize_title


BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
)

CHANNEL_ID = os.getenv("CHAT_ID")

HISTORY_FILE = "sent_history.txt"


# ============================================================
# إنشاء بصمة العنوان
# ============================================================

def title_hash(title):

    normalized = normalize_title(title)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


# ============================================================
# تحميل سجل الإرسال
# ============================================================

def load_sent_history():

    sent_links = set()
    sent_title_hashes = set()

    if not os.path.exists(HISTORY_FILE):
        return sent_links, sent_title_hashes

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            # ------------------------------------------------
            # السجل الجديد:
            #
            # URL|TITLE_HASH
            # ------------------------------------------------

            if "|" in line:

                parts = line.split("|", 1)

                link = parts[0].strip()
                hash_value = parts[1].strip()

                if link:
                    sent_links.add(link)

                if hash_value:
                    sent_title_hashes.add(
                        hash_value
                    )

                continue

            # ------------------------------------------------
            # دعم السجل القديم
            #
            # نبحث عن أي URL موجود داخل السطر
            # ------------------------------------------------

            urls = re.findall(
                r"https?://\S+",
                line
            )

            for url in urls:

                url = url.rstrip(
                    ")]}>.,"
                )

                sent_links.add(url)

    return sent_links, sent_title_hashes


# ============================================================
# حفظ الخبر في السجل
# ============================================================

def save_to_history(
    link,
    title
):

    hash_value = title_hash(title)

    with open(
        HISTORY_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{link}|{hash_value}\n"
        )


# ============================================================
# إنشاء رسالة Telegram
# ============================================================

def format_message(tender):

    title = tender.get(
        "title",
        "بدون عنوان"
    )

    link = tender.get(
        "link",
        ""
    )

    category = tender.get(
        "category",
        "🏥 قطاع صحي"
    )

    score = tender.get(
        "score",
        0
    )

    source = tender.get(
        "source",
        "Google News"
    )

    published_at = tender.get(
        "published_at",
        ""
    )

    # --------------------------------------------------------
    # الأولوية
    # --------------------------------------------------------

    if score >= 85:
        priority = "🔥 عالية جدًا"

    elif score >= 70:
        priority = "🟢 عالية"

    else:
        priority = "🟡 متوسطة"

    message = (
        "🏥 <b>فرصة صحية جديدة</b>\n\n"
        f"📌 <b>{title}</b>\n\n"
        f"📂 <b>التصنيف:</b> {category}\n"
        f"🎯 <b>درجة الصلة:</b> {score}/100\n"
        f"⚡ <b>الأولوية:</b> {priority}\n"
    )

    if published_at:

        message += (
            f"🕐 <b>تاريخ النشر:</b> "
            f"{published_at}\n"
        )

    message += (
        f"📰 <b>المصدر:</b> {source}\n\n"
        f'🔗 <a href="{link}">'
        "التفاصيل والمصدر"
        "</a>"
    )

    return message


# ============================================================
# إرسال القناة
# ============================================================

async def send_to_channel():

    if not BOT_TOKEN or not CHANNEL_ID:

        print(
            "❌ لم يتم ضبط "
            "BOT_TOKEN/TELEGRAM_TOKEN أو CHAT_ID."
        )

        return

    print(
        "🚀 Starting Healthcare Tender Bot..."
    )

    sent_links, sent_title_hashes = (
        load_sent_history()
    )

    print(
        f"📚 History loaded: "
        f"{len(sent_links)} links / "
        f"{len(sent_title_hashes)} title hashes"
    )

    print(
        "🔎 Fetching new opportunities..."
    )

    tenders = fetch_tenders()

    if not tenders:

        print(
            "⚠️ No relevant opportunities found."
        )

        return

    print(
        f"📊 Candidates found: "
        f"{len(tenders)}"
    )

    bot = Bot(
        token=BOT_TOKEN
    )

    new_count = 0
    duplicate_count = 0
    error_count = 0

    for tender in tenders:

        link = tender.get(
            "link",
            ""
        ).strip()

        title = tender.get(
            "title",
            ""
        ).strip()

        if not link or not title:

            print(
                "⚠️ Skipping incomplete result."
            )

            continue

        current_hash = title_hash(
            title
        )

        # ----------------------------------------------------
        # التحقق من الرابط
        # ----------------------------------------------------

        if link in sent_links:

            duplicate_count += 1

            print(
                f"⏭️ Duplicate URL: {title}"
            )

            continue

        # ----------------------------------------------------
        # التحقق من بصمة العنوان
        # ----------------------------------------------------

        if current_hash in sent_title_hashes:

            duplicate_count += 1

            print(
                f"⏭️ Duplicate title: {title}"
            )

            continue

        # ----------------------------------------------------
        # الرسالة
        # ----------------------------------------------------

        message = format_message(
            tender
        )

        try:

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            # ------------------------------------------------
            # نحفظ فقط بعد نجاح Telegram
            # ------------------------------------------------

            save_to_history(
                link,
                title
            )

            sent_links.add(link)
            sent_title_hashes.add(
                current_hash
            )

            new_count += 1

            print(
                f"✅ Sent: {title}"
            )

            await asyncio.sleep(2)

        except Exception as error:

            error_count += 1

            print(
                f"❌ Telegram error: {error}"
            )

    # ========================================================
    # ملخص التشغيل
    # ========================================================

    print("\n" + "=" * 55)
    print("📊 BOT RUN SUMMARY")
    print("=" * 55)

    print(
        f"🔎 Candidates: {len(tenders)}"
    )

    print(
        f"✅ New sent: {new_count}"
    )

    print(
        f"⏭️ Duplicates skipped: "
        f"{duplicate_count}"
    )

    print(
        f"❌ Errors: {error_count}"
    )

    print("=" * 55)


def main():

    asyncio.run(
        send_to_channel()
    )


if __name__ == "__main__":

    main()

import os


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
)


MAX_HISTORY_ITEMS = int(
    os.getenv(
        "MAX_HISTORY_ITEMS",
        "5000",
    )
)


REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "30",
    )
)


# ============================================================
# Google News
# Broad discovery queries
# Smart filter decides Saudi + Medical + Tender
# ============================================================

GOOGLE_NEWS_QUERIES = [

    # Arabic
    '"منافسة" "مستلزمات طبية"',
    '"مناقصة" "مستلزمات طبية"',
    '"منافسة" "مختبرات"',
    '"مناقصة" "مختبرات"',
    '"توريد" "أجهزة طبية"',
    '"تأمين" "مستلزمات طبية"',
    '"تأمين" "مختبرات"',
    '"شراء" "أجهزة طبية"',
    '"ترسية" "مستلزمات طبية"',
    '"ترسية" "مختبرات"',
    '"طلب عروض" "طبية"',
    '"كواشف" "منافسة"',
    '"محاليل" "منافسة"',
    '"مواد مخبرية" "توريد"',
    '"مستلزمات تشخيصية" "توريد"',

    # English
    '"medical supplies" tender',
    '"medical equipment" tender',
    '"laboratory supplies" tender',
    '"laboratory equipment" procurement',
    '"medical devices" procurement',
    '"diagnostic" procurement',
    '"medical consumables" tender',
    '"laboratory reagents" tender',
    '"healthcare procurement"',
    '"medical procurement" Saudi',
    '"laboratory procurement" Saudi',
]


# ============================================================
# NUPCO
# ============================================================

NUPCO_TENDERS_URL = (
    "https://www.nupco.com/ar/المنافسات/tenders-list/"
)

NUPCO_DOMAIN = "nupco.com"

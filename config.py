import os

# =========================
# Telegram
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# =========================
# General
# =========================

MAX_HISTORY_ITEMS = int(os.getenv("MAX_HISTORY_ITEMS", "5000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# =========================
# Google News
# =========================

GOOGLE_NEWS_QUERIES = [
    # Arabic
    '"منافسة" "مستلزمات طبية" السعودية',
    '"مناقصة" "مستلزمات طبية" السعودية',
    '"منافسة" "مختبرات" السعودية',
    '"مناقصة" "مختبرات" السعودية',
    '"تأمين مستلزمات طبية" السعودية',
    '"تأمين مستلزمات المختبرات" السعودية',
    '"أجهزة طبية" "منافسة" السعودية',
    '"محاليل مختبرية" السعودية',
    '"مواد مخبرية" السعودية',

    # English
    '"medical supplies" tender Saudi Arabia',
    '"laboratory supplies" tender Saudi Arabia',
    '"medical equipment" tender Saudi Arabia',
    '"diagnostic" tender Saudi Arabia',
    '"laboratory" procurement Saudi Arabia',
]

# =========================
# Direct official sources
# =========================

NUPCO_TENDERS_URL = (
    "https://www.nupco.com/ar/المنافسات/tenders-list/"
)

NUPCO_DOMAIN = "nupco.com"

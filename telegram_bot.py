import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


def escape_markdown(text: str) -> str:

    if not text:
        return ""

    characters = r"_*[]()~`>#+-=|{}.!"

    for char in characters:
        text = text.replace(
            char,
            "\\" + char,
        )

    return text


def build_message(item: dict) -> str:

    title = escape_markdown(
        item.get("title", "")
    )

    source = escape_markdown(
        item.get("source", "")
    )

    tender_id = escape_markdown(
        item.get("tender_id", "")
    )

    url = item.get(
        "url",
        "",
    )

    message = (
        "🚨 *فرصة مناقصة طبية جديدة*\n\n"
        f"📌 *العنوان:*\n{title}\n\n"
    )

    if tender_id:
        message += (
            f"🆔 *رقم المنافسة:*\n"
            f"`{tender_id}`\n\n"
        )

    message += (
        f"🏢 *المصدر:* {source}\n\n"
        f"🇸🇦 *النطاق:* السعودية\n"
        f"🏥 *التصنيف:* طبي / مخبري\n\n"
        f"🔗 [فتح المصدر]({url})"
    )

    return message


def send_telegram_message(
    message: str,
) -> bool:

    if not TELEGRAM_BOT_TOKEN:
        print(
            "Telegram token is missing."
        )
        return False

    if not TELEGRAM_CHAT_ID:
        print(
            "Telegram chat ID is missing."
        )
        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False,
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return bool(
            data.get("ok")
        )

    except Exception as e:

        print(
            f"Telegram error: {e}"
        )

        return False


def send_item(item: dict) -> bool:

    message = build_message(
        item
    )

    return send_telegram_message(
        message
    )

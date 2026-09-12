import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


def escape_markdown(text: str) -> str:
    """
    Escape all Telegram MarkdownV2 reserved characters.
    """
    if not text:
        return ""

    characters = r"_*[]()~`>#+-=|{}.!"

    for char in characters:
        text = text.replace(
            char,
            "\\" + char
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
        ""
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
        "🇸🇦 *النطاق:* السعودية\n"
        "🏥 *التصنيف:* طبي / مخبري\n\n"
        f"🔗 [فتح المصدر]({url})"
    )

    return message


def send_telegram_message(
    message: str
) -> bool:

    if not TELEGRAM_BOT_TOKEN:
        print(
            "❌ Telegram token is missing."
        )
        return False

    if not TELEGRAM_CHAT_ID:
        print(
            "❌ Telegram chat ID is missing."
        )
        return False

    telegram_url = (
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
            telegram_url,
            json=payload,
            timeout=30
        )

        print(
            f"Telegram HTTP status: "
            f"{response.status_code}"
        )

        try:
            data = response.json()

        except Exception:

            print(
                "❌ Telegram returned invalid JSON."
            )

            print(
                response.text
            )

            return False

        print(
            f"Telegram response: "
            f"{data}"
        )

        if data.get("ok") is True:

            print(
                "✅ Telegram message sent successfully."
            )

            return True

        print(
            "❌ Telegram rejected the message."
        )

        return False

    except requests.RequestException as e:

        print(
            f"❌ Telegram request error: {e}"
        )

        return False

    except Exception as e:

        print(
            f"❌ Unexpected Telegram error: {e}"
        )

        return False


def send_item(item: dict) -> bool:

    message = build_message(
        item
    )

    return send_telegram_message(
        message
    )


def test_telegram() -> bool:

    print("=" * 60)
    print("Testing Telegram connection...")
    print("=" * 60)

    # Every MarkdownV2 reserved character
    # is escaped before sending.
    test_message = (
        "✅ *Saudi Healthcare Tender Bot*\n\n"
        "Telegram connection test successful\\.\n"
        "البوت متصل بالقناة بنجاح\\."
    )

    result = send_telegram_message(
        test_message
    )

    print("=" * 60)

    if result:

        print(
            "✅ TELEGRAM TEST PASSED"
        )

    else:

        print(
            "❌ TELEGRAM TEST FAILED"
        )

    print("=" * 60)

    return result

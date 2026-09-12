import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


# ============================================================
# MarkdownV2 escaping
# ============================================================

def escape_markdown(
    text: str,
) -> str:

    if not text:

        return ""

    characters = (
        r"_*[]()~`>#+-=|{}.!"
    )

    for char in characters:

        text = text.replace(
            char,
            "\\" + char,
        )

    return text


# ============================================================
# Category labels
# ============================================================

def get_category_label(
    category: str,
) -> str:

    categories = {

        "مختبرات":
            "🧪 مختبرات",

        "مستلزمات طبية":
            "🩺 مستلزمات طبية",

        "أجهزة ومعدات طبية":
            "⚙️ أجهزة ومعدات طبية",

        "تشخيص":
            "🔬 تشخيص",
    }

    return categories.get(
        category,
        "🏥 طبي",
    )


# ============================================================
# Build Telegram message
# ============================================================

def build_message(
    item: dict,
) -> str:

    title = escape_markdown(
        item.get(
            "title",
            "",
        )
    )

    source = escape_markdown(
        item.get(
            "source",
            "",
        )
    )

    tender_id = escape_markdown(
        item.get(
            "tender_id",
            "",
        )
    )

    category = get_category_label(
        item.get(
            "category",
            "",
        )
    )

    url = item.get(
        "url",
        "",
    )

    message = (
        "🚨 *فرصة مناقصة طبية جديدة*\n\n"

        "📌 *العنوان:*\n"
        f"{title}\n\n"
    )

    if tender_id:

        message += (
            "🆔 *رقم المنافسة:*\n"
            f"`{tender_id}`\n\n"
        )

    message += (
        f"🏢 *المصدر:* "
        f"{source}\n\n"

        "🇸🇦 *النطاق:* السعودية\n"

        f"🏥 *التصنيف:* "
        f"{category}\n\n"

        f"🔗 [فتح المصدر]({url})"
    )

    return message


# ============================================================
# Send Telegram message
# ============================================================

def send_telegram_message(
    message: str,
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
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {

        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,

        "parse_mode":
            "MarkdownV2",

        "disable_web_page_preview":
            False,
    }

    try:

        response = requests.post(
            telegram_url,
            json=payload,
            timeout=30,
        )

        print(
            "Telegram HTTP status: "
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
            "Telegram response: "
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


# ============================================================
# Send tender item
# ============================================================

def send_item(
    item: dict,
) -> bool:

    message = build_message(
        item
    )

    return send_telegram_message(
        message
    )


# ============================================================
# Manual Telegram test
# ============================================================

def test_telegram() -> bool:

    print(
        "=" * 60
    )

    print(
        "Testing Telegram connection..."
    )

    print(
        "=" * 60
    )

    test_message = (
        "✅ *Saudi Healthcare Tender Bot*\n\n"
        "Telegram connection test successful\\.\n"
        "البوت متصل بالقناة بنجاح\\."
    )

    result = send_telegram_message(
        test_message
    )

    print(
        "=" * 60
    )

    if result:

        print(
            "✅ TELEGRAM TEST PASSED"
        )

    else:

        print(
            "❌ TELEGRAM TEST FAILED"
        )

    print(
        "=" * 60
    )

    return result

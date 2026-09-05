import hashlib
import json
import os
import re
from datetime import datetime, timezone

HISTORY_FILE = "history.json"


def normalize_for_hash(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"https?://\S+",
        "",
        text,
    )

    text = re.sub(
        r"[^a-z0-9\u0600-\u06ff]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def create_hash(
    title: str,
    url: str = "",
    tender_id: str = "",
) -> str:

    if tender_id:
        raw = normalize_for_hash(
            f"TENDER:{tender_id}"
        )
    else:
        raw = normalize_for_hash(
            f"{title}|{url}"
        )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def load_history() -> dict:

    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

            if isinstance(data, dict):
                return data

    except Exception:
        pass

    return {}


def save_history(history: dict, max_items: int = 5000):

    # Keep newest entries
    items = list(history.items())

    items.sort(
        key=lambda x: x[1].get(
            "saved_at",
            "",
        ),
        reverse=True,
    )

    history = dict(
        items[:max_items]
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=2,
        )


def already_seen(
    history: dict,
    item_hash: str,
) -> bool:

    return item_hash in history


def add_to_history(
    history: dict,
    item_hash: str,
    item: dict,
):

    history[item_hash] = {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "tender_id": item.get("tender_id", ""),
        "saved_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

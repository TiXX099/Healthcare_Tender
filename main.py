from config import MAX_HISTORY_ITEMS

from deduplication import (
    add_to_history,
    already_seen,
    load_history,
    save_history,
)

from scraper import (
    collect_all,
)

from telegram_bot import (
    send_item,
    test_telegram,
)


def main():

    print("=" * 60)
    print("Saudi Healthcare Tender Bot")
    print("=" * 60)

    # Load history
    history = load_history()

    print(
        f"History records: "
        f"{len(history)}"
    )

    # ---------------------------------------------------------
    # Telegram connection test
    # ---------------------------------------------------------
    print()
    print("Testing Telegram connection...")

    telegram_ok = test_telegram()

    if telegram_ok:
        print("✅ Telegram connection is working.")
    else:
        print("❌ Telegram connection failed.")
        print(
            "The bot will continue collecting tenders "
            "so the Telegram error can be diagnosed."
        )

    print()

    # ---------------------------------------------------------
    # Collect tenders
    # ---------------------------------------------------------
    items = collect_all()

    print(
        f"Collected unique items: "
        f"{len(items)}"
    )

    # ---------------------------------------------------------
    # Find new opportunities
    # ---------------------------------------------------------
    new_items = []

    for item in items:

        item_hash = item["hash"]

        if already_seen(
            history,
            item_hash,
        ):

            print(
                f"[SKIP DUPLICATE] "
                f"{item['title']}"
            )

            continue

        new_items.append(
            item
        )

    print(
        f"New opportunities: "
        f"{len(new_items)}"
    )

    # ---------------------------------------------------------
    # Highest relevance first
    # ---------------------------------------------------------
    new_items.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # Send new tenders
    # ---------------------------------------------------------
    sent = 0

    for item in new_items:

        print(
            f"[NEW] "
            f"{item.get('title', '')} "
            f"(score={item.get('score', 0)})"
        )

        success = send_item(
            item
        )

        # IMPORTANT:
        # Keep the original behavior:
        # save item as seen whether sending succeeds or fails.
        add_to_history(
            history,
            item["hash"],
            item,
        )

        if success:
            sent += 1

    # ---------------------------------------------------------
    # Save history
    # ---------------------------------------------------------
    save_history(
        history,
        MAX_HISTORY_ITEMS,
    )

    print()
    print(
        f"Telegram messages sent: "
        f"{sent}"
    )

    print(
        f"History total: "
        f"{len(history)}"
    )

    print("=" * 60)
    print("Bot run completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()

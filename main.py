from config import MAX_HISTORY_ITEMS

from deduplication import (
    add_to_history,
    already_seen,
    load_history,
    save_history,
)

from scraper import collect_all

from telegram_bot import (
    send_item,
    test_telegram,
)


def main():

    print("=" * 60)
    print("Saudi Healthcare Tender Bot")
    print("=" * 60)

    # --------------------------------------------------------
    # Load history
    # --------------------------------------------------------

    history = load_history()

    print(
        f"History records: {len(history)}"
    )

    # --------------------------------------------------------
    # Test Telegram
    # --------------------------------------------------------

    print()
    print("Testing Telegram connection...")

    telegram_ok = test_telegram()

    if telegram_ok:

        print(
            "✅ Telegram connection is working."
        )

    else:

        print(
            "❌ Telegram connection failed."
        )

        print(
            "The bot will continue collecting tenders."
        )

    # --------------------------------------------------------
    # Collect opportunities
    # --------------------------------------------------------

    print()

    items = collect_all()

    print(
        f"Collected unique items: {len(items)}"
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    new_items = []

    for item in items:

        item_hash = item["hash"]

        if already_seen(
            history,
            item_hash,
        ):

            print(
                f"[SKIP DUPLICATE] "
                f"{item.get('title', '')}"
            )

            continue

        new_items.append(item)

    print(
        f"New opportunities: {len(new_items)}"
    )

    # --------------------------------------------------------
    # Sort by smart score
    # --------------------------------------------------------

    new_items.sort(
        key=lambda x: x.get("score", 0),
        reverse=True,
    )

    # --------------------------------------------------------
    # Send to Telegram
    # --------------------------------------------------------

    sent = 0

    for item in new_items:

        print(
            f"[NEW] "
            f"{item.get('title', '')} "
            f"(score={item.get('score', 0)})"
        )

        print(
            f"[REASON] "
            f"{item.get('filter_reason', '')}"
        )

        success = send_item(item)

        # IMPORTANT:
        # Save to history ONLY if Telegram succeeded.
        # This allows failed messages to be retried
        # on the next GitHub Actions run.

        if success:

            sent += 1

            add_to_history(
                history,
                item["hash"],
                item,
            )

        else:

            print(
                f"[NOT SAVED] Telegram failed: "
                f"{item.get('title', '')}"
            )

    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

    save_history(
        history,
        MAX_HISTORY_ITEMS,
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()

    print(
        f"Telegram messages sent: {sent}"
    )

    print(
        f"History total: {len(history)}"
    )

    print("=" * 60)
    print("Bot run completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()

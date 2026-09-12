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
)


def main():

    print("=" * 60)
    print("Saudi Healthcare Tender Bot")
    print("=" * 60)

    history = load_history()

    print(
        f"History records: {len(history)}"
    )

    print()

    # Collect tenders
    items = collect_all()

    print(
        f"Collected unique items: {len(items)}"
    )

    new_items = []

    # Remove previously sent items
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

    # Highest score first
    new_items.sort(
        key=lambda x: x.get("score", 0),
        reverse=True,
    )

    sent = 0

    # Send new opportunities
    for item in new_items:

        print(
            f"[NEW] "
            f"{item.get('title', '')} "
            f"(score={item.get('score', 0)})"
        )

        print(
            f"[CATEGORY] "
            f"{item.get('category', '')}"
        )

        print(
            f"[REASON] "
            f"{item.get('filter_reason', '')}"
        )

        success = send_item(item)

        if success:

            sent += 1

            # Save ONLY after successful Telegram delivery
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

    # Save history
    save_history(
        history,
        MAX_HISTORY_ITEMS,
    )

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

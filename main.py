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
)


def main():

    print("=" * 60)
    print(
        "Saudi Healthcare Tender Bot"
    )
    print("=" * 60)

    history = load_history()

    print(
        f"History records: "
        f"{len(history)}"
    )

    items = collect_all()

    print(
        f"Collected unique items: "
        f"{len(items)}"
    )

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

    # Highest relevance first
    new_items.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True,
    )

    sent = 0

    for item in new_items:

        print(
            f"[NEW] "
            f"{item['title']} "
            f"(score={item['score']})"
        )

        success = send_item(
            item
        )

        # IMPORTANT:
        # Save as seen whether sent successfully
        # or not, to prevent repeated spam.
        #
        # If you want retries on Telegram failure,
        # move add_to_history() inside if success.

        add_to_history(
            history,
            item["hash"],
            item,
        )

        if success:
            sent += 1

    save_history(
        history,
        MAX_HISTORY_ITEMS,
    )

    print(
        f"Telegram messages sent: "
        f"{sent}"
    )

    print(
        f"History total: "
        f"{len(history)}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

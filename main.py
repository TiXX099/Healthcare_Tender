for item in new_items:

    print(
        f"[NEW] "
        f"{item.get('title', '')} "
        f"(score={item.get('score', 0)})"
    )

    success = send_item(
        item
    )

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

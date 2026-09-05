import html
import re
from datetime import datetime, timezone
from urllib.parse import quote, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    GOOGLE_NEWS_QUERIES,
    NUPCO_TENDERS_URL,
    REQUEST_TIMEOUT,
)
from filters import (
    passes_filter,
)
from deduplication import (
    create_hash,
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
}


def clean_text(text: str) -> str:

    if not text:
        return ""

    text = html.unescape(text)

    soup = BeautifulSoup(
        text,
        "html.parser",
    )

    text = soup.get_text(
        " ",
        strip=True,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_tender_id(text: str) -> str:

    match = re.search(
        r"\b((?:NPT|NDP)\d{3,6}/\d{2})\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).upper()

    return ""


def google_news_url(query: str) -> str:

    encoded = quote(query)

    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=ar"
        "&gl=SA"
        "&ceid=SA:ar"
    )


def fetch_google_news():

    results = []

    for query in GOOGLE_NEWS_QUERIES:

        try:

            feed = feedparser.parse(
                google_news_url(query)
            )

            for entry in feed.entries:

                title = clean_text(
                    entry.get("title", "")
                )

                description = clean_text(
                    entry.get("summary", "")
                )

                url = entry.get(
                    "link",
                    "",
                )

                source_name = ""

                if hasattr(entry, "source"):
                    source_name = clean_text(
                        entry.source.get(
                            "title",
                            "",
                        )
                    )

                published = entry.get(
                    "published",
                    "",
                )

                accepted, score, reason = (
                    passes_filter(
                        title=title,
                        description=description,
                        url=url,
                        source=source_name,
                    )
                )

                if not accepted:
                    continue

                tender_id = extract_tender_id(
                    f"{title} {description}"
                )

                item_hash = create_hash(
                    title=title,
                    url=url,
                    tender_id=tender_id,
                )

                results.append({
                    "title": title,
                    "description": description,
                    "url": url,
                    "source": source_name or "Google News",
                    "published": published,
                    "tender_id": tender_id,
                    "score": score,
                    "filter_reason": reason,
                    "hash": item_hash,
                    "collected_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                })

        except Exception as e:

            print(
                f"[Google News] "
                f"Query failed: {query} -> {e}"
            )

    return results


def fetch_nupco():

    results = []

    try:

        response = requests.get(
            NUPCO_TENDERS_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Find links containing /tender/
        links = soup.find_all(
            "a",
            href=True,
        )

        seen_urls = set()

        for link in links:

            href = link.get("href", "").strip()

            if "/tender/" not in href:
                continue

            url = urljoin(
                NUPCO_TENDERS_URL,
                href,
            )

            if url in seen_urls:
                continue

            seen_urls.add(url)

            title = clean_text(
                link.get_text(
                    " ",
                    strip=True,
                )
            )

            if not title:
                continue

            # Get surrounding card text
            parent = link

            for _ in range(4):

                if parent.parent:
                    parent = parent.parent

                card_text = clean_text(
                    parent.get_text(
                        " ",
                        strip=True,
                    )
                )

                if len(card_text) > len(title):
                    break

            description = card_text

            tender_id = extract_tender_id(
                description
            )

            accepted, score, reason = (
                passes_filter(
                    title=title,
                    description=description,
                    url=url,
                    source="NUPCO",
                )
            )

            if not accepted:
                continue

            item_hash = create_hash(
                title=title,
                url=url,
                tender_id=tender_id,
            )

            results.append({
                "title": title,
                "description": description,
                "url": url,
                "source": "NUPCO",
                "published": "",
                "tender_id": tender_id,
                "score": score,
                "filter_reason": reason,
                "hash": item_hash,
                "collected_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            })

    except Exception as e:

        print(
            f"[NUPCO] Failed: {e}"
        )

    return results


def collect_all():

    all_items = []

    print(
        "Collecting NUPCO..."
    )

    all_items.extend(
        fetch_nupco()
    )

    print(
        f"NUPCO accepted: {len(all_items)}"
    )

    print(
        "Collecting Google News..."
    )

    google_items = fetch_google_news()

    print(
        f"Google News accepted: "
        f"{len(google_items)}"
    )

    all_items.extend(
        google_items
    )

    # Remove duplicates within current run
    unique = {}

    for item in all_items:

        key = item["hash"]

        if key not in unique:
            unique[key] = item

    return list(
        unique.values()
    )

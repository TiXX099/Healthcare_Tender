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
    detect_category,
)

from deduplication import (
    create_hash,
)


# ============================================================
# HTTP headers
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": (
        "ar-SA,ar;q=0.9,en;q=0.8"
    ),
}


# ============================================================
# Clean text
# ============================================================

def clean_text(text: str) -> str:

    if not text:
        return ""

    text = html.unescape(
        text
    )

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


# ============================================================
# Extract tender ID
# ============================================================

def extract_tender_id(
    text: str,
) -> str:

    match = re.search(
        r"\b((?:NPT|NDP)\d{3,6}/\d{2})\b",
        text,
        re.IGNORECASE,
    )

    if match:

        return match.group(
            1
        ).upper()

    return ""


# ============================================================
# Google News RSS URL
# ============================================================

def google_news_url(
    query: str,
) -> str:

    encoded = quote(
        query
    )

    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=ar"
        "&gl=SA"
        "&ceid=SA:ar"
    )


# ============================================================
# Google News
# ============================================================

def fetch_google_news():

    results = []

    for query in GOOGLE_NEWS_QUERIES:

        try:

            feed = feedparser.parse(
                google_news_url(query)
            )

            for entry in feed.entries:

                title = clean_text(
                    entry.get(
                        "title",
                        "",
                    )
                )

                description = clean_text(
                    entry.get(
                        "summary",
                        "",
                    )
                )

                url = entry.get(
                    "link",
                    "",
                )

                source_name = ""

                if hasattr(
                    entry,
                    "source",
                ):

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

                # --------------------------------------------
                # Filter
                # --------------------------------------------

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

                # --------------------------------------------
                # Category
                # --------------------------------------------

                category = detect_category(
                    title,
                    description,
                    source_name,
                )[0]

                # --------------------------------------------
                # Tender ID
                # --------------------------------------------

                tender_id = extract_tender_id(
                    f"{title} {description}"
                )

                # --------------------------------------------
                # Hash
                # --------------------------------------------

                item_hash = create_hash(
                    title=title,
                    url=url,
                    tender_id=tender_id,
                )

                # --------------------------------------------
                # Item
                # --------------------------------------------

                results.append({

                    "title": title,

                    "description": description,

                    "url": url,

                    "source": (
                        source_name
                        or "Google News"
                    ),

                    "published": published,

                    "tender_id": tender_id,

                    "category": category,

                    "score": score,

                    "filter_reason": reason,

                    "hash": item_hash,

                    "collected_at": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                })

        except Exception as e:

            print(
                "[Google News] "
                f"Query failed: {query} -> {e}"
            )

    return results


# ============================================================
# NUPCO
# ============================================================

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

        links = soup.find_all(
            "a",
            href=True,
        )

        seen_urls = set()

        for link in links:

            href = link.get(
                "href",
                "",
            ).strip()

            if "/tender/" not in href:

                continue

            url = urljoin(
                NUPCO_TENDERS_URL,
                href,
            )

            if url in seen_urls:

                continue

            seen_urls.add(
                url
            )

            title = clean_text(
                link.get_text(
                    " ",
                    strip=True,
                )
            )

            if not title:

                continue

            # --------------------------------------------
            # Get surrounding tender information
            # --------------------------------------------

            parent = link
            card_text = title

            for _ in range(4):

                if parent.parent:

                    parent = (
                        parent.parent
                    )

                current_text = clean_text(
                    parent.get_text(
                        " ",
                        strip=True,
                    )
                )

                if len(current_text) > len(title):

                    card_text = current_text

                    break

            description = card_text

            # --------------------------------------------
            # Tender ID
            # --------------------------------------------

            tender_id = extract_tender_id(
                description
            )

            # --------------------------------------------
            # Filter
            # --------------------------------------------

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

            # --------------------------------------------
            # Category
            # --------------------------------------------

            category = detect_category(
                title,
                description,
                "NUPCO",
            )[0]

            # --------------------------------------------
            # Hash
            # --------------------------------------------

            item_hash = create_hash(
                title=title,
                url=url,
                tender_id=tender_id,
            )

            # --------------------------------------------
            # Item
            # --------------------------------------------

            results.append({

                "title": title,

                "description": description,

                "url": url,

                "source": "NUPCO",

                "published": "",

                "tender_id": tender_id,

                "category": category,

                "score": score,

                "filter_reason": reason,

                "hash": item_hash,

                "collected_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            })

    except Exception as e:

        print(
            f"[NUPCO] Failed: {e}"
        )

    return results


# ============================================================
# Collect everything
# ============================================================

def collect_all():

    all_items = []

    # --------------------------------------------------------
    # NUPCO
    # --------------------------------------------------------

    print(
        "Collecting NUPCO..."
    )

    nupco_items = fetch_nupco()

    all_items.extend(
        nupco_items
    )

    print(
        f"NUPCO accepted: "
        f"{len(nupco_items)}"
    )

    # --------------------------------------------------------
    # Google News
    # --------------------------------------------------------

    print(
        "Collecting Google News..."
    )

    google_items = (
        fetch_google_news()
    )

    print(
        f"Google News accepted: "
        f"{len(google_items)}"
    )

    all_items.extend(
        google_items
    )

    # --------------------------------------------------------
    # Final duplicate removal
    # --------------------------------------------------------

    unique = {}

    for item in all_items:

        key = item["hash"]

        if key not in unique:

            unique[key] = item

    return list(
        unique.values()
    )

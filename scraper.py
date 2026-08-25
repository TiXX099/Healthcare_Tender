"""
scraper.py
----------
مسؤول عن البحث وجلب أخبار المناقصات/المنافسات الطبية في السعودية
(توريدات طبية، تحاليل، مختبرات، مستلزمات، أجهزة طبية...) من:
  1) Google News RSS
  2) منصة اعتماد الحكومية (tenders.etimad.sa) - تجريبي

يرجع كل مصدر قائمة عناصر بنفس الشكل:
    {"id": "...", "title": "...", "link": "...", "source": "...", "published": "..."}
"""

import hashlib
import urllib.parse
from datetime import datetime

import feedparser
import pytz
import requests

# ==================== إعدادات عامة ====================
TIMEZONE = "Asia/Riyadh"
RIYADH_TZ = pytz.timezone(TIMEZONE)

# ==================== الكلمات المفتاحية ====================
KEYWORDS_AR = [
    "مناقصة طبية",
    "منافسة طبية",
    "مناقصة توريد أدوية",
    "مناقصة مستلزمات طبية",
    "مناقصة تحاليل مخبرية",
    "مناقصة مختبرات طبية",
    "توريد مستلزمات طبية",
    "مناقصة مستشفى",
    "منافسة توريد مستلزمات طبية",
    "مناقصة اجهزة طبية",
    "مناقصة معدات طبية",
    "طرح مناقصة طبية",
    "مناقصة وزارة الصحة",
]

KEYWORDS_EN = [
    "medical tender Saudi Arabia",
    "medical supplies tender KSA",
    "laboratory tender Saudi",
    "hospital tender Saudi Arabia",
    "medical equipment tender Saudi",
    "healthcare procurement Saudi Arabia",
]

ALL_QUERIES = KEYWORDS_AR + KEYWORDS_EN

# يجب أن يحتوي العنوان على واحدة من هذه الكلمات على الأقل حتى نعتبره ذا صلة
RELEVANCE_FILTER = [
    "مناقصة", "منافسة", "توريد", "تحاليل", "مختبر", "مستلزمات طبية",
    "أدوية", "اجهزة طبية", "معدات طبية", "مستشفى", "طرح",
    "tender", "procurement", "medical", "laboratory", "hospital", "supplies",
]

MEDICAL_ACTIVITY_KEYWORDS = ["طبي", "صحي", "دواء", "مستشفى", "مختبر", "تحاليل", "مستلزمات طبية"]

ETIMAD_SEARCH_URL = "https://tenders.etimad.sa/Tender/AllSuppliersTendersForVisitorSearch"
ETIMAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


# ==================== أدوات مساعدة ====================
def _hash_link(link: str) -> str:
    return hashlib.sha256(link.encode("utf-8")).hexdigest()


def _is_relevant(text: str, extra_keywords=None) -> bool:
    keywords = RELEVANCE_FILTER + (extra_keywords or [])
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


# ==================== مصدر 1: Google News ====================
def _make_google_news_url(query: str) -> str:
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=ar&gl=SA&ceid=SA:ar"


def _is_today(pub_date_struct) -> bool:
    if not pub_date_struct:
        return False
    pub_dt_utc = datetime(*pub_date_struct[:6], tzinfo=pytz.UTC)
    pub_dt_riyadh = pub_dt_utc.astimezone(RIYADH_TZ)
    today_riyadh = datetime.now(RIYADH_TZ).date()
    return pub_dt_riyadh.date() == today_riyadh


def fetch_google_news_items() -> list:
    """يرجع أخبار اليوم فقط المتعلقة بمناقصات طبية من Google News RSS"""
    results = []
    seen_links_in_run = set()

    for query in ALL_QUERIES:
        url = _make_google_news_url(query)
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"⚠️ فشل جلب Google News للاستعلام '{query}': {e}")
            continue

        for entry in feed.entries:
            link = entry.get("link", "")
            title = entry.get("title", "").strip()

            if not link or not title:
                continue

            link_hash = _hash_link(link)
            if link_hash in seen_links_in_run:
                continue

            if not _is_today(entry.get("published_parsed")):
                continue

            if not _is_relevant(title):
                continue

            source = ""
            if "source" in entry and hasattr(entry.source, "title"):
                source = entry.source.title
            elif " - " in title:
                source = title.rsplit(" - ", 1)[-1]

            results.append({
                "id": link_hash,
                "title": title,
                "link": link,
                "source": source,
                "published": entry.get("published", ""),
            })
            seen_links_in_run.add(link_hash)

    return results


# ==================== مصدر 2: منصة اعتماد (تجريبي) ====================
def fetch_etimad_items() -> list:
    """
    يحاول جلب المنافسات المنشورة اليوم من منصة اعتماد والمتعلقة بالمجال الطبي.
    ⚠️ تجريبي: الموقع قد يغيّر شكل الـ API بدون إشعار، فالدالة تُرجع قائمة
    فارغة عند أي خطأ بدل ما توقف تنفيذ البوت بالكامل.
    """
    results = []
    try:
        params = {"PageSize": 50, "PageNumber": 1}
        resp = requests.get(ETIMAD_SEARCH_URL, headers=ETIMAD_HEADERS, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠️ تعذر جلب بيانات منصة اعتماد (قد تحتاج مراجعة الكود): {e}")
        return results

    items = data.get("data", []) if isinstance(data, dict) else []
    today_riyadh = datetime.now(RIYADH_TZ).date()

    for item in items:
        title = (item.get("tenderName") or "").strip()
        tender_id = item.get("tenderIdString") or item.get("referenceNumber") or ""
        pub_date_raw = item.get("submitionDate") or item.get("publishDate") or ""

        if not title or not tender_id:
            continue

        if not _is_relevant(title, MEDICAL_ACTIVITY_KEYWORDS):
            continue

        try:
            pub_date = datetime.fromisoformat(pub_date_raw.replace("Z", "")).date()
            if pub_date != today_riyadh:
                continue
        except (ValueError, AttributeError):
            pass

        link = f"https://tenders.etimad.sa/Tender/DetailsForVisitor?STenderId={tender_id}"

        results.append({
            "id": _hash_link(link),
            "title": title,
            "link": link,
            "source": "منصة اعتماد",
            "published": pub_date_raw,
        })

    return results


# ==================== دالة التجميع الرئيسية ====================
def get_all_tenders() -> list:
    """يجمع النتائج من كل المصادر مع إزالة التكرار حسب id"""
    items = fetch_google_news_items() + fetch_etimad_items()
    unique = {}
    for item in items:
        unique[item["id"]] = item
    return list(unique.values())

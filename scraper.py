import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher


# ============================================================
# SETTINGS
# ============================================================

MAX_AGE_DAYS = 7

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ============================================================
# MEDICAL / LABORATORY KEYWORDS
# ============================================================

MEDICAL_KEYWORDS = [
    "مختبر",
    "مختبرات",
    "مختبري",
    "مختبرية",
    "تحاليل",
    "تحليل مخبري",
    "أجهزة مخبرية",
    "معدات مخبرية",
    "مستلزمات مخبرية",
    "مواد مخبرية",
    "كواشف",
    "كاشف",
    "كواشف مخبرية",
    "مواد تشخيصية",
    "تشخيص مخبري",

    "أجهزة طبية",
    "جهاز طبي",
    "معدات طبية",
    "مستلزمات طبية",
    "مستلزمات صحية",
    "مستهلكات طبية",
    "مستهلكات صحية",
    "تجهيزات طبية",
    "معدات صحية",
    "مواد طبية",
    "مستلزمات المستشفيات",

    "أدوية",
    "دواء",
    "دوائية",
    "مستحضرات دوائية",
    "مستحضرات صيدلانية",
    "صيدلية",
    "صيدليات",

    "نوبكو",
    "nupco",

    "laboratory",
    "laboratories",
    "diagnostic",
    "reagents",
]


# ============================================================
# TENDER / PROCUREMENT KEYWORDS
# ============================================================

TENDER_KEYWORDS = [
    "مناقصة",
    "مناقصات",
    "منافسة",
    "منافسات",
    "ترسية",
    "ترسيه",
    "توريد",
    "توريدات",
    "تأمين",
    "شراء",
    "مشتريات",
    "طلب عروض",
    "طلب عرض",
    "طلب تقديم عروض",
    "دعوة لتقديم العروض",
    "دعوة للمنافسة",
    "طرح منافسة",
    "طرح مناقصة",
    "تأهيل الموردين",
    "تأهيل موردين",
    "اتفاقية توريد",
    "عقد توريد",
]


# ============================================================
# EXCLUDED CONTENT
# ============================================================

EXCLUDE_WORDS = [
    "غزة",
    "فلسطين",
    "حرب",
    "سياسة",
    "سياسي",
    "انتخابات",

    "أرباح",
    "سهم",
    "أسهم",
    "البورصة",
    "تداول",

    "الرياضية",
    "رياضة",
    "كرة القدم",
    "دوري",

    "نظافة",
    "حراسة",
    "أمن",

    "إعاشة",
    "وجبات",
    "تغذية",

    "صيانة عامة",
    "صيانة المباني",

    "مقاولات",
    "مقاول",
    "إنشاءات",
    "إنشاء",
    "تشييد",

    "أثاث",

    "سيارات",
    "مركبات",
    "وقود",
    "محروقات",
]


# ============================================================
# SEARCH QUERIES
# ============================================================

QUERIES = [
    '"مناقصة" "مستلزمات طبية" السعودية',
    '"مناقصة" "أجهزة طبية" السعودية',
    '"مناقصة" "أجهزة مخبرية" السعودية',
    '"مناقصة" "كواشف" السعودية',
    '"مناقصة" مختبر السعودية',

    '"منافسة" "مستلزمات طبية" السعودية',
    '"منافسة" "أجهزة طبية" السعودية',
    '"منافسة" "أجهزة مخبرية" السعودية',
    '"منافسة" كواشف السعودية',
    '"منافسة" مختبر السعودية',

    '"توريد" "مستلزمات طبية" السعودية',
    '"توريد" "أجهزة طبية" السعودية',
    '"توريد" "أجهزة مخبرية" السعودية',
    '"توريد" كواشف السعودية',
    '"توريد" مختبر السعودية',

    '"ترسية" "أجهزة طبية" السعودية',
    '"ترسية" "مستلزمات طبية" السعودية',
    '"ترسية" "أجهزة مخبرية" السعودية',
    '"ترسية" كواشف السعودية',

    '"نوبكو" مناقصة السعودية',
    '"نوبكو" منافسة السعودية',
    '"نوبكو" توريد السعودية',
    '"نوبكو" ترسية السعودية',

    '"NUPCO" tender Saudi',

    '"طلب عروض" "أجهزة طبية" السعودية',
    '"طلب عروض" "مستلزمات طبية" السعودية',
    '"طلب عروض" مختبر السعودية',

    '"تأهيل الموردين" طبي السعودية',
    '"تأهيل موردين" طبي السعودية',
]


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# NORMALIZE TITLE
# ============================================================

def normalize_title(title):

    if not title:
        return ""

    text = title.lower()

    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ة", "ه")
    text = text.replace("ى", "ي")

    text = re.sub(
        r"[\u064B-\u065F\u0670]",
        "",
        text
    )

    text = re.sub(
        r"[^\w\s\u0600-\u06FF]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SIMILAR TITLES
# ============================================================

def titles_are_similar(title1, title2):

    a = normalize_title(title1)
    b = normalize_title(title2)

    if not a or not b:
        return False

    if a == b:
        return True

    ratio = SequenceMatcher(
        None,
        a,
        b
    ).ratio()

    return ratio >= 0.88


# ============================================================
# KEYWORD MATCH
# ============================================================

def has_keyword(text, keywords):

    text = text.lower()

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


# ============================================================
# PARSE DATE
# ============================================================

def parse_date(date_text):

    if not date_text:
        return None

    try:

        dt = parsedate_to_datetime(
            date_text
        )

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )

    except Exception:

        return None


# ============================================================
# RECENT NEWS CHECK
# ============================================================

def is_recent(date_text):

    dt = parse_date(date_text)

    if not dt:
        return False

    now = datetime.now(
        timezone.utc
    )

    age = now - dt

    return (
        age >= timedelta(minutes=-5)
        and age <= timedelta(
            days=MAX_AGE_DAYS
        )
    )


# ============================================================
# DATE FORMAT
# ============================================================

def format_date(date_text):

    dt = parse_date(date_text)

    if not dt:
        return ""

    # Saudi Arabia UTC+3
    dt_saudi = dt + timedelta(hours=3)

    return dt_saudi.strftime(
        "%Y-%m-%d %H:%M"
    )


# ============================================================
# FETCH GOOGLE RSS
# ============================================================

def fetch_google_rss(query):

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=MAX_AGE_DAYS)
    ).strftime("%Y-%m-%d")

    final_query = (
        f"{query} after:{cutoff}"
    )

    encoded_query = urllib.parse.quote(
        final_query
    )

    rss_url = (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=ar"
        "&gl=SA"
        "&ceid=SA:ar"
    )

    results = []

    try:

        response = requests.get(
            rss_url,
            headers=HEADERS,
            timeout=15
        )

        print(
            f"   HTTP: {response.status_code}"
        )

        if response.status_code != 200:
            return []

        root = ET.fromstring(
            response.content
        )

        items = root.findall(
            ".//item"
        )

        print(
            f"   Results found: {len(items)}"
        )

        for item in items[:20]:

            title_node = item.find(
                "title"
            )

            link_node = item.find(
                "link"
            )

            description_node = item.find(
                "description"
            )

            date_node = item.find(
                "pubDate"
            )

            source_node = item.find(
                "source"
            )

            title = clean_text(
                title_node.text
                if title_node is not None
                else ""
            )

            link = clean_text(
                link_node.text
                if link_node is not None
                else ""
            )

            description = clean_text(
                description_node.text
                if description_node is not None
                else ""
            )

            pub_date = clean_text(
                date_node.text
                if date_node is not None
                else ""
            )

            source = clean_text(
                source_node.text
                if source_node is not None
                else ""
            )

            if not title or not link:
                continue

            results.append({
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
                "source": source,
                "query": query,
            })

    except Exception as error:

        print(
            f"❌ RSS ERROR: {error}"
        )

    return results


# ============================================================
# VALIDATE OPPORTUNITY
# ============================================================

def is_valid_opportunity(item):

    title = item["title"]
    description = item["description"]
    query = item["query"]

    # نستخدم العنوان + الوصف + الاستعلام
    # لأن الاستعلام نفسه يحدد مجال الخبر
    searchable_text = (
        f"{title} "
        f"{description} "
        f"{query}"
    ).lower()

    # --------------------------------------------------------
    # التاريخ
    # --------------------------------------------------------

    if not is_recent(
        item["pub_date"]
    ):

        print(
            f"⏳ OLD/NO DATE: {title}"
        )

        return False

    # --------------------------------------------------------
    # يجب أن يكون طبي
    # --------------------------------------------------------

    medical = has_keyword(
        searchable_text,
        MEDICAL_KEYWORDS
    )

    if not medical:

        print(
            f"❌ NOT MEDICAL: {title}"
        )

        return False

    # --------------------------------------------------------
    # يجب أن يكون مناقصة / توريد
    # --------------------------------------------------------

    tender = has_keyword(
        searchable_text,
        TENDER_KEYWORDS
    )

    if not tender:

        print(
            f"❌ NOT TENDER: {title}"
        )

        return False

    # --------------------------------------------------------
    # استبعاد المحتوى غير المطلوب
    # --------------------------------------------------------

    excluded = [
        word
        for word in EXCLUDE_WORDS
        if word.lower() in title.lower()
    ]

    if excluded:

        print(
            f"❌ EXCLUDED {excluded}: {title}"
        )

        return False

    return True


# ============================================================
# FETCH TENDERS
# ============================================================

def fetch_tenders():

    accepted = []

    seen_links = set()
    seen_titles = []

    total_results = 0

    for query in QUERIES:

        print()
        print(
            f"🔎 SEARCH: {query}"
        )

        items = fetch_google_rss(
            query
        )

        total_results += len(items)

        for item in items:

            title = item["title"]
            link = item["link"]

            # ------------------------------------------------
            # URL duplicate
            # ------------------------------------------------

            if link in seen_links:

                print(
                    f"🔁 DUPLICATE URL: {title}"
                )

                continue

            # ------------------------------------------------
            # Similar title duplicate
            # ------------------------------------------------

            duplicate = False

            for old_title in seen_titles:

                if titles_are_similar(
                    title,
                    old_title
                ):

                    print(
                        f"🔁 SIMILAR TITLE: {title}"
                    )

                    duplicate = True
                    break

            if duplicate:
                continue

            # ------------------------------------------------
            # Validate
            # ------------------------------------------------

            if not is_valid_opportunity(
                item
            ):
                continue

            # ------------------------------------------------
            # Accept
            # ------------------------------------------------

            seen_links.add(link)
            seen_titles.append(title)

            accepted.append({
                "title": title,
                "link": link,
                "description": item["description"],
                "published_at": format_date(
                    item["pub_date"]
                ),
                "source": item["source"],
            })

            print(
                f"✅ ACCEPTED: {title}"
            )

    print()
    print("=" * 60)
    print(
        f"📊 TOTAL RSS RESULTS: {total_results}"
    )
    print(
        f"✅ FINAL ACCEPTED: {len(accepted)}"
    )
    print("=" * 60)

    return accepted


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    fetch_tenders()

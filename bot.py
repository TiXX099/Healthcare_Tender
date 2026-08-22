import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MAX_AGE_DAYS = 7
MIN_SCORE = 65
TITLE_SIMILARITY_THRESHOLD = 0.88


# ============================================================
# المجال الطبي والمخبري
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
    "كواشف",
    "كاشف",
    "مواد مخبرية",
    "reagents",
    "laboratory",
    "diagnostic",

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

    "أدوية",
    "دواء",
    "مستحضرات دوائية",
    "صيدلية",
    "صيدليات",
    "pharmaceutical",

    "نوبكو",
    "nupco",
]


# ============================================================
# كلمات المناقصات والتوريد
# ============================================================

TENDER_KEYWORDS = [
    "مناقصة",
    "مناقصات",
    "منافسة",
    "منافسات",
    "ترسية",
    "ترسيه",
    "توريد",
    "تأمين",
    "شراء",
    "طلب عروض",
    "طلب تقديم عروض",
    "دعوة لتقديم العروض",
    "دعوة للمنافسة",
    "تأهيل الموردين",
    "تأهيل موردين",
    "طرح منافسة",
    "طرح مناقصة",
]


WEAK_TENDER_KEYWORDS = [
    "عقد",
    "عقود",
    "تجهيز",
    "تجهيزات",
]


# ============================================================
# كلمات يجب استبعادها
# ============================================================

EXCLUDE_WORDS = [
    "غزة",
    "فلسطين",
    "الرياضية",
    "تلاعب",
    "أرباح",
    "سهم",
    "أسهم",
    "البورصة",
    "انتخابات",
    "سياسي",
    "سياسة",
    "حرب",
    "كرة القدم",
    "دوري",

    "تغذية",
    "وجبات",
    "إعاشة",
    "نظافة",
    "حراسة",
    "أمن",
    "صيانة عامة",
    "صيانة المباني",
    "مقاولات",
    "مقاول",
    "إنشاءات",
    "إنشاء",
    "تشييد",
    "مباني",
    "أثاث",
    "سيارات",
    "مركبات",
    "وقود",
    "محروقات",
]


# ============================================================
# البحث
# ============================================================

QUERIES = [
    '"مناقصة" "مستلزمات طبية" السعودية',
    '"مناقصة" "أجهزة طبية" السعودية',
    '"مناقصة" "أجهزة مخبرية" السعودية',
    '"مناقصة" "كواشف" السعودية',

    '"منافسة" "مستلزمات طبية" السعودية',
    '"منافسة" "أجهزة طبية" السعودية',
    '"منافسة" "أجهزة مخبرية" السعودية',
    '"منافسة" "كواشف" السعودية',

    '"توريد" "مستلزمات طبية" السعودية',
    '"توريد" "أجهزة طبية" السعودية',
    '"توريد" "أجهزة مخبرية" السعودية',
    '"توريد" "كواشف" السعودية',

    '"ترسية" "أجهزة طبية" السعودية',
    '"ترسية" "مستلزمات طبية" السعودية',
    '"ترسية" "أجهزة مخبرية" السعودية',
    '"ترسية" "كواشف" السعودية',

    '"نوبكو" مناقصة السعودية',
    '"نوبكو" منافسة السعودية',
    '"نوبكو" توريد السعودية',
    '"NUPCO" tender Saudi',

    '"طلب عروض" "أجهزة طبية" السعودية',
    '"طلب عروض" "مستلزمات طبية" السعودية',

    '"تأهيل الموردين" طبي السعودية',
    '"تأهيل موردين" طبي السعودية',
]


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# توحيد العنوان لمنع التكرار
# ============================================================

def normalize_title(title):
    if not title:
        return ""

    text = title.lower()

    text = re.sub(r"https?://\S+", "", text)

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

    stop_words = {
        "اعلان",
        "اعلن",
        "تعلن",
        "شركة",
        "السعودية",
        "السعودي",
        "اليوم",
        "الجديد",
        "جديدة",
        "عن",
        "في",
        "من",
        "الى",
        "و",
        "مع",
        "ل",
    }

    words = text.split()

    words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)


# ============================================================
# مقارنة العناوين
# ============================================================

def titles_are_similar(title1, title2):

    normalized1 = normalize_title(title1)
    normalized2 = normalize_title(title2)

    if not normalized1 or not normalized2:
        return False

    if normalized1 == normalized2:
        return True

    sequence_ratio = SequenceMatcher(
        None,
        normalized1,
        normalized2
    ).ratio()

    words1 = set(normalized1.split())
    words2 = set(normalized2.split())

    if not words1 or not words2:
        return False

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    jaccard = intersection / union

    if sequence_ratio >= TITLE_SIMILARITY_THRESHOLD:
        return True

    if jaccard >= 0.80 and intersection >= 4:
        return True

    return False


# ============================================================
# التاريخ
# ============================================================

def parse_date(date_text):

    if not date_text:
        return None

    try:
        return parsedate_to_datetime(
            date_text
        ).astimezone(timezone.utc)

    except Exception:
        return None


def is_recent(date_text):

    published = parse_date(date_text)

    # لا يوجد تاريخ موثوق = تجاهل
    if not published:
        return False

    now = datetime.now(timezone.utc)

    age = now - published

    # يمنع التواريخ المستقبلية الغريبة
    if age.total_seconds() < -300:
        return False

    return age <= timedelta(
        days=MAX_AGE_DAYS
    )


def format_date(date_text):

    published = parse_date(date_text)

    if not published:
        return ""

    # السعودية UTC+3
    saudi_time = published + timedelta(hours=3)

    return saudi_time.strftime(
        "%Y-%m-%d %H:%M"
    )


# ============================================================
# البحث عن الكلمات
# ============================================================

def find_matches(text, keywords):

    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


# ============================================================
# حساب داخلي فقط
# ============================================================

def calculate_score(title, description):

    combined = f"{title} {description}".lower()
    title_lower = title.lower()

    medical_matches = find_matches(
        combined,
        MEDICAL_KEYWORDS
    )

    tender_matches = find_matches(
        combined,
        TENDER_KEYWORDS
    )

    weak_tender_matches = find_matches(
        combined,
        WEAK_TENDER_KEYWORDS
    )

    excluded_matches = find_matches(
        combined,
        EXCLUDE_WORDS
    )

    score = 0

    if medical_matches:
        score += 25

    if medical_matches:
        score += 25

    if tender_matches:
        score += 25

    strong_tender_words = [
        "مناقصة",
        "منافسة",
        "ترسية",
        "توريد",
        "طلب عروض",
        "تأهيل الموردين",
        "تأهيل موردين",
    ]

    if any(
        word in title_lower
        for word in strong_tender_words
    ):
        score += 15

    if (
        "نوبكو" in combined
        or "nupco" in combined
    ):
        score += 10

    score -= len(
        excluded_matches
    ) * 20

    score = max(
        0,
        min(score, 100)
    )

    return {
        "score": score,
        "medical_matches": medical_matches,
        "tender_matches": tender_matches,
        "weak_tender_matches": weak_tender_matches,
        "excluded_matches": excluded_matches,
    }


# ============================================================
# القبول النهائي
# ============================================================

def is_valid_opportunity(
    title,
    description,
    analysis
):

    # يجب أن يكون طبي
    if not analysis["medical_matches"]:
        return False

    # يجب أن يكون شراء/توريد/مناقصة
    if not analysis["tender_matches"]:
        return False

    # خدمات عامة مرفوضة
    if analysis["excluded_matches"]:
        return False

    # الحد الأدنى
    if analysis["score"] < MIN_SCORE:
        return False

    return True


# ============================================================
# التصنيف
# ============================================================

def classify_tender(text):

    text = text.lower()

    if (
        "نوبكو" in text
        or "nupco" in text
    ):
        return "🏢 مشتريات نوبكو"

    if any(
        word in text
        for word in [
            "مختبر",
            "مختبرات",
            "تحاليل",
            "كواشف",
            "كاشف",
            "أجهزة مخبرية",
            "معدات مخبرية",
            "مستلزمات مخبرية",
            "reagents",
        ]
    ):
        return "🧪 مختبرات وكواشف"

    if any(
        word in text
        for word in [
            "أجهزة طبية",
            "جهاز طبي",
            "معدات طبية",
            "مستلزمات طبية",
            "مستهلكات طبية",
            "تجهيزات طبية",
        ]
    ):
        return "🔬 أجهزة ومستلزمات طبية"

    if any(
        word in text
        for word in [
            "أدوية",
            "دواء",
            "مستحضرات دوائية",
            "صيدلية",
            "pharmaceutical",
        ]
    ):
        return "💊 أدوية وصيدلة"

    return "🏥 توريدات صحية"


# ============================================================
# Google News RSS
# ============================================================

def fetch_google_rss(query):

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(days=MAX_AGE_DAYS)
    ).strftime("%Y-%m-%d")

    query_with_date = (
        f"{query} after:{cutoff_date}"
    )

    encoded_query = urllib.parse.quote(
        query_with_date
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

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        for item in root.findall(
            ".//item"
        )[:20]:

            title_element = item.find("title")
            link_element = item.find("link")
            description_element = item.find("description")
            pub_date_element = item.find("pubDate")
            source_element = item.find("source")

            title = clean_text(
                title_element.text
                if title_element is not None
                else ""
            )

            link = (
                link_element.text.strip()
                if link_element is not None
                and link_element.text
                else ""
            )

            description = clean_text(
                description_element.text
                if description_element is not None
                else ""
            )

            pub_date = (
                pub_date_element.text.strip()
                if pub_date_element is not None
                and pub_date_element.text
                else ""
            )

            source = (
                source_element.text.strip()
                if source_element is not None
                and source_element.text
                else "Google News"
            )

            if not title or not link:
                continue

            # التاريخ شرط إجباري
            if not is_recent(pub_date):
                print(
                    f"⏳ OLD/INVALID: {title}"
                )
                continue

            results.append({
                "title": title,
                "link": link,
                "description": description,
                "published_at": format_date(pub_date),
                "source": source,
            })

    except requests.RequestException as error:

        print(
            f"❌ RSS request error: {error}"
        )

    except ET.ParseError as error:

        print(
            f"❌ RSS XML error: {error}"
        )

    except Exception as error:

        print(
            f"❌ Unexpected error: {error}"
        )

    return results


# ============================================================
# جلب المناقصات
# ============================================================

def fetch_tenders():

    accepted = []

    seen_links = set()
    seen_titles = []

    for query in QUERIES:

        print(f"\n🔎 SEARCH: {query}")

        items = fetch_google_rss(query)

        for item in items:

            title = item["title"]
            link = item["link"]
            description = item["description"]

            # منع تكرار الرابط
            if link in seen_links:
                print(
                    f"🔁 DUPLICATE URL: {title}"
                )
                continue

            # منع العنوان المشابه
            duplicate = False

            for existing_title in seen_titles:

                if titles_are_similar(
                    title,
                    existing_title
                ):
                    duplicate = True

                    print(
                        f"🔁 SIMILAR TITLE: {title}"
                    )

                    break

            if duplicate:
                continue

            analysis = calculate_score(
                title,
                description
            )

            if not is_valid_opportunity(
                title,
                description,
                analysis
            ):
                print(
                    f"❌ REJECTED: {title}"
                )
                continue

            seen_links.add(link)
            seen_titles.append(title)

            category = classify_tender(
                f"{title} {description}"
            )

            accepted.append({
                "title": title,
                "link": link,
                "description": description,
                "published_at": item["published_at"],
                "source": item["source"],
                "category": category,
                "score": analysis["score"],
            })

            print(
                f"✅ ACCEPTED "
                f"[{analysis['score']}/100]: "
                f"{title}"
            )

    accepted.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print("\n" + "=" * 60)
    print(
        f"✅ FINAL ACCEPTED: {len(accepted)}"
    )
    print("=" * 60)

    return accepted


if __name__ == "__main__":
    fetch_tenders()

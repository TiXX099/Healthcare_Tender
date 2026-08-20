import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ============================================================
# إعدادات النظام
# ============================================================

MAX_AGE_DAYS = 7
MIN_SCORE = 60
TITLE_SIMILARITY_THRESHOLD = 0.82


# ============================================================
# الكلمات الطبية
# ============================================================

MEDICAL_KEYWORDS = [
    "مختبر",
    "مختبرات",
    "تحاليل",
    "أجهزة مخبرية",
    "معدات مخبرية",
    "كواشف",
    "كاشف",
    "مستلزمات طبية",
    "مستلزمات صحية",
    "أجهزة طبية",
    "معدات طبية",
    "مستهلكات طبية",
    "مستهلكات صحية",
    "مستشفى",
    "مستشفيات",
    "مركز صحي",
    "مراكز صحية",
    "عيادة",
    "عيادات",
    "رعاية صحية",
    "قطاع صحي",
    "وزارة الصحة",
    "نوبكو",
    "NUPCO",
    "دواء",
    "أدوية",
    "صيدلية",
    "صيدليات",
    "مستلزمات مختبرية",
    "تجهيزات طبية",
    "تجهيزات صحية",
]


# ============================================================
# كلمات المناقصات
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
    "عقد",
    "عقود",
    "تجهيز",
    "تجهيزات",
    "طرح",
    "طرح منافسة",
    "فرصة",
    "طلب عروض",
    "طلب تقديم عروض",
    "عرض سعر",
    "دعوة للمنافسة",
    "دعوة لتقديم العروض",
    "تأهيل",
    "تأهيل الموردين",
]


# ============================================================
# كلمات الاستبعاد
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
    "عسكري",
    "كرة القدم",
    "دوري",
]


# ============================================================
# البحث
# ============================================================

QUERIES = [
    '"مناقصة" "مستلزمات طبية" السعودية',
    '"مناقصة" "أجهزة طبية" السعودية',
    '"مناقصة" "أجهزة مخبرية" السعودية',
    '"منافسة" "مستلزمات طبية" السعودية',
    '"منافسة" "أجهزة طبية" السعودية',
    '"منافسة" "أجهزة مخبرية" السعودية',
    '"توريد" "مستلزمات طبية" السعودية',
    '"توريد" "أجهزة طبية" السعودية',
    '"توريد" "كواشف" السعودية',
    '"ترسية" "أجهزة طبية" السعودية',
    '"ترسية" "مستلزمات طبية" السعودية',
    '"ترسية" مستشفى السعودية',
    '"نوبكو" مناقصة السعودية',
    '"نوبكو" منافسة السعودية',
    '"نوبكو" توريد السعودية',
    '"طلب عروض" "أجهزة طبية" السعودية',
    '"تأهيل الموردين" طبي السعودية',
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
# تنظيف العنوان للمقارنة
# ============================================================

def normalize_title(title):
    if not title:
        return ""

    text = title.lower()

    # إزالة الروابط
    text = re.sub(r"https?://\S+", "", text)

    # إزالة علامات الترقيم
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)

    # إزالة كلمات عامة لا تفيد في مقارنة الأخبار
    stop_words = [
        "شركة",
        "تعلن",
        "إعلان",
        "السعودية",
        "السعودي",
        "اليوم",
        "الجديد",
        "جديدة",
        "توقيع",
        "توقع",
        "عقد",
    ]

    words = text.split()

    words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)


# ============================================================
# مقارنة عنوانين
# ============================================================

def titles_are_similar(title1, title2):
    normalized1 = normalize_title(title1)
    normalized2 = normalize_title(title2)

    if not normalized1 or not normalized2:
        return False

    # تطابق مباشر
    if normalized1 == normalized2:
        return True

    # نسبة التشابه
    similarity = SequenceMatcher(
        None,
        normalized1,
        normalized2
    ).ratio()

    return similarity >= TITLE_SIMILARITY_THRESHOLD


# ============================================================
# التاريخ
# ============================================================

def parse_date(date_text):
    if not date_text:
        return None

    try:
        return parsedate_to_datetime(date_text).astimezone(
            timezone.utc
        )
    except Exception:
        return None


def format_date(date_text):
    dt = parse_date(date_text)

    if not dt:
        return ""

    return dt.strftime("%Y-%m-%d %H:%M")


def is_recent(date_text):
    published = parse_date(date_text)

    if not published:
        # إذا Google لم يعطنا تاريخًا واضحًا
        # لا نحذف الخبر تلقائياً
        return True

    now = datetime.now(timezone.utc)

    age = now - published

    return age <= timedelta(days=MAX_AGE_DAYS)


# ============================================================
# الكلمات الموجودة
# ============================================================

def find_matches(text, keywords):

    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


# ============================================================
# حساب Score
# ============================================================

def calculate_score(title, description):

    title = title or ""
    description = description or ""

    title_lower = title.lower()
    combined_text = f"{title} {description}".lower()

    medical_matches = find_matches(
        combined_text,
        MEDICAL_KEYWORDS
    )

    tender_matches = find_matches(
        combined_text,
        TENDER_KEYWORDS
    )

    excluded_matches = find_matches(
        combined_text,
        EXCLUDE_WORDS
    )

    # --------------------------------------------------------
    # نقاط المجال الصحي
    # --------------------------------------------------------

    medical_score = 0

    if medical_matches:
        medical_score += 25

    # وجود كلمة قوية في العنوان
    strong_medical = [
        "مختبر",
        "كواشف",
        "أجهزة طبية",
        "أجهزة مخبرية",
        "مستلزمات طبية",
        "نوبكو",
        "مستشفى",
    ]

    if any(
        keyword.lower() in title_lower
        for keyword in strong_medical
    ):
        medical_score += 15

    # --------------------------------------------------------
    # نقاط المناقصة
    # --------------------------------------------------------

    tender_score = 0

    if tender_matches:
        tender_score += 25

    strong_tender = [
        "مناقصة",
        "منافسة",
        "ترسية",
        "طلب عروض",
    ]

    if any(
        keyword.lower() in title_lower
        for keyword in strong_tender
    ):
        tender_score += 20

    # --------------------------------------------------------
    # نقاط إضافية
    # --------------------------------------------------------

    extra_score = 0

    if "نوبكو" in combined_text or "nupco" in combined_text:
        extra_score += 10

    if "توريد" in combined_text:
        extra_score += 5

    if "عقد" in combined_text:
        extra_score += 5

    # --------------------------------------------------------
    # مجموع النقاط
    # --------------------------------------------------------

    score = (
        medical_score
        + tender_score
        + extra_score
    )

    # خصم للكلمات غير المرغوبة
    score -= len(excluded_matches) * 25

    # الحد 0 - 100
    score = max(0, min(score, 100))

    return {
        "score": score,
        "medical_matches": medical_matches,
        "tender_matches": tender_matches,
        "excluded_matches": excluded_matches,
    }


# ============================================================
# التصنيف
# ============================================================

def classify_tender(text):

    text = text.lower()

    if any(
        keyword in text
        for keyword in [
            "نوبكو",
            "nupco",
        ]
    ):
        return "🏢 مشتريات نوبكو"

    if any(
        keyword in text
        for keyword in [
            "مختبر",
            "كواشف",
            "تحاليل",
            "أجهزة مخبرية",
            "مستلزمات مختبرية",
        ]
    ):
        return "🧪 مختبرات وتحاليل"

    if any(
        keyword in text
        for keyword in [
            "أجهزة طبية",
            "معدات طبية",
            "تجهيزات طبية",
            "مستهلكات طبية",
            "مستلزمات طبية",
        ]
    ):
        return "🔬 أجهزة ومستلزمات طبية"

    if any(
        keyword in text
        for keyword in [
            "دواء",
            "أدوية",
            "صيدلية",
            "صيدليات",
        ]
    ):
        return "💊 أدوية وصيدلة"

    if any(
        keyword in text
        for keyword in [
            "مستشفى",
            "مستشفيات",
            "مركز صحي",
            "مراكز صحية",
        ]
    ):
        return "🏥 مستشفيات ورعاية صحية"

    return "🏥 قطاع صحي"


# ============================================================
# Google News RSS
# ============================================================

def fetch_google_rss(query):

    encoded_query = urllib.parse.quote(query)

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

        for item in root.findall(".//item")[:20]:

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

            published_at = (
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

            # ------------------------------------------------
            # فلتر التاريخ
            # ------------------------------------------------

            if not is_recent(published_at):
                print(
                    f"⏳ Old news ignored: {title}"
                )
                continue

            results.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "published_at": format_date(
                        published_at
                    ),
                    "source": source,
                }
            )

    except requests.RequestException as error:

        print(
            f"❌ RSS request error: {error}"
        )

    except ET.ParseError as error:

        print(
            f"❌ RSS XML parsing error: {error}"
        )

    except Exception as error:

        print(
            f"❌ Unexpected RSS error: {error}"
        )

    return results


# ============================================================
# جلب المناقصات
# ============================================================

def fetch_tenders():

    all_results = []

    seen_links = set()
    seen_titles = []

    for query in QUERIES:

        print(
            f"\n🔎 Searching: {query}"
        )

        items = fetch_google_rss(query)

        for item in items:

            title = item["title"]
            link = item["link"]
            description = item["description"]

            # ------------------------------------------------
            # منع تكرار الرابط
            # ------------------------------------------------

            if link in seen_links:
                continue

            # ------------------------------------------------
            # منع تكرار العنوان / الخبر
            # ------------------------------------------------

            duplicate_title = False

            for existing_title in seen_titles:

                if titles_are_similar(
                    title,
                    existing_title
                ):
                    duplicate_title = True
                    break

            if duplicate_title:
                print(
                    f"🔁 Duplicate ignored: {title}"
                )
                continue

            # ------------------------------------------------
            # تحليل المحتوى
            # ------------------------------------------------

            analysis = calculate_score(
                title,
                description
            )

            score = analysis["score"]

            has_medical = bool(
                analysis["medical_matches"]
            )

            has_tender = bool(
                analysis["tender_matches"]
            )

            has_excluded = bool(
                analysis["excluded_matches"]
            )

            # ------------------------------------------------
            # شروط القبول
            # ------------------------------------------------

            if not has_medical:
                continue

            if not has_tender:
                continue

            if has_excluded:
                continue

            if score < MIN_SCORE:
                continue

            # ------------------------------------------------
            # تسجيل الخبر المقبول
            # ------------------------------------------------

            seen_links.add(link)
            seen_titles.append(title)

            category = classify_tender(
                f"{title} {description}"
            )

            all_results.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "published_at": item[
                        "published_at"
                    ],
                    "source": item["source"],
                    "category": category,
                    "score": score,
                    "medical_matches": analysis[
                        "medical_matches"
                    ],
                    "tender_matches": analysis[
                        "tender_matches"
                    ],
                }
            )

    # --------------------------------------------------------
    # ترتيب الأعلى Score أولاً
    # --------------------------------------------------------

    all_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print(
        f"\n✅ Final relevant opportunities: "
        f"{len(all_results)}"
    )

    return all_results


# ============================================================
# اختبار مباشر
# ============================================================

if __name__ == "__main__":

    results = fetch_tenders()

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    for index, tender in enumerate(
        results,
        start=1
    ):

        print(
            f"\n#{index}"
        )

        print(
            f"📌 {tender['title']}"
        )

        print(
            f"📂 {tender['category']}"
        )

        print(
            f"🎯 Score: "
            f"{tender['score']}/100"
        )

        print(
            f"📰 {tender['source']}"
        )

        print(
            f"🕐 {tender['published_at']}"
        )

        print(
            f"🔗 {tender['link']}"
        )

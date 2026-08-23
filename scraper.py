import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher


# ============================================================
# إعدادات عامة
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# عمر الخبر المسموح
MAX_AGE_DAYS = 7

# نسبة التشابه لمنع تكرار نفس الخبر بصياغات مختلفة
TITLE_SIMILARITY_THRESHOLD = 0.88


# ============================================================
# كلمات المجال الطبي والمخبري
# ============================================================

MEDICAL_KEYWORDS = [

    # مختبرات
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
    "laboratory",
    "laboratories",
    "diagnostic",
    "reagents",

    # أجهزة ومستلزمات طبية
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
    "تجهيز طبي",

    # الأدوية
    "أدوية",
    "دواء",
    "دوائية",
    "مستحضرات دوائية",
    "مستحضرات صيدلانية",
    "صيدلية",
    "صيدليات",
    "pharmaceutical",

    # نوبكو
    "نوبكو",
    "NUPCO",
]


# ============================================================
# كلمات المناقصات والتوريدات
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
# كلمات تستبعد الأخبار غير المطلوبة
# ============================================================

EXCLUDE_WORDS = [

    # سياسية / عامة
    "غزة",
    "فلسطين",
    "حرب",
    "سياسة",
    "سياسي",
    "انتخابات",

    # مالية وأسهم
    "أرباح",
    "سهم",
    "أسهم",
    "البورصة",
    "تداول",

    # رياضة
    "الرياضية",
    "رياضة",
    "كرة القدم",
    "دوري",

    # خدمات عامة لا نريدها
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
# استعلامات البحث
# ============================================================

QUERIES = [

    # مناقصات
    '"مناقصة" "مستلزمات طبية" السعودية',
    '"مناقصة" "أجهزة طبية" السعودية',
    '"مناقصة" "أجهزة مخبرية" السعودية',
    '"مناقصة" "كواشف" السعودية',
    '"مناقصة" مختبر السعودية',

    # منافسات
    '"منافسة" "مستلزمات طبية" السعودية',
    '"منافسة" "أجهزة طبية" السعودية',
    '"منافسة" "أجهزة مخبرية" السعودية',
    '"منافسة" كواشف السعودية',
    '"منافسة" مختبر السعودية',

    # توريد
    '"توريد" "مستلزمات طبية" السعودية',
    '"توريد" "أجهزة طبية" السعودية',
    '"توريد" "أجهزة مخبرية" السعودية',
    '"توريد" كواشف السعودية',
    '"توريد" مختبر السعودية',

    # ترسية
    '"ترسية" "أجهزة طبية" السعودية',
    '"ترسية" "مستلزمات طبية" السعودية',
    '"ترسية" "أجهزة مخبرية" السعودية',
    '"ترسية" كواشف السعودية',

    # نوبكو
    '"نوبكو" مناقصة السعودية',
    '"نوبكو" منافسة السعودية',
    '"نوبكو" توريد السعودية',
    '"نوبكو" ترسية السعودية',
    '"NUPCO" tender Saudi',

    # طلب عروض
    '"طلب عروض" "أجهزة طبية" السعودية',
    '"طلب عروض" "مستلزمات طبية" السعودية',
    '"طلب عروض" مختبر السعودية',

    # تأهيل
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
# توحيد العنوان
# ============================================================

def normalize_title(title):

    if not title:
        return ""

    text = title.lower()

    # إزالة الروابط
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # توحيد بعض الحروف العربية
    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ة", "ه")
    text = text.replace("ى", "ي")

    # إزالة التشكيل
    text = re.sub(
        r"[\u064B-\u065F\u0670]",
        "",
        text
    )

    # إزالة علامات الترقيم
    text = re.sub(
        r"[^\w\s\u0600-\u06FF]",
        " ",
        text
    )

    # كلمات عامة لا تفيد في مقارنة الأخبار
    stop_words = {
        "اعلان",
        "اعلن",
        "تعلن",
        "شركة",
        "السعودية",
        "السعودي",
        "جديدة",
        "الجديدة",
        "عن",
        "في",
        "من",
        "الى",
        "و",
        "مع",
        "ل",
        "على",
    }

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

    if ratio >= TITLE_SIMILARITY_THRESHOLD:
        return True

    words_a = set(a.split())
    words_b = set(b.split())

    if not words_a or not words_b:
        return False

    intersection = len(
        words_a & words_b
    )

    union = len(
        words_a | words_b
    )

    jaccard = intersection / union

    if jaccard >= 0.80 and intersection >= 4:
        return True

    return False


# ============================================================
# استخراج الكلمات الموجودة
# ============================================================

def find_matches(text, keywords):

    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


# ============================================================
# قراءة تاريخ الخبر
# ============================================================

def parse_date(date_text):

    if not date_text:
        return None

    try:

        parsed = parsedate_to_datetime(
            date_text
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except Exception:

        return None


# ============================================================
# التأكد أن الخبر حديث
# ============================================================

def is_recent(date_text):

    published = parse_date(
        date_text
    )

    if not published:
        return False

    now = datetime.now(
        timezone.utc
    )

    age = now - published

    # الأخبار المستقبلية الغريبة
    if age.total_seconds() < -300:
        return False

    return age <= timedelta(
        days=MAX_AGE_DAYS
    )


# ============================================================
# تنسيق التاريخ
# ============================================================

def format_date(date_text):

    published = parse_date(
        date_text
    )

    if not published:
        return ""

    # توقيت السعودية UTC+3
    saudi_time = (
        published + timedelta(hours=3)
    )

    return saudi_time.strftime(
        "%Y-%m-%d %H:%M"
    )


# ============================================================
# تصنيف داخلي
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
# تحميل Google News RSS
# ============================================================

def fetch_google_rss(query):

    # نطلب فقط الأخبار المنشورة خلال الفترة المطلوبة
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

        items = root.findall(
            ".//item"
        )

        for item in items[:20]:

            title_element = item.find(
                "title"
            )

            link_element = item.find(
                "link"
            )

            description_element = (
                item.find("description")
            )

            pub_date_element = (
                item.find("pubDate")
            )

            source_element = (
                item.find("source")
            )

            title = clean_text(
                title_element.text
                if title_element is not None
                else ""
            )

            link = (
                link_element.text.strip()
                if (
                    link_element is not None
                    and link_element.text
                )
                else ""
            )

            description = clean_text(
                description_element.text
                if description_element is not None
                else ""
            )

            pub_date = (
                pub_date_element.text.strip()
                if (
                    pub_date_element is not None
                    and pub_date_element.text
                )
                else ""
            )

            source = (
                source_element.text.strip()
                if (
                    source_element is not None
                    and source_element.text
                )
                else "Google News"
            )

            if not title or not link:
                continue

            # التاريخ شرط أساسي
            if not is_recent(pub_date):

                print(
                    f"⏳ OLD: {title}"
                )

                continue

            results.append({
                "title": title,
                "link": link,
                "description": description,
                "published_at": format_date(
                    pub_date
                ),
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
# التحقق من أن الخبر فرصة طبية فعلًا
# ============================================================

def is_valid_opportunity(
    title,
    description
):

    # ندمج العنوان والوصف
    combined_text = (
        f"{title} {description}"
    ).lower()

    # ---------------------------------------------
    # 1. يجب وجود كلمة طبية
    # ---------------------------------------------

    medical_matches = find_matches(
        combined_text,
        MEDICAL_KEYWORDS
    )

    if not medical_matches:

        print(
            f"❌ NOT MEDICAL: {title}"
        )

        return False

    # ---------------------------------------------
    # 2. يجب وجود كلمة مناقصة/توريد
    # ---------------------------------------------

    tender_matches = find_matches(
        combined_text,
        TENDER_KEYWORDS
    )

    if not tender_matches:

        print(
            f"❌ NOT TENDER: {title}"
        )

        return False

    # ---------------------------------------------
    # 3. الكلمات المستبعدة
    # ---------------------------------------------

    excluded_matches = find_matches(
        combined_text,
        EXCLUDE_WORDS
    )

    if excluded_matches:

        print(
            f"❌ EXCLUDED "
            f"{excluded_matches}: "
            f"{title}"
        )

        return False

    # ---------------------------------------------
    # 4. إذا كان الخبر عن نوبكو
    # نسمح به إذا كان مرتبطًا بمناقصة/شراء/توريد
    # ---------------------------------------------

    if (
        "نوبكو" in combined_text
        or "nupco" in combined_text
    ):

        return True

    # ---------------------------------------------
    # 5. قبول الخبر
    # ---------------------------------------------

    return True


# ============================================================
# جلب جميع الفرص
# ============================================================

def fetch_tenders():

    accepted = []

    seen_links = set()
    seen_titles = []

    for query in QUERIES:

        print(
            f"\n🔎 SEARCH: {query}"
        )

        items = fetch_google_rss(
            query
        )

        if not items:

            print(
                "   ↳ No results"
            )

            continue

        for item in items:

            title = item[
                "title"
            ]

            link = item[
                "link"
            ]

            description = item[
                "description"
            ]

            # =========================================
            # منع تكرار الرابط
            # =========================================

            if link in seen_links:

                print(
                    f"🔁 DUPLICATE URL: "
                    f"{title}"
                )

                continue

            # =========================================
            # منع تكرار العنوان
            # =========================================

            duplicate = False

            for old_title in seen_titles:

                if titles_are_similar(
                    title,
                    old_title
                ):

                    duplicate = True

                    print(
                        f"🔁 SIMILAR TITLE: "
                        f"{title}"
                    )

                    break

            if duplicate:
                continue

            # =========================================
            # الفلترة
            # =========================================

            if not is_valid_opportunity(
                title,
                description
            ):

                continue

            # =========================================
            # قبول الخبر
            # =========================================

            seen_links.add(
                link
            )

            seen_titles.append(
                title
            )

            category = classify_tender(
                f"{title} {description}"
            )

            accepted.append({
                "title": title,
                "link": link,
                "description": description,
                "published_at": item[
                    "published_at"
                ],
                "source": item[
                    "source"
                ],
                "category": category,
            })

            print(
                f"✅ ACCEPTED: {title}"
            )

    # ترتيب الأحدث أولاً
    accepted.sort(
        key=lambda x: x.get(
            "published_at",
            ""
        ),
        reverse=True
    )

    print("\n" + "=" * 60)

    print(
        f"✅ FINAL ACCEPTED: "
        f"{len(accepted)}"
    )

    print("=" * 60)

    return accepted


# ============================================================
# تشغيل مباشر للاختبار
# ============================================================

if __name__ == "__main__":

    fetch_tenders()

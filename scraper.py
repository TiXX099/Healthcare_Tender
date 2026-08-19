import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re
from email.utils import parsedate_to_datetime


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ============================================================
# الكلمات الطبية والصحية
# ============================================================

MEDICAL_KEYWORDS = [
    "مختبر",
    "مختبرات",
    "مختبري",
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
    "الصحة",
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
# كلمات المناقصات والفرص
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
# Queries
# ============================================================

QUERIES = [
    '"مناقصة" مستلزمات طبية السعودية',
    '"منافسة" أجهزة مخبرية السعودية',
    '"منافسة" أجهزة طبية السعودية',
    '"توريد" مستلزمات طبية السعودية',
    '"توريد" كواشف مختبرية السعودية',
    '"تأمين" أجهزة طبية السعودية',
    '"تأمين" مستلزمات طبية السعودية',
    '"ترسية" مستشفى السعودية',
    '"ترسية" أجهزة طبية السعودية',
    '"ترسية" مختبر السعودية',
    '"نوبكو" مناقصة',
    '"نوبكو" منافسة',
    '"نوبكو" توريد',
    'مناقصات مستشفيات السعودية',
    'مناقصات مختبرات السعودية',
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
# استخراج التاريخ
# ============================================================

def format_date(date_text):
    if not date_text:
        return ""

    try:
        dt = parsedate_to_datetime(date_text)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_text.strip()


# ============================================================
# حساب التطابق
# ============================================================

def find_matches(text, keywords):
    """
    ترجع الكلمات الموجودة فعلياً داخل النص.
    """
    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


# ============================================================
# حساب Relevance Score
# ============================================================

def calculate_score(title, description):
    title = title or ""
    description = description or ""

    title_lower = title.lower()
    description_lower = description.lower()

    combined_text = f"{title} {description}".lower()

    score = 0

    matched_medical = find_matches(
        combined_text,
        MEDICAL_KEYWORDS
    )

    matched_tender = find_matches(
        combined_text,
        TENDER_KEYWORDS
    )

    matched_excluded = find_matches(
        combined_text,
        EXCLUDE_WORDS
    )

    # --------------------------------------------------------
    # نقاط المجال الطبي
    # --------------------------------------------------------

    for keyword in matched_medical:
        if keyword.lower() in title_lower:
            score += 25
        else:
            score += 10

    # --------------------------------------------------------
    # نقاط المناقصات
    # --------------------------------------------------------

    for keyword in matched_tender:
        if keyword.lower() in title_lower:
            score += 30
        else:
            score += 10

    # --------------------------------------------------------
    # نقاط إضافية لبعض الكلمات المهمة
    # --------------------------------------------------------

    high_value_keywords = [
        "نوبكو",
        "مناقصة",
        "منافسة",
        "ترسية",
        "كواشف",
        "أجهزة طبية",
        "أجهزة مخبرية",
    ]

    for keyword in high_value_keywords:
        if keyword.lower() in title_lower:
            score += 15

    # --------------------------------------------------------
    # الخصم للكلمات المستبعدة
    # --------------------------------------------------------

    score -= len(matched_excluded) * 30

    # الحد الأعلى 100
    score = min(score, 100)

    # الحد الأدنى 0
    score = max(score, 0)

    return {
        "score": score,
        "medical_matches": matched_medical,
        "tender_matches": matched_tender,
        "excluded_matches": matched_excluded,
    }


# ============================================================
# تصنيف الفرصة
# ============================================================

def classify_tender(text):
    text = text.lower()

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

    if any(
        keyword in text
        for keyword in [
            "نوبكو",
            "NUPCO",
        ]
    ):
        return "🏢 نوبكو / مشتريات صحية"

    return "🏥 قطاع صحي"


# ============================================================
# جلب Google News RSS
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

        root = ET.fromstring(response.content)

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
                if link_element is not None and link_element.text
                else ""
            )

            description = clean_text(
                description_element.text
                if description_element is not None
                else ""
            )

            published_at = (
                pub_date_element.text.strip()
                if pub_date_element is not None and pub_date_element.text
                else ""
            )

            source = (
                source_element.text.strip()
                if source_element is not None and source_element.text
                else "Google News"
            )

            if title and link:
                results.append(
                    {
                        "title": title,
                        "link": link,
                        "description": description,
                        "published_at": format_date(published_at),
                        "source": source,
                    }
                )

    except requests.RequestException as error:
        print(f"❌ RSS request error: {error}")

    except ET.ParseError as error:
        print(f"❌ RSS XML parsing error: {error}")

    except Exception as error:
        print(f"❌ Unexpected RSS error: {error}")

    return results


# ============================================================
# جلب وفرز المناقصات
# ============================================================

def fetch_tenders():

    all_results = []

    # منع تكرار الرابط بين الـ Queries
    seen_links = set()

    for query in QUERIES:

        print(f"🔎 Searching: {query}")

        items = fetch_google_rss(query)

        for item in items:

            title = item["title"]
            description = item["description"]

            # ------------------------------------------------
            # منع تكرار نفس الرابط
            # ------------------------------------------------

            if item["link"] in seen_links:
                continue

            seen_links.add(item["link"])

            # ------------------------------------------------
            # النص الكامل للتحليل
            # ------------------------------------------------

            combined_text = f"{title} {description}"

            # ------------------------------------------------
            # حساب Score
            # ------------------------------------------------

            analysis = calculate_score(
                title,
                description
            )

            score = analysis["score"]

            # ------------------------------------------------
            # يجب وجود مجال صحي + مجال مناقصات
            # ------------------------------------------------

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

            if score < 60:
                continue

            # ------------------------------------------------
            # التصنيف
            # ------------------------------------------------

            category = classify_tender(
                combined_text
            )

            # ------------------------------------------------
            # حفظ النتيجة
            # ------------------------------------------------

            all_results.append(
                {
                    "title": title,
                    "link": item["link"],
                    "description": description,
                    "published_at": item["published_at"],
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
    # ترتيب النتائج من الأعلى Score إلى الأقل
    # --------------------------------------------------------

    all_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print(
        f"✅ Found {len(all_results)} relevant opportunities."
    )

    return all_results


# ============================================================
# اختبار مباشر للملف
# ============================================================

if __name__ == "__main__":

    results = fetch_tenders()

    for index, tender in enumerate(results, start=1):

        print("\n" + "=" * 60)

        print(f"#{index}")
        print(f"Title: {tender['title']}")
        print(f"Category: {tender['category']}")
        print(f"Score: {tender['score']}/100")
        print(f"Source: {tender['source']}")
        print(f"Published: {tender['published_at']}")
        print(f"Link: {tender['link']}")
        print(
            f"Medical: {', '.join(tender['medical_matches'])}"
        )
        print(
            f"Tender: {', '.join(tender['tender_matches'])}"
        )

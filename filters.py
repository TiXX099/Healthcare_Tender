import re
import unicodedata
from urllib.parse import urlparse


# ============================================================
# Saudi Arabia keywords
# ============================================================

SAUDI_KEYWORDS = [
    "السعودية",
    "السعوديه",
    "المملكة العربية السعودية",
    "المملكه العربيه السعوديه",
    "saudi arabia",
    "saudi",
    "ksa",
    "riyadh",
    "الرياض",
    "jeddah",
    "جدة",
    "makkah",
    "مكة",
    "madinah",
    "المدينة",
    "dammam",
    "الدمام",
    "khobar",
    "الخبر",
    "mecca",
    "medina",
    "tabuk",
    "تبوك",
    "abha",
    "أبها",
    "jazan",
    "جازان",
    "najran",
    "نجران",
    "taif",
    "الطائف",
]


# ============================================================
# Medical / Laboratory keywords
# ============================================================

MEDICAL_KEYWORDS = [
    # Arabic
    "مستلزمات طبية",
    "مستلزم طبي",
    "مستلزمات المختبر",
    "مستلزمات المختبرات",
    "مختبر",
    "مختبرات",
    "مواد مخبرية",
    "محاليل مخبرية",
    "محاليل المختبر",
    "تحاليل",
    "تشخيص",
    "تشخيصية",
    "أجهزة طبية",
    "جهاز طبي",
    "معدات طبية",
    "مستهلكات طبية",
    "مستهلكات مخبرية",
    "كواشف",
    "كواشف مخبرية",
    "كواشف تشخيصية",
    "أدوات مختبرية",
    "معدات مختبرية",
    "توريد طبي",
    "توريدات طبية",
    "توريد مختبري",
    "توريدات مختبرية",
    "القطاع الصحي",
    "المستشفيات",
    "الصحة",
    "الرعاية الصحية",

    # English
    "medical supplies",
    "medical supply",
    "laboratory supplies",
    "laboratory equipment",
    "laboratory consumables",
    "lab supplies",
    "lab equipment",
    "diagnostic",
    "diagnostics",
    "medical equipment",
    "medical devices",
    "medical consumables",
    "reagents",
    "diagnostic reagents",
    "laboratory reagents",
    "clinical laboratory",
    "healthcare procurement",
]


# ============================================================
# Tender keywords
# ============================================================

TENDER_KEYWORDS = [
    "مناقصة",
    "منافسة",
    "طرح",
    "توريد",
    "تأمين",
    "شراء",
    "طلب عروض",
    "طلب تقديم عروض",
    "عطاء",
    "عطاءات",
    "فرصة",
    "منافسات",
    "المنافسات",

    "tender",
    "tenders",
    "procurement",
    "rfp",
    "rfq",
    "request for proposal",
    "request for quotation",
    "bid",
    "bidding",
    "quotation",
    "supply",
    "supplies",
    "procurement opportunity",
]


# ============================================================
# Strong medical terms
# ============================================================

STRONG_MEDICAL_TERMS = [
    "laboratory",
    "lab",
    "reagent",
    "diagnostic",
    "diagnostics",
    "medical supplies",
    "medical equipment",
    "medical device",

    "مختبر",
    "مختبرات",
    "محاليل",
    "كواشف",
    "تشخيص",
    "مستلزمات طبية",
    "مستلزمات المختبر",
    "أجهزة طبية",
]


# ============================================================
# Excluded countries / locations
# ============================================================

EXCLUDED_COUNTRIES = [
    "العراق",
    "iraq",
    "baghdad",
    "بغداد",

    "مصر",
    "egypt",
    "cairo",
    "القاهرة",

    "الإمارات",
    "الامارات",
    "uae",
    "united arab emirates",
    "dubai",
    "دبي",
    "abu dhabi",
    "أبوظبي",

    "الكويت",
    "kuwait",

    "قطر",
    "qatar",
    "doha",
    "الدوحة",

    "البحرين",
    "bahrain",

    "عمان",
    "oman",
    "muscat",
    "مسقط",

    "الأردن",
    "jordan",
    "amman",

    "لبنان",
    "lebanon",

    "المغرب",
    "morocco",

    "الجزائر",
    "algeria",

    "تونس",
    "tunisia",

    "ليبيا",
    "libya",

    "فلسطين",
    "palestine",

    "اليمن",
    "yemen",
]


# ============================================================
# Excluded content
# ============================================================

EXCLUDED_KEYWORDS = [
    "وظائف",
    "وظيفة",
    "توظيف",
    "careers",
    "career",
    "jobs",
    "job",

    "مؤتمر",
    "مؤتمرات",
    "conference",
    "congress",

    "ندوة",
    "webinar",

    "منشور توعوي",
    "توعية",

    "وفاة",
    "death",

    "طقس",
    "weather",

    "رياضة",
    "sports",

    "كرة القدم",
    "football",

    "أسعار الأسهم",
    "stock",

    "سياحة",
    "tourism",
]


def normalize_text(text: str) -> str:
    """
    Normalize Arabic/English text for reliable matching.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Arabic normalization
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")

    # Remove URLs
    text = re.sub(r"https?://\S+", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in keywords
    )


def is_saudi(text: str) -> bool:
    """
    Saudi location must be present.
    """

    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in SAUDI_KEYWORDS
    )


def contains_excluded_country(text: str) -> bool:
    normalized = normalize_text(text)

    return any(
        normalize_text(country) in normalized
        for country in EXCLUDED_COUNTRIES
    )


def is_medical(text: str) -> bool:
    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in MEDICAL_KEYWORDS
    )


def is_tender(text: str) -> bool:
    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in TENDER_KEYWORDS
    )


def is_excluded(text: str) -> bool:
    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in EXCLUDED_KEYWORDS
    )


def source_is_trusted(url: str) -> bool:
    """
    Direct official sources are automatically trusted.
    Google News URLs are also allowed because the article itself
    is inspected and filtered.
    """

    if not url:
        return False

    domain = urlparse(url).netloc.lower()

    trusted_domains = [
        "nupco.com",
        "etimad.sa",
        "portal.etimad.sa",
        "google.com",
        "news.google.com",
    ]

    return any(
        domain == trusted
        or domain.endswith("." + trusted)
        for trusted in trusted_domains
    )


def score_opportunity(
    title: str,
    description: str,
    source: str = "",
) -> int:

    text = normalize_text(
        f"{title} {description} {source}"
    )

    score = 0

    # Saudi
    if is_saudi(text):
        score += 30

    # Tender
    if is_tender(text):
        score += 30

    # Medical
    if is_medical(text):
        score += 35

    # Strong medical term
    if contains_any(text, STRONG_MEDICAL_TERMS):
        score += 20

    # NUPCO
    if "nupco" in text or "نوبكو" in text:
        score += 30

    # Direct tender ID
    if re.search(
        r"\b(?:NPT|NDP)\d{3,6}/\d{2}\b",
        text,
        re.IGNORECASE,
    ):
        score += 35

    # Negative
    if contains_excluded_country(text):
        score -= 100

    if is_excluded(text):
        score -= 80

    return score


def passes_filter(
    title: str,
    description: str,
    url: str = "",
    source: str = "",
) -> tuple[bool, int, str]:

    full_text = f"{title} {description} {source}"

    # Hard reject
    if contains_excluded_country(full_text):
        return False, -100, "Excluded country"

    if is_excluded(full_text):
        return False, -80, "Excluded content"

    # Saudi required
    if not is_saudi(full_text):
        return False, 0, "No Saudi Arabia indicator"

    # Tender required
    if not is_tender(full_text):
        return False, 0, "Not a tender/procurement opportunity"

    # Medical required
    if not is_medical(full_text):
        return False, 0, "Not medical/laboratory"

    score = score_opportunity(
        title,
        description,
        source,
    )

    # Strong threshold
    if score < 60:
        return False, score, "Low relevance score"

    return True, score, "Accepted"

import re
from urllib.parse import urlparse


# ============================================================
# Saudi Healthcare Tender Bot
# Smart Context-Based Filter
# ============================================================


# ------------------------------------------------------------
# Trusted Saudi Sources
# ------------------------------------------------------------

TRUSTED_SAUDI_DOMAINS = {
    "nupco.com",
    "www.nupco.com",
    "etimad.sa",
    "www.etimad.sa",
    "portal.etimad.sa",
}

TRUSTED_SAUDI_SOURCES = {
    "nupco",
    "nupco السعودية",
    "منصة اعتماد",
    "اعتماد",
    "وزارة الصحة",
    "ministry of health",
    "saudi ministry of health",
}


# ------------------------------------------------------------
# Saudi Country / Location Indicators
# ------------------------------------------------------------

SAUDI_TERMS = {
    "السعودية",
    "المملكة العربية السعودية",
    "المملكه العربيه السعوديه",
    "السعوديه",
    "saudi arabia",
    "kingdom of saudi arabia",
    "ksa",
}

SAUDI_CITIES = {
    "الرياض",
    "جدة",
    "مكة",
    "مكه",
    "المدينة المنورة",
    "المدينه المنوره",
    "المدينة",
    "الدمام",
    "الخبر",
    "الظهران",
    "الطائف",
    "تبوك",
    "أبها",
    "ابها",
    "خميس مشيط",
    "جازان",
    "نجران",
    "حائل",
    "القصيم",
    "بريدة",
    "ينبع",
    "رابغ",
    "الأحساء",
    "الاحساء",
    "الجبيل",
    "عرعر",
    "سكاكا",
    "الباحة",
    "بيشة",
    "Saudi",
    "Riyadh",
    "Jeddah",
    "Mecca",
    "Medina",
    "Dammam",
    "Khobar",
    "Tabuk",
    "Abha",
    "Jazan",
    "Najran",
    "Hail",
    "Qassim",
    "Yanbu",
    "Jubail",
}


# ------------------------------------------------------------
# Saudi Organizations / Entities
# ------------------------------------------------------------

SAUDI_ENTITIES = {
    "نوبكو",
    "الشركة الوطنية للشراء الموحد",
    "الشركة الوطنية للشراء الموحد للادوية والأجهزة والمستلزمات الطبية",
    "الشركة الوطنية للشراء الموحد للأدوية والأجهزة والمستلزمات الطبية",
    "وزارة الصحة",
    "هيئة الغذاء والدواء",
    "الهيئة العامة للغذاء والدواء",
    "المركز الوطني للتخصيص",
    "منصة اعتماد",
    "اعتماد",
    "تجمع الرياض الصحي",
    "تجمع جدة الصحي",
    "تجمع مكة الصحي",
    "تجمع المدينة الصحي",
    "تجمع الشرقية الصحي",
    "تجمع القصيم الصحي",
    "تجمع عسير الصحي",
    "تجمع جازان الصحي",
    "تجمع تبوك الصحي",
    "جامعة الملك سعود",
    "جامعة الملك عبدالعزيز",
    "جامعة الملك فهد",
    "جامعة أم القرى",
    "مستشفى الملك فيصل التخصصي",
    "مدينة الملك فهد الطبية",
    "مدينة الملك عبدالله الطبية",
    "الشؤون الصحية",
    "Saudi Ministry of Health",
    "Ministry of Health Saudi Arabia",
    "NUPCO",
    "National Unified Procurement Company",
    "SFDA",
    "Saudi Food and Drug Authority",
    "Saudi Health Holding Company",
}


# ------------------------------------------------------------
# Medical / Laboratory Context
# ------------------------------------------------------------

MEDICAL_TERMS = {
    # Arabic
    "مستلزمات طبية",
    "مستلزمات طبيه",
    "مستلزمات المختبرات",
    "مستلزمات مختبرية",
    "مستلزمات مخبرية",
    "مواد مخبرية",
    "مواد مختبرية",
    "أجهزة طبية",
    "اجهزة طبية",
    "اجهزة طبيه",
    "معدات طبية",
    "معدات طبيه",
    "أدوية",
    "ادوية",
    "دواء",
    "أدوية ومستلزمات",
    "محاليل",
    "محاليل مختبرية",
    "كواشف",
    "كواشف مخبرية",
    "كواشف مختبرية",
    "تحاليل",
    "مختبر",
    "مختبرات",
    "مختبري",
    "مختبرية",
    "تشخيص",
    "تشخيصية",
    "مستلزمات تشخيصية",
    "مواد استهلاكية طبية",
    "مستهلكات طبية",
    "مستهلكات مختبرية",
    "عينات",
    "أجهزة تشخيصية",
    "مستلزمات الأسنان",
    "مستلزمات اسنان",
    "أشعة",
    "اشعة",
    "غسيل الكلى",
    "بنك الدم",
    "بنوك الدم",
    "مستلزمات العمليات",
    "مستلزمات جراحية",
    "مستلزمات تمريض",

    # English
    "medical supplies",
    "medical equipment",
    "medical devices",
    "laboratory supplies",
    "laboratory equipment",
    "lab supplies",
    "lab equipment",
    "diagnostic",
    "diagnostics",
    "reagents",
    "laboratory reagents",
    "medical consumables",
    "healthcare supplies",
    "healthcare equipment",
    "pharmaceutical",
    "pharmaceuticals",
    "medicine",
    "medicines",
    "drugs",
    "clinical",
    "laboratory",
    "lab",
    "pathology",
    "blood bank",
    "radiology",
    "surgical",
    "surgical supplies",
    "dental supplies",
    "dialysis",
    "medical devices",
}


# ------------------------------------------------------------
# Tender / Procurement Context
# ------------------------------------------------------------

TENDER_TERMS = {
    # Arabic
    "منافسة",
    "مناقصة",
    "مناقصات",
    "منافسات",
    "طرح",
    "طرح المنافسة",
    "توريد",
    "تأمين",
    "تأمين وتوريد",
    "شراء",
    "مشتريات",
    "شراء موحد",
    "تعاقد",
    "عقد",
    "عقود",
    "ترسية",
    "ترسية المنافسة",
    "دعوة للتنافس",
    "دعوة للمنافسة",
    "طلب عروض",
    "طلب تقديم عروض",
    "عرض سعر",
    "عروض الأسعار",
    "كراسة الشروط",
    "كراسة الشروط والمواصفات",
    "المنافسات والمشتريات",
    "الشراء والتوريد",
    "التوريد",
    "منافسة عامة",
    "منافسة محدودة",

    # English
    "tender",
    "tenders",
    "procurement",
    "purchase",
    "purchasing",
    "sourcing",
    "contract",
    "contracts",
    "bid",
    "bids",
    "bidding",
    "rfp",
    "rfq",
    "request for proposal",
    "request for quotation",
    "supply",
    "supplies",
    "supplier",
    "suppliers",
    "award",
    "contract award",
    "procurement opportunity",
}


# ------------------------------------------------------------
# Strong Medical Terms
# ------------------------------------------------------------

STRONG_MEDICAL_TERMS = {
    "مستلزمات طبية",
    "مستلزمات طبيه",
    "مستلزمات مختبرية",
    "مستلزمات مخبرية",
    "محاليل مختبرية",
    "كواشف مخبرية",
    "كواشف مختبرية",
    "أجهزة طبية",
    "اجهزة طبية",
    "أجهزة تشخيصية",
    "مختبرات",
    "مختبر",
    "medical supplies",
    "medical devices",
    "medical equipment",
    "laboratory supplies",
    "laboratory equipment",
    "laboratory reagents",
    "diagnostic equipment",
    "diagnostic supplies",
    "medical consumables",
}


# ------------------------------------------------------------
# Explicit Foreign Countries
# ------------------------------------------------------------

FOREIGN_COUNTRIES = {
    "العراق",
    "مصر",
    "الإمارات",
    "الامارات",
    "الكويت",
    "قطر",
    "البحرين",
    "عمان",
    "الأردن",
    "الاردن",
    "لبنان",
    "المغرب",
    "الجزائر",
    "تونس",
    "ليبيا",
    "فلسطين",
    "اليمن",
    "السودان",
    "سوريا",
    "سوريا",
    "تركيا",
    "إيران",
    "ايران",
    "باكستان",
    "الهند",
    "بنغلاديش",
    "أمريكا",
    "الولايات المتحدة",
    "بريطانيا",
    "المملكة المتحدة",

    "iraq",
    "egypt",
    "uae",
    "united arab emirates",
    "kuwait",
    "qatar",
    "bahrain",
    "oman",
    "jordan",
    "lebanon",
    "morocco",
    "algeria",
    "tunisia",
    "libya",
    "palestine",
    "yemen",
    "sudan",
    "syria",
    "turkey",
    "iran",
    "pakistan",
    "india",
    "bangladesh",
    "usa",
    "united states",
    "uk",
    "united kingdom",
}


# ------------------------------------------------------------
# Irrelevant Content
# ------------------------------------------------------------

EXCLUDED_KEYWORDS = {
    "وظيفة",
    "وظائف",
    "توظيف",
    "توظيفي",
    "job",
    "jobs",
    "career",
    "careers",
    "employment",

    "مؤتمر",
    "مؤتمرات",
    "conference",
    "conferences",

    "ندوة",
    "ندوات",
    "webinar",
    "webinars",

    "ورشة عمل",
    "workshop",
    "workshops",

    "طقس",
    "weather",

    "رياضة",
    "sports",
    "football",
    "soccer",

    "أسهم",
    "اسهم",
    "stock",
    "stocks",

    "سياحة",
    "tourism",
    "travel",

    "وفاة",
    "وفاة",
    "death",

    "تهنئة",
    "مهرجان",
    "festival",
}


# ------------------------------------------------------------
# Normalization
# ------------------------------------------------------------

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower()

    # Remove Arabic diacritics
    text = re.sub(
        r"[\u0610-\u061A\u064B-\u065F\u0670]",
        "",
        text,
    )

    # Arabic normalization
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------------------------
# Domain Detection
# ------------------------------------------------------------

def get_domain(url: str) -> str:

    if not url:
        return ""

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


def is_trusted_saudi_source(
    source: str = "",
    url: str = "",
) -> bool:

    source_normalized = normalize_text(source)
    domain = get_domain(url)

    # Trusted domain
    for trusted_domain in TRUSTED_SAUDI_DOMAINS:

        trusted_domain = trusted_domain.lower()

        if domain == trusted_domain:
            return True

        if domain.endswith("." + trusted_domain):
            return True

    # Saudi domain
    if domain.endswith(".sa"):
        return True

    # Trusted source name
    for trusted_source in TRUSTED_SAUDI_SOURCES:

        if normalize_text(trusted_source) in source_normalized:
            return True

    return False


# ------------------------------------------------------------
# Context Detection
# ------------------------------------------------------------

def contains_any(
    text: str,
    terms: set,
) -> int:

    normalized = normalize_text(text)

    count = 0

    for term in terms:

        if normalize_text(term) in normalized:
            count += 1

    return count


def detect_saudi_context(
    title: str,
    description: str,
    url: str,
    source: str,
) -> tuple[int, list[str]]:

    text = " ".join(
        [
            title or "",
            description or "",
            source or "",
        ]
    )

    normalized = normalize_text(text)

    score = 0
    reasons = []

    domain = get_domain(url)

    # Strongest signal: trusted Saudi source
    if is_trusted_saudi_source(source, url):

        score += 70
        reasons.append("trusted Saudi source")

    # .sa domain
    if domain.endswith(".sa"):

        score += 35
        reasons.append("Saudi .sa domain")

    # Saudi country explicitly mentioned
    if contains_any(normalized, SAUDI_TERMS) > 0:

        score += 45
        reasons.append("Saudi Arabia context")

    # Saudi city
    city_count = contains_any(
        normalized,
        SAUDI_CITIES,
    )

    if city_count > 0:

        score += min(
            city_count * 15,
            45,
        )

        reasons.append(
            f"Saudi location ({city_count})"
        )

    # Saudi organization
    entity_count = contains_any(
        normalized,
        SAUDI_ENTITIES,
    )

    if entity_count > 0:

        score += min(
            entity_count * 25,
            60,
        )

        reasons.append(
            f"Saudi entity ({entity_count})"
        )

    return score, reasons


# ------------------------------------------------------------
# Medical Context
# ------------------------------------------------------------

def detect_medical_context(
    title: str,
    description: str,
    source: str,
) -> tuple[int, list[str]]:

    text = " ".join(
        [
            title or "",
            description or "",
            source or "",
        ]
    )

    normalized = normalize_text(text)

    medical_count = contains_any(
        normalized,
        MEDICAL_TERMS,
    )

    strong_count = contains_any(
        normalized,
        STRONG_MEDICAL_TERMS,
    )

    score = 0
    reasons = []

    if medical_count > 0:

        score += min(
            medical_count * 18,
            60,
        )

        reasons.append(
            f"medical context ({medical_count})"
        )

    if strong_count > 0:

        score += min(
            strong_count * 25,
            60,
        )

        reasons.append(
            f"strong medical context ({strong_count})"
        )

    return score, reasons


# ------------------------------------------------------------
# Tender Context
# ------------------------------------------------------------

def detect_tender_context(
    title: str,
    description: str,
    source: str,
) -> tuple[int, list[str]]:

    text = " ".join(
        [
            title or "",
            description or "",
            source or "",
        ]
    )

    normalized = normalize_text(text)

    tender_count = contains_any(
        normalized,
        TENDER_TERMS,
    )

    score = 0
    reasons = []

    if tender_count > 0:

        score += min(
            tender_count * 20,
            70,
        )

        reasons.append(
            f"procurement context ({tender_count})"
        )

    return score, reasons


# ------------------------------------------------------------
# Foreign Context
# ------------------------------------------------------------

def detect_foreign_context(
    title: str,
    description: str,
) -> tuple[int, list[str]]:

    text = normalize_text(
        " ".join(
            [
                title or "",
                description or "",
            ]
        )
    )

    found = []

    for country in FOREIGN_COUNTRIES:

        if normalize_text(country) in text:
            found.append(country)

    return len(found), found


# ------------------------------------------------------------
# Excluded Content
# ------------------------------------------------------------

def detect_excluded_content(
    title: str,
    description: str,
) -> list[str]:

    text = normalize_text(
        " ".join(
            [
                title or "",
                description or "",
            ]
        )
    )

    found = []

    for keyword in EXCLUDED_KEYWORDS:

        if normalize_text(keyword) in text:
            found.append(keyword)

    return found


# ------------------------------------------------------------
# Opportunity Score
# ------------------------------------------------------------

def score_opportunity(
    title: str,
    description: str,
    url: str,
    source: str,
) -> tuple[int, list[str]]:

    saudi_score, saudi_reasons = detect_saudi_context(
        title,
        description,
        url,
        source,
    )

    medical_score, medical_reasons = detect_medical_context(
        title,
        description,
        source,
    )

    tender_score, tender_reasons = detect_tender_context(
        title,
        description,
        source,
    )

    foreign_count, foreign_countries = detect_foreign_context(
        title,
        description,
    )

    excluded = detect_excluded_content(
        title,
        description,
    )

    total_score = (
        saudi_score
        + medical_score
        + tender_score
    )

    reasons = (
        saudi_reasons
        + medical_reasons
        + tender_reasons
    )

    # Foreign-country penalty is contextual,
    # not an automatic rejection.
    if foreign_count > 0:

        total_score -= min(
            foreign_count * 20,
            50,
        )

        reasons.append(
            "foreign country mentioned: "
            + ", ".join(
                foreign_countries[:4]
            )
        )

    # Excluded content penalty
    if excluded:

        total_score -= min(
            len(excluded) * 50,
            100,
        )

        reasons.append(
            "excluded content: "
            + ", ".join(
                excluded[:4]
            )
        )

    return total_score, reasons


# ------------------------------------------------------------
# Main Filter
# ------------------------------------------------------------

def passes_filter(
    title: str,
    description: str,
    url: str,
    source: str,
) -> tuple[bool, int, str]:

    title = title or ""
    description = description or ""
    url = url or ""
    source = source or ""

    saudi_score, saudi_reasons = detect_saudi_context(
        title,
        description,
        url,
        source,
    )

    medical_score, medical_reasons = detect_medical_context(
        title,
        description,
        source,
    )

    tender_score, tender_reasons = detect_tender_context(
        title,
        description,
        source,
    )

    foreign_count, foreign_countries = detect_foreign_context(
        title,
        description,
    )

    excluded = detect_excluded_content(
        title,
        description,
    )

    total_score = (
        saudi_score
        + medical_score
        + tender_score
    )

    # --------------------------------------------------------
    # Trusted Saudi source
    # --------------------------------------------------------

    trusted_source = is_trusted_saudi_source(
        source,
        url,
    )

    # --------------------------------------------------------
    # Hard reject obvious irrelevant content
    # --------------------------------------------------------

    # Only reject excluded content when it dominates
    # the title/description.
    title_normalized = normalize_text(title)

    strong_excluded = any(
        normalize_text(keyword) in title_normalized
        for keyword in EXCLUDED_KEYWORDS
    )

    if strong_excluded and medical_score < 35:

        return (
            False,
            total_score,
            "Rejected: irrelevant content",
        )

    # --------------------------------------------------------
    # Medical requirement
    # --------------------------------------------------------

    if medical_score < 25:

        return (
            False,
            total_score,
            "Rejected: not sufficiently medical",
        )

    # --------------------------------------------------------
    # Tender requirement
    # --------------------------------------------------------

    if tender_score < 20:

        return (
            False,
            total_score,
            "Rejected: not a procurement/tender opportunity",
        )

    # --------------------------------------------------------
    # Saudi requirement
    # --------------------------------------------------------

    if not trusted_source and saudi_score < 35:

        return (
            False,
            total_score,
            "Rejected: Saudi context not strong enough",
        )

    # --------------------------------------------------------
    # Foreign-country logic
    # --------------------------------------------------------

    # If foreign countries appear but Saudi context is
    # significantly stronger, keep the opportunity.
    if (
        foreign_count >= 2
        and not trusted_source
        and saudi_score < 50
    ):

        return (
            False,
            total_score,
            "Rejected: foreign-country context dominates",
        )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    minimum_score = 70

    if trusted_source:
        minimum_score = 50

    if total_score < minimum_score:

        return (
            False,
            total_score,
            f"Rejected: confidence score {total_score} < {minimum_score}",
        )

    # --------------------------------------------------------
    # Accepted
    # --------------------------------------------------------

    all_reasons = (
        saudi_reasons
        + medical_reasons
        + tender_reasons
    )

    reason = (
        f"Accepted | score={total_score} | "
        + " | ".join(all_reasons[:8])
    )

    return (
        True,
        total_score,
        reason,
    )

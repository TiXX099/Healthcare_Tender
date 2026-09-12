import re
from urllib.parse import urlparse


# ============================================================
# TRUSTED SAUDI SOURCES
# ============================================================

TRUSTED_SAUDI_DOMAINS = {
    "nupco.com",
    "www.nupco.com",
    "etimad.sa",
    "www.etimad.sa",
    "portal.etimad.sa",
}


TRUSTED_SAUDI_SOURCES = {
    "nupco",
    "منصة اعتماد",
    "اعتماد",
    "وزارة الصحة",
    "ministry of health",
}


# ============================================================
# SAUDI CONTEXT
# ============================================================

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
    "المدينة",
    "المدينة المنورة",
    "المدينه المنوره",
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
    "الجبيل",
    "الأحساء",
    "الاحساء",
    "سكاكا",
    "عرعر",
    "الباحة",

    "jeddah",
    "riyadh",
    "mecca",
    "medina",
    "dammam",
    "khobar",
    "tabuk",
    "abha",
    "jazan",
    "najran",
    "hail",
}


SAUDI_ENTITIES = {
    "نوبكو",
    "الشركة الوطنية للشراء الموحد",
    "وزارة الصحة",
    "هيئة الغذاء والدواء",
    "الهيئة العامة للغذاء والدواء",
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

    "NUPCO",
    "Saudi Ministry of Health",
    "Ministry of Health Saudi Arabia",
    "Saudi Food and Drug Authority",
    "SFDA",
}


# ============================================================
# TARGET CATEGORIES
# ONLY THESE 4 CATEGORIES ARE ALLOWED
# ============================================================

CATEGORY_TERMS = {

    # --------------------------------------------------------
    # 1. Laboratories
    # --------------------------------------------------------

    "مختبرات": {
        "مختبر",
        "مختبرات",
        "مختبري",
        "مختبرية",
        "معمل",
        "معامل",
        "تحاليل مخبرية",
        "مواد مخبرية",
        "مستلزمات مختبرية",
        "مستلزمات مخبرات",
        "كواشف مخبرية",
        "كواشف مختبرية",
        "محاليل مختبرية",
        "محاليل مخبرية",

        "laboratory",
        "laboratories",
        "lab",
        "labs",
        "laboratory supplies",
        "laboratory equipment",
        "lab supplies",
        "lab equipment",
        "laboratory reagents",
        "reagents",
    },


    # --------------------------------------------------------
    # 2. Medical Supplies
    # --------------------------------------------------------

    "مستلزمات طبية": {
        "مستلزمات طبية",
        "مستلزمات طبيه",
        "مستهلكات طبية",
        "مستهلكات طبيه",
        "مواد استهلاكية طبية",
        "مستلزمات صحية",
        "مستلزمات المستشفيات",
        "مستلزمات رعاية صحية",

        "medical supplies",
        "medical consumables",
        "healthcare supplies",
        "hospital supplies",
    },


    # --------------------------------------------------------
    # 3. Medical Devices & Equipment
    # --------------------------------------------------------

    "أجهزة ومعدات طبية": {
        "أجهزة طبية",
        "اجهزة طبية",
        "اجهزة طبيه",
        "معدات طبية",
        "معدات طبيه",
        "أجهزة ومعدات طبية",
        "معدات وأجهزة طبية",
        "جهاز طبي",

        "medical devices",
        "medical equipment",
        "medical device",
        "healthcare equipment",
    },


    # --------------------------------------------------------
    # 4. Diagnostics
    # --------------------------------------------------------

    "تشخيص": {
        "تشخيص",
        "تشخيصية",
        "تشخيصي",
        "مستلزمات تشخيصية",
        "أجهزة تشخيصية",
        "معدات تشخيصية",
        "اختبارات تشخيصية",

        "diagnostic",
        "diagnostics",
        "diagnostic equipment",
        "diagnostic devices",
        "diagnostic supplies",
        "diagnostic tests",
    },
}


# ============================================================
# TENDER / PROCUREMENT TERMS
# ============================================================

TENDER_TERMS = {
    "منافسة",
    "منافسات",
    "مناقصة",
    "مناقصات",
    "طرح",
    "توريد",
    "تأمين",
    "تأمين وتوريد",
    "شراء",
    "مشتريات",
    "تعاقد",
    "عقد",
    "عقود",
    "ترسية",
    "دعوة للمنافسة",
    "دعوة للتنافس",
    "طلب عروض",
    "طلب تقديم عروض",
    "كراسة الشروط",
    "كراسة الشروط والمواصفات",

    "tender",
    "tenders",
    "procurement",
    "purchase",
    "purchasing",
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
    "procurement opportunity",
}


# ============================================================
# EXCLUDED CATEGORIES
# ============================================================

EXCLUDED_CATEGORY_TERMS = {

    # --------------------------------------------------------
    # Pharmaceuticals
    # --------------------------------------------------------

    "أدوية",
    "ادوية",
    "دواء",
    "صيدلية",
    "صيدليات",

    "pharmaceutical",
    "pharmaceuticals",
    "medicine",
    "medicines",
    "drugs",

    # --------------------------------------------------------
    # Dental
    # --------------------------------------------------------

    "أسنان",
    "اسنان",
    "dental",

    # --------------------------------------------------------
    # Nursing
    # --------------------------------------------------------

    "تمريض",
    "nursing",

    # --------------------------------------------------------
    # Nutrition / Food
    # --------------------------------------------------------

    "تغذية",
    "nutrition",
    "غذاء",
    "food",

    # --------------------------------------------------------
    # General Medical Services
    # --------------------------------------------------------

    "خدمات طبية",
    "medical services",

    # --------------------------------------------------------
    # Jobs
    # --------------------------------------------------------

    "وظائف",
    "وظيفة",
    "job",
    "jobs",

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    "مؤتمر",
    "مؤتمرات",
    "conference",
    "conferences",
    "ندوة",
    "ندوات",
    "webinar",
    "webinars",

    # --------------------------------------------------------
    # Other irrelevant content
    # --------------------------------------------------------

    "رياضة",
    "sports",
    "سياحة",
    "tourism",
}


# ============================================================
# FOREIGN COUNTRIES
# ============================================================

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
    "تركيا",
    "إيران",
    "ايران",
    "باكستان",
    "الهند",

    "egypt",
    "iraq",
    "uae",
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
    "yemen",
    "sudan",
    "syria",
    "turkey",
    "iran",
    "pakistan",
    "india",
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

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

    # Normalize Arabic characters
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# GET DOMAIN
# ============================================================

def get_domain(
    url: str,
) -> str:

    if not url:
        return ""

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        return domain

    except Exception:

        return ""


# ============================================================
# COUNT MATCHES
# ============================================================

def contains_any(
    text: str,
    terms: set,
) -> int:

    normalized = normalize_text(
        text
    )

    count = 0

    for term in terms:

        normalized_term = normalize_text(
            term
        )

        if normalized_term in normalized:

            count += 1

    return count


# ============================================================
# CHECK TRUSTED SAUDI SOURCE
# ============================================================

def is_trusted_saudi_source(
    source: str = "",
    url: str = "",
) -> bool:

    source_text = normalize_text(
        source
    )

    domain = get_domain(
        url
    )

    # Any Saudi domain
    if domain.endswith(".sa"):

        return True

    # Specific trusted domains
    for trusted_domain in TRUSTED_SAUDI_DOMAINS:

        trusted_domain = (
            trusted_domain.lower()
        )

        if domain == trusted_domain:

            return True

        if domain.endswith(
            "." + trusted_domain
        ):

            return True

    # Trusted source names
    for trusted_source in TRUSTED_SAUDI_SOURCES:

        if normalize_text(
            trusted_source
        ) in source_text:

            return True

    return False


# ============================================================
# DETECT SAUDI CONTEXT
# ============================================================

def detect_saudi_context(
    title,
    description,
    url,
    source,
):

    text = " ".join([
        title,
        description,
        source,
    ])

    score = 0
    reasons = []

    # Trusted Saudi source
    if is_trusted_saudi_source(
        source,
        url,
    ):

        score += 70

        reasons.append(
            "Saudi trusted source"
        )

    # Saudi domain
    domain = get_domain(
        url
    )

    if domain.endswith(".sa"):

        score += 30

    # Saudi country
    if contains_any(
        text,
        SAUDI_TERMS,
    ):

        score += 40

        reasons.append(
            "Saudi Arabia"
        )

    # Saudi city
    city_count = contains_any(
        text,
        SAUDI_CITIES,
    )

    if city_count:

        score += min(
            city_count * 15,
            45,
        )

        reasons.append(
            "Saudi location"
        )

    # Saudi organization
    entity_count = contains_any(
        text,
        SAUDI_ENTITIES,
    )

    if entity_count:

        score += min(
            entity_count * 25,
            60,
        )

        reasons.append(
            "Saudi entity"
        )

    return (
        score,
        reasons,
    )


# ============================================================
# DETECT CATEGORY
# ============================================================

def detect_category(
    title,
    description,
    source,
):

    text = " ".join([
        title,
        description,
        source,
    ])

    scores = {}

    for category, terms in CATEGORY_TERMS.items():

        count = contains_any(
            text,
            terms,
        )

        if count:

            scores[category] = (
                count * 25
            )

    if not scores:

        return (
            "",
            0,
            {},
        )

    sorted_categories = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    category = sorted_categories[0][0]

    score = sorted_categories[0][1]

    return (
        category,
        score,
        scores,
    )


# ============================================================
# DETECT TENDER CONTEXT
# ============================================================

def detect_tender_context(
    title,
    description,
    source,
):

    text = " ".join([
        title,
        description,
        source,
    ])

    count = contains_any(
        text,
        TENDER_TERMS,
    )

    score = min(
        count * 20,
        70,
    )

    return (
        score,
        count,
    )


# ============================================================
# DETECT EXCLUDED CATEGORIES
# ============================================================

def detect_excluded_categories(
    title,
    description,
):

    text = normalize_text(
        " ".join([
            title,
            description,
        ])
    )

    found = []

    for term in EXCLUDED_CATEGORY_TERMS:

        normalized_term = normalize_text(
            term
        )

        if normalized_term in text:

            found.append(
                term
            )

    return found


# ============================================================
# MAIN FILTER
# ============================================================

def passes_filter(
    title,
    description,
    url,
    source,
):

    title = title or ""
    description = description or ""
    url = url or ""
    source = source or ""

    # --------------------------------------------------------
    # Full text
    # --------------------------------------------------------

    full_text = (
        title
        + " "
        + description
    )

    normalized_text = normalize_text(
        full_text
    )

    normalized_title = normalize_text(
        title
    )

    # --------------------------------------------------------
    # Saudi context
    # --------------------------------------------------------

    (
        saudi_score,
        saudi_reasons,
    ) = detect_saudi_context(
        title,
        description,
        url,
        source,
    )

    trusted_source = (
        is_trusted_saudi_source(
            source,
            url,
        )
    )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    (
        category,
        category_score,
        category_scores,
    ) = detect_category(
        title,
        description,
        source,
    )

    # No target category
    if not category:

        return (
            False,
            0,
            "Rejected: not one of the 4 target categories",
        )

    # Weak target category
    if category_score < 25:

        return (
            False,
            category_score,
            "Rejected: weak target-category context",
        )

    # --------------------------------------------------------
    # Tender context
    # --------------------------------------------------------

    (
        tender_score,
        tender_count,
    ) = detect_tender_context(
        title,
        description,
        source,
    )

    if tender_score < 20:

        return (
            False,
            category_score,
            "Rejected: not a tender/procurement opportunity",
        )

    # --------------------------------------------------------
    # Saudi requirement
    # --------------------------------------------------------

    if (
        not trusted_source
        and saudi_score < 35
    ):

        return (
            False,
            category_score,
            "Rejected: Saudi context not strong enough",
        )

    # --------------------------------------------------------
    # Foreign country protection
    # --------------------------------------------------------

    foreign_count = contains_any(
        normalized_text,
        FOREIGN_COUNTRIES,
    )

    if foreign_count > 0:

        if not trusted_source:

            if not contains_any(
                normalized_text,
                SAUDI_TERMS,
            ):

                return (
                    False,
                    0,
                    "Rejected: foreign country opportunity",
                )

    # --------------------------------------------------------
    # Excluded categories
    # --------------------------------------------------------

    excluded = detect_excluded_categories(
        title,
        description,
    )

    # --------------------------------------------------------
    # STRICT PHARMACEUTICAL REJECTION
    # --------------------------------------------------------
    #
    # If the TITLE itself contains pharmaceutical terms,
    # reject the opportunity.
    #
    # This means:
    #
    # "تأمين بنود أدوية"
    #                       -> REJECT
    #
    # "تأمين بنود أدوية ومستلزمات طبية"
    #                       -> REJECT
    #
    # "تأمين أدوية ومستلزمات مختبرية"
    #                       -> REJECT
    #
    # "Pharmaceutical supplies tender"
    #                       -> REJECT
    #
    # --------------------------------------------------------

    pharmaceutical_terms = {
        "أدوية",
        "ادوية",
        "دواء",
        "صيدلية",
        "صيدليات",

        "pharmaceutical",
        "pharmaceuticals",
        "medicine",
        "medicines",
        "drugs",
    }

    pharmaceutical_in_title = any(
        normalize_text(term)
        in normalized_title
        for term in pharmaceutical_terms
    )

    if pharmaceutical_in_title:

        return (
            False,
            0,
            "Rejected: pharmaceutical opportunity",
        )

    # --------------------------------------------------------
    # Other excluded categories
    # --------------------------------------------------------

    non_pharmaceutical_excluded = [
        term
        for term in excluded
        if normalize_text(term)
        not in {
            normalize_text(x)
            for x in pharmaceutical_terms
        }
    ]

    if non_pharmaceutical_excluded:

        target_score = (
            category_scores.get(
                category,
                0,
            )
        )

        # Reject if excluded category is not strongly
        # accompanied by a target category.
        if target_score < 50:

            return (
                False,
                target_score,
                "Rejected: excluded category",
            )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    total_score = (
        saudi_score
        + category_score
        + tender_score
    )

    minimum_score = (
        50
        if trusted_source
        else 70
    )

    if total_score < minimum_score:

        return (
            False,
            total_score,
            f"Rejected: score {total_score} < {minimum_score}",
        )

    # --------------------------------------------------------
    # ACCEPT
    # --------------------------------------------------------

    reason = (
        f"Accepted | "
        f"category={category} | "
        f"score={total_score}"
    )

    return (
        True,
        total_score,
        reason,
    )

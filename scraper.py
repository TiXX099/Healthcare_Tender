
# -*- coding: utf-8 -*-
"""
scrapers.py
===========
مسؤول فقط عن جلب المناقصات من المصادر المختلفة وإرجاعها بشكل منظم:
    {"source": "اسم المصدر", "title": "عنوان المناقصة", "link": "الرابط"}
 
لا تنسَ:
- نوبكو (NUPCO) موقع عادي (server-rendered) ويعمل مباشرة عبر requests.
- اعتماد / تنافس / المركز الوطني للتخصيص مواقع JavaScript (Angular/React SPA)،
  يعني لازم متصفح حقيقي (Playwright) لتحميل المحتوى قبل قراءته.
  الـ selectors تحتها "أفضل تخمين" ويجب التأكد منها فعليًا عبر:
  فتح الموقع في كروم -> كليك يمين على المناقصة -> Inspect -> شوف اسم
  الـ class أو tag المستخدم فعليًا، وعدّل القيم المعلّمة بـ TODO تحت.
"""
 
import re
import hashlib
import logging
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from bs4 import BeautifulSoup
 
log = logging.getLogger("tenders_bot.scrapers")
 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ar,en;q=0.8",
}
 
# كلمات تدل إن المناقصة متعلقة فعلاً بالقطاع الصحي (تُستخدم كفلتر إضافي
# للمصادر العامة اللي ما تكون كل نتائجها صحية بالضرورة)
HEALTH_KEYWORDS = [
    "صحة", "صحي", "صحية", "طبي", "طبية", "مستشفى", "مستشفيات",
    "مختبر", "مختبرات", "دواء", "أدوية", "مستلزمات طبية", "أجهزة طبية",
    "تمريض", "عيادة", "عيادات", "صيدلية", "الرعاية الصحية", "تعقيم", "أشعة",
]
 
# كلمات تدل إن الخبر فعلاً عن "مناقصة" أو "طرح" (مو مجرد ذكر عابر للكلمة
# بسياق ثاني — زي خبر سياسي أو فني يحتوي كلمة "مناقصات" بالصدفة)
TENDER_KEYWORDS = [
    "مناقصة", "مناقصات", "منافسة", "منافسات", "طرح مناقصة",
    "توريد", "عطاء", "عطاءات", "الطرح", "طرح عطاء",
]
 
# كلمات تحصر النتائج بالسعودية فقط (احتياطي إضافي فوق فلتر gl=SA بالرابط،
# لأن بعض الأخبار تذكر السعودية بسياق دبلوماسي/غير محلي)
SAUDI_KEYWORDS = ["السعودية", "السعودي", "المملكة العربية السعودية", "المملكة"]
 
 
def clean_text(text: str) -> str:
    """تنظيف النص من المسافات والأسطر الزائدة"""
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()
 
 
def normalize_title(title: str) -> str:
    """
    تطبيع العنوان لمقارنة "هل هذا نفس الخبر؟" — نفس الخبر ممكن يوصلنا
    بروابط مختلفة (Google News يضيف معرّف تتبع فريد بكل رابط حتى لو نفس
    المقال بالضبط)، فالاعتماد على الرابط وحده للمقارنة غير كافٍ.
    نشيل علامات الترقيم والمسافات الزائدة ونحوّل لحروف صغيرة.
    """
    text = clean_text(title).lower()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text
 
 
def get_tender_id(tender: dict) -> str:
    """
    معرّف ثابت لكل مناقصة/خبر يُستخدم لمنع التكرار — مبني على العنوان
    المطبَّع بدل الرابط الخام، عشان نفس الخبر ما يُرسَل مرتين حتى لو
    وصل برابط مختلف شوي في مرة تانية.
    """
    normalized = normalize_title(tender["title"])
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()
 
 
def is_health_related(text: str) -> bool:
    return any(k in text for k in HEALTH_KEYWORDS)
 
 
def is_tender_related(text: str) -> bool:
    return any(k in text for k in TENDER_KEYWORDS)
 
 
def is_saudi_related(text: str) -> bool:
    return any(k in text for k in SAUDI_KEYWORDS)
 
 
# ---------------------------------------------------------------------------
# 1) نوبكو (NUPCO) — يعمل مباشرة، تم التحقق من بنية الصفحة الفعلية
# ---------------------------------------------------------------------------
def fetch_nupco_tenders():
    """
    الشركة الوطنية للشراء الموحد (نوبكو).
    كل مناقصة تظهر داخل <h3><a href=".../tender/...">العنوان</a></h3>
    وتتكرر مرتين بالصفحة (نسخة جوال + ديسكتوب) لذلك نعمل dedupe بالرابط.
    نوبكو متخصصة بالكامل بالمستلزمات الطبية، فلا حاجة لفلترة إضافية.
    """
    url = "https://www.nupco.com/tenders/tenders-list/"
    tenders = []
    seen_links = set()
 
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
 
        # كل روابط المناقصات تحتوي على "/tender/" في الـ href
        links = soup.select('h3 a[href*="/tender/"]')
 
        for a in links:
            link = a.get("href", "").strip()
            title = clean_text(a.get_text())
 
            if not link or not title or link in seen_links:
                continue
 
            seen_links.add(link)
            tenders.append({"source": "نوبكو (NUPCO)", "title": title, "link": link})
 
    except requests.RequestException as e:
        log.error("فشل الاتصال بموقع نوبكو: %s", e)
    except Exception as e:
        log.exception("خطأ غير متوقع أثناء جلب نوبكو: %s", e)
 
    return tenders
 
 
# ---------------------------------------------------------------------------
# 2) منصة اعتماد — موقع Angular، يحتاج متصفح حقيقي (Playwright)
# ---------------------------------------------------------------------------
def fetch_etimad_tenders(max_results=5):
    """
    منصة اعتماد الحكومية (tenders.etimad.sa).
    لا يوجد API عام موثّق من اعتماد نفسها، والصفحة تُبنى بالكامل بالجافاسكربت،
    لذلك requests وحده لا يكفي إطلاقًا. نستخدم Playwright لتحميل الصفحة فعليًا
    ثم نقرأ الـ DOM بعد التحميل.
 
    ملاحظة مهمة: الـ selector تحت (`.tender-item`, أو أي عنصر يحوي رابط
    تفاصيل المنافسة) هو تخمين مبدئي. افتح الصفحة بالمتصفح وتأكد من الاسم
    الحقيقي للعنصر عبر Inspect، وعدّله في المكان المعلّم TODO.
    """
    from playwright.sync_api import sync_playwright
 
    url = "https://tenders.etimad.sa/Tender/AllSupplierTendersForVisitor"
    tenders = []
 
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            page.goto(url, timeout=30000, wait_until="networkidle")
 
            # TODO: تأكد من الـ selector الصحيح لبطاقة المنافسة عبر Inspect
            cards = page.query_selector_all("a[href*='DetailsForVisitor']")
 
            for card in cards[:max_results]:
                title = clean_text(card.inner_text())
                href = card.get_attribute("href") or ""
                if href.startswith("/"):
                    href = "https://tenders.etimad.sa" + href
 
                if title and is_health_related(title):
                    tenders.append({"source": "منصة اعتماد", "title": title, "link": href or url})
 
            browser.close()
 
    except ImportError:
        log.warning("Playwright غير مثبت — راجع requirements.txt")
    except Exception as e:
        log.error("فشل جلب مناقصات اعتماد: %s", e)
 
    return tenders
 
 
# ---------------------------------------------------------------------------
# 3) منصة تنافس — نفس ملاحظة الجافاسكربت + الموقع يمنع الوصول الآلي
#    عبر robots.txt، فاستخدامه آليًا قد يخالف شروط استخدام الموقع.
# ---------------------------------------------------------------------------
def fetch_tanafus_tenders(max_results=5):
    """
    منصة تنافس. تنبيه: robots.txt الخاص بالموقع يمنع الزحف الآلي صراحة،
    لذلك ننصح إما بعدم تضمينه في البوت، أو التواصل معهم للحصول على
    وصول رسمي/API إن وُجد، بدل الزحف المباشر.
    تُركت الدالة هنا كهيكل جاهز فقط في حال حصلت على إذن/API رسمي.
    """
    log.info("تم تخطي تنافس: robots.txt يمنع الوصول الآلي لهذا الموقع.")
    return []
 
 
# ---------------------------------------------------------------------------
# 4) المركز الوطني للتخصيص — موقع SharePoint/JS، نفس مبدأ Playwright
# ---------------------------------------------------------------------------
def fetch_ncp_tenders(max_results=5):
    """
    المركز الوطني للتخصيص وتنمية القطاع الخاص - فرص الشراكة الصحية.
    نفس مبدأ اعتماد: يحتاج Playwright، والـ selector أدناه تخميني ويجب
    التحقق منه عبر Inspect بالمتصفح.
    """
    from playwright.sync_api import sync_playwright
 
    url = "https://www.ncp.gov.sa/ar/Opportunities/Pages/default.aspx"
    tenders = []
 
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            page.goto(url, timeout=30000, wait_until="networkidle")
 
            # TODO: تأكد من الـ selector الصحيح عبر Inspect
            items = page.query_selector_all("a")
 
            for item in items:
                title = clean_text(item.inner_text())
                href = item.get_attribute("href") or ""
                if title and is_health_related(title) and len(title) > 10:
                    if href.startswith("/"):
                        href = "https://www.ncp.gov.sa" + href
                    tenders.append({"source": "المركز الوطني للتخصيص", "title": title, "link": href or url})
                if len(tenders) >= max_results:
                    break
 
            browser.close()
 
    except ImportError:
        log.warning("Playwright غير مثبت — راجع requirements.txt")
    except Exception as e:
        log.error("فشل جلب فرص المركز الوطني للتخصيص: %s", e)
 
    return tenders
 
 
# ---------------------------------------------------------------------------
# 5) Google News RSS — خلاصة عامة رسمية، لا تحتاج API key ولا متصفح JS
# ---------------------------------------------------------------------------
GOOGLE_NEWS_QUERIES = [
    '"مناقصة" مستلزمات طبية السعودية',
    '"مناقصة" مختبرات طبية السعودية',
    '"مناقصة" أجهزة طبية السعودية',
    '"مناقصة" أدوية السعودية',
    '"مناقصة" تحاليل طبية السعودية',
]
 
 
def fetch_google_news_tenders(max_results=10):
    """
    يجلب أخبارًا عن مناقصات طبية عبر خلاصة RSS العامة لـ Google News،
    مع تطبيق فلاتر صارمة بعد الجلب (مو بس البحث) لأن Google News أحيانًا
    يرجّع نتائج تحتوي كلمة واحدة من الاستعلام بسياق مختلف تمامًا (زي خبر
    عن السينما يذكر كلمة "مناقصات" بالصدفة).
 
    القاعدة: نقبل الخبر فقط لو كان عن مناقصة فعلية + صحي + سعودي مجتمعين.
 
    هذا مصدر "أخبار عن مناقصات" (تغطية صحفية) وليس الإعلان الرسمي من الجهة
    الحكومية نفسها — مفيد كمكمّل للمصادر الرسمية، لكن تحقق دائمًا من تاريخ
    الخبر والرابط الأصلي قبل الاعتماد عليه للتقديم الفعلي.
    """
    tenders = []
    seen_links = set()
    seen_titles = set()
 
    for query in GOOGLE_NEWS_QUERIES:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ar&gl=SA&ceid=SA:ar"
 
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            root = ET.fromstring(res.content)
 
            for item in root.findall(".//item")[:max_results]:
                title_el = item.find("title")
                link_el = item.find("link")
 
                title = clean_text(title_el.text) if title_el is not None else ""
                link = clean_text(link_el.text) if link_el is not None else ""
 
                if not title or not link:
                    continue
 
                title_key = normalize_title(title)
 
                # نفس الخبر ممكن يطلع من أكثر من استعلام بروابط مختلفة —
                # المقارنة هنا بالعنوان المطبَّع مو بالرابط
                if link in seen_links or title_key in seen_titles:
                    continue
 
                relevant = (
                    is_tender_related(title)
                    and is_health_related(title)
                    and is_saudi_related(title)
                )
 
                if not relevant:
                    continue
 
                seen_links.add(link)
                seen_titles.add(title_key)
                tenders.append({"source": "أخبار Google News", "title": title, "link": link})
 
        except requests.RequestException as e:
            log.error("فشل الاتصال بخلاصة Google News: %s", e)
        except ET.ParseError as e:
            log.error("فشل تحليل خلاصة Google News (XML غير صالح): %s", e)
 
    return tenders
 
 
# ---------------------------------------------------------------------------
# دالة التجميع الرئيسية
# ---------------------------------------------------------------------------
def fetch_all_tenders():
    """
    يجمع نتائج كل المصادر في قائمة واحدة منظمة، مع إزالة أي تكرار حتى لو
    جاء نفس الخبر من مصدرين مختلفين (مثلاً نوبكو + خبر عنه بجوجل نيوز)،
    بالاعتماد على العنوان المطبَّع (normalize_title) لا الرابط.
    """
    all_tenders = []
    all_tenders.extend(fetch_nupco_tenders())
    all_tenders.extend(fetch_etimad_tenders())
    all_tenders.extend(fetch_tanafus_tenders())
    all_tenders.extend(fetch_ncp_tenders())
    all_tenders.extend(fetch_google_news_tenders())
 
    unique_tenders = []
    seen_titles = set()
    for tender in all_tenders:
        title_key = normalize_title(tender["title"])
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        unique_tenders.append(tender)
 
    return unique_tenders
 
 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = fetch_all_tenders()
    print(f"تم جلب {len(results)} مناقصة:\n")
    for r in results:
        print("---")
        print(f"المصدر: {r['source']}")
        print(f"العنوان: {r['title']}")
        print(f"الرابط: {r['link']}")

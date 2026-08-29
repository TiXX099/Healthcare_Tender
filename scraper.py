import re
import time
import requests
import feedparser
from datetime import datetime, date
from bs4 import BeautifulSoup

# الكلمات المفتاحية للمناقصات
TENDER_KEYWORDS = [
    "مناقصة", "مناقصات", "عطاء", "عطاءات", "شراء موحد", 
    "توريد أدوية", "تأمين أجهزة", "مستلزمات طبية", "تشغيل مستشفى"
]

# كلمات الاستبعاد (تمنع الأخبار الخارجية)
EXCLUDE_KEYWORDS = [
    "صنعاء", "اليوم السابع", "مصر", "موريتانية", "البرلمان", 
    "الإسرائيلية", "الزنداني", "جنيه", "صوت الأمة", "يمن برس"
]

def is_from_today_onwards(entry):
    """تحديد هل الخبر منشور بتاريخ اليوم أو بعده حصراً"""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        # استخراج تاريخ الخبر فقط (سنة - شهر - يوم)
        entry_date = datetime.fromtimestamp(time.mktime(entry.published_parsed)).date()
        today = date.today()  # يقرأ تاريخ اليوم تلقائياً عند التشغيل (مثلاً 2026-08-29)
        
        # قبول الخبر فقط إذا كان تاريخه يساوي اليوم أو بعده
        if entry_date < today:
            return False
    return True

def is_valid_saudi_tender(title):
    """التحقق من أن الخبر مناقصة سعودية دون أي مصادر خارجية"""
    for ex in EXCLUDE_KEYWORDS:
        if ex in title:
            return False
            
    pattern = re.compile("|".join(TENDER_KEYWORDS), re.IGNORECASE)
    return bool(pattern.search(title))

def fetch_google_news():
    """جلب مناقصات الصحة من Google News المنشورة بدءاً من اليوم"""
    query = '("مناقصة" OR "مناقصات" OR "شراء موحد") AND ("الصحة" OR "نوبكو" OR "مستشفى") site:.sa OR site:news.google.com'
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=ar&gl=SA&ceid=SA:ar"
    
    feed = feedparser.parse(rss_url)
    items = []
    for entry in feed.entries:
        # فحص التاريخ (اليوم وما بعده) + الفلترة المفهومية
        if is_from_today_onwards(entry) and is_valid_saudi_tender(entry.title):
            items.append({
                "id": entry.link,
                "title": entry.title,
                "source": "أخبار جوجل (السعودية)",
                "link": entry.link
            })
    return items

def fetch_etimad():
    """جلب مناقصات القطاع الصحي من منصة اعتماد الحكومية"""
    url = "https://tenders.etimad.sa/Tender/AllTendersForVisitor"
    items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='card-content')
            for card in cards:
                text = card.get_text()
                if any(k in text for k in ["صحة", "مستشفى", "أدوية", "طبي", "مختبر"]) and is_valid_saudi_tender(text):
                    link_tag = card.find('a', href=True)
                    tender_link = "https://tenders.etimad.sa" + link_tag['href'] if link_tag else url
                    tender_title = card.find('h3').get_text(strip=True) if card.find('h3') else "مناقصة صحية - اعتماد"
                    items.append({
                        "id": tender_link,
                        "title": tender_title,
                        "source": "منصة اعتماد",
                        "link": tender_link
                    })
    except Exception as e:
        print(f"خطأ في كشط اعتماد: {e}")
    return items

def fetch_nupco_and_nafas():
    """جلب مناقصات نوبكو ونافس المنشورة بدءاً من اليوم"""
    query = '("مناقصة" OR "مناقصات" OR "عطاءات") AND ("نوبكو" OR "نافس")'
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=ar&gl=SA&ceid=SA:ar"
    
    feed = feedparser.parse(rss_url)
    items = []
    for entry in feed.entries:
        if is_from_today_onwards(entry) and is_valid_saudi_tender(entry.title):
            items.append({
                "id": entry.link,
                "title": entry.title,
                "source": "نوبكو / نافس",
                "link": entry.link
            })
    return items

def get_all_tenders():
    tenders = []
    tenders.extend(fetch_google_news())
    tenders.extend(fetch_etimad())
    tenders.extend(fetch_nupco_and_nafas())
    return tenders

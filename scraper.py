import re
import requests
import feedparser
from bs4 import BeautifulSoup

# الكلمات المفتاحية للمجال الطبي والصحي في السعودية
KEYWORDS = [
    "مستشفى", "مستشفيات", "أدوية", "مستلزمات طبية", "أجهزة طبية",
    "تجهيزات طبية", "صحة", "الصحة", "تشغيل طبي", "صيانة طبية",
    "صيدلة", "مختبرات", "عيادات", "تأمين طبي", "حلول صحية"
]

def is_medical_saudi(text):
    """التحقق من ارتباط النص بالقطاع الصحي في السعودية"""
    pattern = re.compile("|".join(KEYWORDS), re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_google_news():
    """جلب الأخبار والمناقصات من Google News RSS"""
    query = 'مناقصات صحية OR مناقصات طبية OR نوبكو OR "وزارة الصحة" السعودية'
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=ar&gl=SA&ceid=SA:ar"
    
    feed = feedparser.parse(rss_url)
    items = []
    for entry in feed.entries:
        if is_medical_saudi(entry.title):
            items.append({
                "id": entry.link,
                "title": entry.title,
                "source": "أخبار جوجل (السعودية)",
                "link": entry.link
            })
    return items

def fetch_etimad():
    """جلب مناقصات منصة اعتماد للقطاع الصحي"""
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
                if is_medical_saudi(text):
                    link_tag = card.find('a', href=True)
                    tender_link = "https://tenders.etimad.sa" + link_tag['href'] if link_tag else url
                    tender_title = card.find('h3').get_text(strip=True) if card.find('h3') else "مناقصة صحية جديدة"
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
    """جلب أخبار ومناقصات نوبكو ونافس"""
    queries = ['"نوبكو" OR "NUPCO"', '"منصة نافس" OR "نافس الطبية"']
    items = []
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl=ar&gl=SA&ceid=SA:ar"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            if is_medical_saudi(entry.title):
                items.append({
                    "id": entry.link,
                    "title": entry.title,
                    "source": "نوبكو / نافس",
                    "link": entry.link
                })
    return items

def get_all_tenders():
    """تجميع كافة البيانات المفلترة"""
    tenders = []
    tenders.extend(fetch_google_news())
    tenders.extend(fetch_etimad())
    tenders.extend(fetch_nupco_and_nafas())
    return tenders

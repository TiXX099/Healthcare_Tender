import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# الكلمات المفتاحية المستهدفة للمناقصات الطبية والمخبرية السعودية
HEALTH_KEYWORDS = [
    "مختبر", "أجهزة طبية", "توريد", "كواشف", "مستلزمات طبية",
    "تحاليل", "مناقصة", "مستشفى", "أدوية", "عيادات"
]

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_google_health_news():
    """البحث في الأخبار الرسمية وإعلانات المستشفيات والقطاع الصحي السعودي"""
    rss_url = "https://news.google.com/rss/search?q=%D9%85%D9%86%D8%A7%D9%82%D8%B5%D8%A9+%D9%85%D8%B3%D8%AA%D8%B4%D9%81%D9%89+%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9&hl=ar&gl=SA&ceid=SA:ar"
    tenders = []
    try:
        res = requests.get(rss_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for item in root.findall('.//item')[:3]:
                title = clean_text(item.find('title').text if item.find('title') is not None else '')
                link = item.find('link').text if item.find('link') is not None else ''
                
                if any(kw in title for kw in HEALTH_KEYWORDS):
                    tenders.append(
                        f"🏥 **إعلان/خبر صحي (مستشفيات وقطاع خاص):**\n"
                        f"📌 **التفاصيل:** {title}\n"
                        f"🔗 [مصدر الخبر والتفاصيل]({link})"
                    )
    except Exception as e:
        print(f"خطأ في جلب الأخبار العامة: {e}")
    return tenders

def fetch_etimad_tenders():
    """منصة اعتماد - المنافسات الحكومية"""
    url = "https://monaqasat.etimad.sa/Tender/AllTendersForVisitor?SearchKey=%D8%B5%D8%AD%D8%A9"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_='card-body', limit=3)
            for card in cards:
                title_tag = card.find('h3') or card.find('a')
                if title_tag:
                    title = clean_text(title_tag.get_text())
                    if any(kw in title for kw in HEALTH_KEYWORDS):
                        tenders.append(
                            f"🟢 **منصة اعتماد الحكومية:**\n"
                            f"📌 **المنافسة:** {title}\n"
                            f"🔗 [عرض المنافسة في اعتماد]({url})"
                        )
    except Exception as e:
        print(f"خطأ اعتماد: {e}")
    return tenders

def fetch_nupco_tenders():
    """الشراء الموحد - نوبكو NUPCO"""
    url = "https://nupco.com/tenders/"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all(['tr', 'li', 'div'], limit=15)
            for item in items:
                txt = clean_text(item.get_text())
                if any(kw in txt for kw in HEALTH_KEYWORDS) and len(txt) > 20 and "HomeAbout" not in txt:
                    tenders.append(
                        f"💊 **بوابة نوبكو (NUPCO):**\n"
                        f"📌 **التفاصيل:** {txt[:150]}...\n"
                        f"🔗 [رابط منافسات نوبكو]({url})"
                    )
                    break
    except Exception as e:
        print(f"خطأ نوبكو: {e}")
    return tenders

def fetch_tenders(url=None):
    all_results = []
    all_results.extend(fetch_google_health_news())
    all_results.extend(fetch_etimad_tenders())
    all_results.extend(fetch_nupco_tenders())
    return all_results

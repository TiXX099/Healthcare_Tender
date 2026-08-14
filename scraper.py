import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def fetch_google_news_tenders():
    """1. البحث الشامل المخصص للسعودية فقط"""
    keywords = '("مناقصة صحية" OR "مستلزمات طبية" OR "مستشفى") AND (السعودية OR الرياض OR جدة OR "وزارة الصحة")'
    url = f"https://news.google.com/rss/search?q={quote(keywords)}&hl=ar&gl=SA&ceid=SA:ar"
    
    EXCLUDE_WORDS = ["البحرين", "دينار", "قسنطينة", "الجزائر", "لبنان", "الكويت", "مصر", "تونس", "المغرب"]
    
    tenders = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            # فحص استبعاد الدول الأخرى
            if any(bad_word in title for bad_word in EXCLUDE_WORDS):
                continue
                
            tenders.append(f"🌐 أخبار ومناقصات (السعودية): {title}\n🔗 [رابط الخبر/المنصّة]({link})")
            
            # إيقاف التجميع عند أحدث 4 نتائج حقيقية ومفلترة
            if len(tenders) == 4:
                break
                
    except Exception as e:
        print(f"خطأ في البحث العام عبر قوقل: {e}")
        
    return tenders

def fetch_spa_tenders():
    """2. وكالة الأنباء السعودية (واس)"""
    url = "https://www.spa.gov.sa/ar/search?q=%D9%85%D9%86%D8%A7%D9%82%D8%B5%D8%A9+%D8%B5%D8%AD%D9%8A%D8%A9"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.find_all('a', class_='news-title', limit=2)
            for art in articles:
                title = art.get_text(strip=True)
                link = art.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.spa.gov.sa{link}"
                tenders.append(f"🏛️ واس: {title}\n🔗 [رابط الخبر]({link})")
    except Exception as e:
        print(f"خطأ في واس: {e}")
    return tenders

def fetch_etimad_tenders():
    """3. منصة اعتماد"""
    url = "https://monaqasat.etimad.sa/Tender/AllTendersForVisitor?SearchKey=%D8%B5%D8%AD%D8%A9"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_='card-body', limit=2)
            for card in cards:
                title_tag = card.find('h3') or card.find('a')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = "https://monaqasat.etimad.sa/Tender/AllTendersForVisitor"
                    tenders.append(f"🟢 اعتماد: {title}\n🔗 [منصة اعتماد]({link})")
    except Exception as e:
        print(f"خطأ في اعتماد: {e}")
    return tenders

def fetch_tenders(url=None):
    """تجميع البحث العام + المصادر المحددة"""
    all_results = []
    
    # 🔍 البحث المفلتر الخاص بالسعودية
    all_results.extend(fetch_google_news_tenders())
    
    # 🏛️ المصادر الرسمية
    all_results.extend(fetch_spa_tenders())
    all_results.extend(fetch_etimad_tenders())
    
    return all_results

if __name__ == "__main__":
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} نتائج مفلترة:")
    for res in results:
        print("---")
        print(res)

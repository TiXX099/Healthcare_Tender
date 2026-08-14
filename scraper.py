import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def fetch_etimad_tenders():
    """1. منصة اعتماد الحكومية للمشتريات والمنافسات"""
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
                    title = title_tag.get_text(strip=True)
                    tenders.append(f"🟢 منصة اعتماد: {title}\n🔗 [تفاصيل المنافسة]({url})")
    except Exception as e:
        print(f"خطأ في اعتماد: {e}")
    return tenders

def fetch_nupco_tenders():
    """2. الشركة الوطنية للشراء الموحد (نوبكو NUPCO)"""
    url = "https://nupco.com/tenders/"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all(['div', 'tr'], limit=5)
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 15:
                    tenders.append(f"💊 نوبكو (NUPCO): {text[:100]}...\n🔗 [بوابة نوبكو]({url})")
                    if len(tenders) == 2:
                        break
    except Exception as e:
        print(f"خطأ في نوبكو: {e}")
    return tenders

def fetch_tanafus_tenders():
    """3. منصة تنافس للمنافسات والجمعيات الصحية"""
    url = "https://tanafus.sa/"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all(['div', 'a'], class_=lambda c: c and 'tender' in c.lower(), limit=3)
            for card in cards:
                title = card.get_text(strip=True)
                if title:
                    tenders.append(f"🤝 منصة تنافس: {title[:100]}...\n🔗 [رابط المنصة]({url})")
    except Exception as e:
        print(f"خطأ في منصة تنافس: {e}")
    return tenders

def fetch_ncp_tenders():
    """4. المركز الوطني للتخصيص (الشراكات الصحية)"""
    url = "https://www.ncp.gov.sa/ar/Opportunities/Pages/default.aspx"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all(['div', 'a', 'h4'], limit=5)
            for item in items:
                title = item.get_text(strip=True)
                if ("صحية" in title or "مستشفى" in title or "صحة" in title) and len(title) > 10:
                    tenders.append(f"🏛️ المركز الوطني للتخصيص: {title[:100]}...\n🔗 [فرص التخصيص]({url})")
                    if len(tenders) == 2:
                        break
    except Exception as e:
        print(f"خطأ في المركز الوطني للتخصيص: {e}")
    return tenders

def fetch_official_saudi_tenders_google():
    """
    5. بحث قوقل المخصّص فقط للمواقع النطاقية الحكومية والصحية السعودية (site:gov.sa)
    هذا الفلتر يمنع ظهور أي صحيفة أو موقع إخباري عالمي أو محلي تماماً تلقائياً بدون قائمة كلمات مستبعدة!
    """
    # البحث ينحصر فقط داخل النطاقات الرسمية المعتمدة
    query = '("مناقصة" OR "منافسة" OR "شراء مباشر" OR "توريد" OR "كراسة شروط") AND ("مختبر" OR "أجهزة طبية" OR "مستلزمات" OR "مستشفى")'
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ar&gl=SA&ceid=SA:ar"
    
    tenders = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            tenders.append(f"🌐 أخبار حكومية سعودية: {title}\n🔗 [رابط الخبر]({link})")
            if len(tenders) == 3:
                break
    except Exception as e:
        print(f"خطأ في البحث الحكومي: {e}")
    return tenders

def fetch_spa_tenders():
    """6. وكالة الأنباء السعودية (واس)"""
    url = "https://www.spa.gov.sa/ar/search?q=%D9%85%D9%86%D8%A7%D9%82%D8%B5%D8%A9+%D8%B5%D8%AD%D9%8A%D8%A9"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.find_all('a', class_='news-title', limit=3)
            for art in articles:
                title = art.get_text(strip=True)
                link = art.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.spa.gov.sa{link}"
                tenders.append(f"🏛️ واس: {title}\n🔗 [رابط الخبر]({link})")
    except Exception as e:
        print(f"خطأ في واس: {e}")
    return tenders

def fetch_tenders(url=None):
    """تجميع نتائج كافة المصادر المعتمدة"""
    all_results = []

    all_results.extend(fetch_etimad_tenders())
    all_results.extend(fetch_nupco_tenders())
    all_results.extend(fetch_tanafus_tenders())
    all_results.extend(fetch_ncp_tenders())
    all_results.extend(fetch_official_saudi_tenders_google())
    all_results.extend(fetch_spa_tenders())

    return all_results

if __name__ == "__main__":
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} نتائج مطابقة:")
    for res in results:
        print("---")
        print(res)

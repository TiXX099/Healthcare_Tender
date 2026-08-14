import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def fetch_spa_tenders():
    """1. سحب أخبار ومناقصات وكالة الأنباء السعودية (واس)"""
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
                tenders.append(f"🏛️ واس: {title}\n🔗 [رابط الخبر/المناقصة]({link})")
    except Exception as e:
        print(f"خطأ في واس: {e}")
    return tenders

def fetch_etimad_tenders():
    """2. سحب مناقصات منصة اعتماد للقطاع الصحي"""
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
                    link = "https://monaqasat.etimad.sa/Tender/AllTendersForVisitor"
                    tenders.append(f"🟢 اعتماد: {title}\n🔗 [تفاصيل منصة اعتماد]({link})")
    except Exception as e:
        print(f"خطأ في اعتماد: {e}")
    return tenders

def fetch_nupco_tenders():
    """3. سحب مناقصات شركة الشراء الموحد (نوبكو)"""
    url = "https://nupco.com/tenders/"
    tenders = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='tender-item', limit=3) or soup.find_all('tr', limit=3)
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 10:
                    tenders.append(f"💊 نوبكو (NUPCO): {text[:100]}...\n🔗 [بوابة نوبكو]({url})")
    except Exception as e:
        print(f"خطأ في نوبكو: {e}")
    return tenders

def fetch_tenders(url=None):
    """تجميع جميع المناقصات من المصادر المختلفة"""
    all_results = []
    
    # 1. جلب من واس
    all_results.extend(fetch_spa_tenders())
    
    # 2. جلب من اعتماد
    all_results.extend(fetch_etimad_tenders())
    
    # 3. جلب من نوبكو
    all_results.extend(fetch_nupco_tenders())
    
    return all_results

if name == "__main__":
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} نتائج إجمالاً:")
    for res in results:
        print("---")
        print(res)

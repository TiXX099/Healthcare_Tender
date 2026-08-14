import requests
from bs4 import BeautifulSoup

def fetch_tenders(url=None):
    """
    سحب أحدث الأخبار والإعلانات الصحّية والمناقصات من وكالة الأنباء السعودية (واس)
    """
    target_url = "https://www.spa.gov.sa/ar/search?q=%D9%85%D9%86%D8%A7%D9%82%D8%B5%D8%A9+%D8%B5%D8%AD%D9%8A%D8%A9"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    tenders = []
    
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن العناوين والروابط في نتائج البحث
            articles = soup.find_all('a', class_='news-title', limit=3)  # نأخذ أحدث 3 أخبار
            
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.spa.gov.sa{link}"
                
                tenders.append(f"📌 **{title}**\n🔗 [رابط التفاصيل]({link})")
        else:
            print(f"فشل الاتصال بالموقع، رمز الاستجابة: {response.status_code}")
            
    except Exception as e:
        print(f"حدث خطأ أثناء سحب البيانات: {e}")
        
    return tenders

if name == "__main__":
    # تجربة سريعة للتحقق من الكود
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} نتائج.")
    for res in results:
        print(res)

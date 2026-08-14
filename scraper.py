def fetch_google_news_tenders():
    """5. البحث العام المفلتر عبر قوقل"""
    keywords = '("مناقصة" OR "توريد" OR "تأمين" OR "منافسة" OR "مختبر" OR "تحليل") AND ("مستلزمات طبية" OR "أجهزة طبية" OR "مستشفى" OR "مختبرات") AND (السعودية OR المملكة OR "وزارة الصحة" OR "تجمع صحي")'
    url = f"https://news.google.com/rss/search?q={quote(keywords)}&hl=ar&gl=SA&ceid=SA:ar"
    
    tenders = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            if is_targeted_tender(title):
                tenders.append(f"🌐 أخبار ومناقصات (السعودية): {title}\n🔗 [رابط الخبر/المنصّة]({link})")
            
            if len(tenders) == 3:
                break
    except Exception as e:
        print(f"خطأ في قوقل: {e}")
        
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
                if is_targeted_tender(title):
                    link = art.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.spa.gov.sa{link}"
                    tenders.append(f"🏛️ واس: {title}\n🔗 [رابط الخبر]({link})")
    except Exception as e:
        print(f"خطأ في واس: {e}")
    return tenders

def fetch_tenders(url=None):
    """تجميع كافة المصادر المعتمدة"""
    all_results = []
    
    all_results.extend(fetch_etimad_tenders())
    all_results.extend(fetch_nupco_tenders())
    all_results.extend(fetch_tanafus_tenders())
    all_results.extend(fetch_ncp_tenders())
    all_results.extend(fetch_google_news_tenders())
    all_results.extend(fetch_spa_tenders())
    
    return all_results

if __name__ == "__main__":
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} نتائج مطابقة:")
    for res in results:
        print("---")
        print(res)

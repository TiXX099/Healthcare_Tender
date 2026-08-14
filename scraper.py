import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def fetch_etimad_tenders():
    """1. منصة اعتماد الحكومية للمشتريات والمنافسات الصحية"""
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
                    tenders.append(f"🟢 **منصة اعتماد الحكومية:**\n{title}\n🔗 [عرض المنافسة في اعتماد]({url})")
    except Exception as e:
        print(f"خطأ في اعتماد: {e}")
    return tenders

def fetch_nupco_tenders():
    """2. الشركة الوطنية للشراء الموحد (نوبكو NUPCO)"""
    url = "https://nupco.com/tenders/"
    tenders = []
    try:
        # إرسال رابط مباشر لبوابة المنافسات دون سحب الهيدر وقوائم الموقع
        tenders.append(
            "💊 **بوابة نوبكو للشراء الموحد (NUPCO):**\n"
            "تحديث قائمة المنافسات والمناقصات الطبية المتاحة حالياً.\n"
            f"🔗 [استعراض منافسات نوبكو المباشرة]({url})"
        )
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
            cards = soup.find_all(['div', 'a'], class_=lambda c: c and 'tender' in c.lower(), limit=2)
            for card in cards:
                title = card.get_text(strip=True)
                if title and len(title) > 10:
                    tenders.append(f"🤝 **منصة تنافس:**\n{title[:100]}...\n🔗 [رابط المنصة]({url})")
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
                    tenders.append(f"🏛️ **المركز الوطني للتخصيص:**\n{title[:100]}...\n🔗 [تفاصيل الفرصة]({url})")
                    if len(tenders) == 1:
                        break
    except Exception as e:
        print(f"خطأ في المركز الوطني للتخصيص: {e}")
    return tenders

def fetch_tenders(url=None):
    """تجميع البيانات النظيفة والدقيقة"""
    all_results = []
    all_results.extend(fetch_etimad_tenders())
    all_results.extend(fetch_nupco_tenders())
    all_results.extend(fetch_tanafus_tenders())
    all_results.extend(fetch_ncp_tenders())
    return all_results

if __name__ == "__main__":
    results = fetch_tenders()
    print(f"تم جلب {len(results)} نتائج نظيفة:")
    for res in results:
        print("---")
        print(res)

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def clean_text(text):
    """تنظيف النص من المسافات الزائدة والسطور الفارغة"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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
                    title = clean_text(title_tag.get_text())
                    if len(title) > 5:
                        tenders.append(f"🟢 منصة اعتماد الحكومية:**\n📌 **المنافسة: {title}\n🔗 [عرض المنافسة في اعتماد]({url})")
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
            items = soup.find_all(['tr', 'div', 'li'], class_=lambda c: c and any(k in str(c).lower() for k in ['tender', 'item', 'row']), limit=10)
            
            for item in items:
                text = clean_text(item.get_text())
                if any(word in text for word in ["توريد", "منافسة", "شراء", "تأمين", "أجهزة", "مستلزمات", "مختبر", "صحة", "طبية"]):
                    if len(text) > 20 and "HomeAbout" not in text:
                        tenders.append(f"💊 بوابة نوبكو (NUPCO):**\n📌 **تفاصيل المنافسة: {text[:150]}...\n🔗 [رابط المنافسة]({url})")
                        if len(tenders) == 3:
                            break
                            
        if not tenders:
            tenders.append(
                "💊 **بوابة نوبكو (NUPCO):**\n"
                "📌 المنافسة: طرح منافسات وتوريدات طبية ومخبرية جديدة عبر الشراء الموحد.\n"
                f"🔗 [استعراض قائمة المنافسات المباشرة]({url})"
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
            cards = soup.find_all(['div', 'a'], class_=lambda c: c and 'tender' in str(c).lower(), limit=2)
            for card in cards:
                title = clean_text(card.get_text())
                if title and len(title) > 10 and "Home" not in title:
                    tenders.append(f"🤝 منصة تنافس:**\n📌 **المنافسة: {title[:120]}\n🔗 [رابط المنصة]({url})")
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
                title = clean_text(item.get_text())
                if ("صحية" in title or "مستشفى" in title or "صحة" in title) and len(title) > 10:
                    tenders.append(f"🏛️ المركز الوطني للتخصيص:**\n📌 **الفرصة: {title[:120]}\n🔗 [تفاصيل الفرصة]({url})")
                    if len(tenders) == 1:
                        break
    except Exception as e:
        print(f"خطأ في المركز الوطني للتخصيص: {e}")
    return tenders

def fetch_tenders():
    """تجميع النتائج من جميع المصادر المعتمدة"""
    all_results = []
    all_results.extend(fetch_etimad_tenders())
    all_results.extend(fetch_nupco_tenders())
    all_results.extend(fetch_tanafus_tenders())
    all_results.extend(fetch_ncp_tenders())
    return all_results

if __name__ == "__main__":
    results = fetch_tenders()
    print(f"تم العثور على {len(results)} مناقصة ومنافسة:")
    for res in results:
        print("---")
        print(res)

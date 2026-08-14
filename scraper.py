import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import quote

HEADERS = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# 🎯 الكلمات الدلالية المستهدفة
TARGET_KEYWORDS = [
"مناقصة", "منافسة", "تأمين", "توريد", "شراء مباشر",
"مستلزمات طبية", "أجهزة طبية", "تشغيل مستشفى", "عقد", "صيانة طبية",
"مختبر", "مختبرات", "تحليل", "تحاليل", "محاليل", "كواشف", "تخصيص"
]

# 🚫 كلمات مستبعدة
EXCLUDE_WORDS = [
"البحرين", "دينار", "الجزائر", "لبنان", "الكويت", "مصر", "تونس",
"مساعدات", "إغاثة", "تبرع", "أنقذت", "اللاذقية", "مأرب"
]

def is_targeted_tender(title):
if any(bad_word in title for bad_word in EXCLUDE_WORDS):
return False
if any(good_word in title for good_word in TARGET_KEYWORDS):
return True
return False

def fetch_etimad_tenders():
"""1. منصة اعتماد الحكومية"""
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
tenders.append(f"🟢 **اعتماد:** {title}\n🔗 [منصة اعتماد]({url})")
except Exception as e:
print(f"خطأ في اعتماد: {e}")
return tenders

def fetch_nupco_tenders():
"""2. الشركة الوطنية للشراء الموحد (نوبكو - NUPCO)"""
url = "https://nupco.com/tenders/"
tenders = []
try:
res = requests.get(url, headers=HEADERS, timeout=10)
if res.status_code == 200:
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.find_all(['div', 'tr'], limit=5)
for item in items:
text = item.get_text(strip=True)
if text and len(text) > 15 and is_targeted_tender(text):
tenders.append(f"💊 **نوبكو (NUPCO):** {text[:100]}...\n🔗 [منصة نوبكو]({url})")
if len(tenders) == 2:
break
except Exception as e:
print(f"خطأ في نوبكو: {e}")
return tenders

def fetch_tanafus_tenders():
"""3. منصة تنافس (Tanafus)"""
url = "https://tanafus.sa/"
tenders = []
try:
res = requests.get(url, headers=HEADERS, timeout=10)
if res.status_code == 200:
soup = BeautifulSoup(res.text, 'html.parser')
cards = soup.find_all(['div', 'a'], class_=lambda c: c and 'tender' in c.lower(), limit=3)
for card in cards:
title = card.get_text(strip=True)
if title and is_targeted_tender(title):
tenders.append(f"🤝 **تنافس:** {title[:100]}...\n🔗 [منصة تنافس]({url})")
except Exception as e:
print(f"خطأ في منصة تنافس: {e}")
return tenders

def fetch_ncp_tenders():
"""4. المركز الوطني للتخصيص (NCP)"""
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
tenders.append(f"🏛️ **المركز الوطني للتخصيص:** {title[:100]}...\n🔗 [فرص التخصيص]({url})")
if len(tenders) == 2:
break
except Exception as e:
print(f"خطأ في المركز الوطني للتخصيص: {e}")
return tenders

def fetch_google_news_tenders():
"""5. البحث العام عبر قوقل"""
keywords = '("مناقصة" OR "توريد" OR "تأمين" OR "منافسة" OR "مختبر" OR "تحليل") AND ("مستلزمات طبية" OR "أجهزة طبية" OR "مستشفى" OR "مختبرات") AND (السعودية OR المملكة OR "وزارة الصحة" OR "تجمع صحي")'
url = f"https://news.google.com/rss/search?q={quote(keywords)}&hl=ar&gl=SA&ceid=SA:ar"

tenders = []
try:
feed = feedparser.parse(url)
for entry in feed.entries:
title = entry.title
link = entry.link

if is_targeted_tender(title):
tenders.append(f"🌐 **أخبار ومناقصات (السعودية):** {title}\n🔗 [رابط الخبر/المنصّة]({link})")

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
tenders.append(f"🏛️ **واس:** {title}\n🔗 [رابط الخبر]({link})")
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
all_results.extend(fetch_google_news_tenders())
all_results.extend(fetch_spa_tenders())

return all_results

if __name__ == "__main__":
results = fetch_tenders()
print(f"تم العثور على {len(results)} نتائج مطابقة:")
for res in results:
print("---")
print(res)

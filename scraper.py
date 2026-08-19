import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

KEYWORDS = [
    "مناقصة", "منافسة", "مختبر", "أجهزة", "طبية", "تجهيز", 
    "توريد", "مستشفى", "صحة", "دواء", "مستلزمات", "كواشف", "عقد", "نوبكو", "اعتماد"
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_google_rss(query):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=SA&ceid=SA:ar"
    results = []
    
    try:
        res = requests.get(rss_url, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for item in root.findall('.//item')[:5]:
                title = clean_text(item.find('title').text if item.find('title') is not None else '')
                link = item.find('link').text if item.find('link') is not None else ''
                
                if title and link:
                    results.append({
                        "title": title,
                        "link": link
                    })
    except Exception as e:
        print(f"Error fetching RSS for '{query}': {e}")
    return results

def fetch_tenders():
    all_tenders = []
    
    queries = [
        "مناقصة صحة السعودية",
        "منافسات وزارة الصحة السعودية",
        "مختبرات ومستلزمات طبية السعودية",
        "مناقصات نوبكو السعودية"
    ]
    
    seen_titles = set()
    
    for q in queries:
        items = fetch_google_rss(q)
        for item in items:
            title = item["title"]
            if title not in seen_titles:
                if any(kw in title for kw in KEYWORDS):
                    seen_titles.add(title)
                    formatted_msg = (
                        f"🏥 **تحديث القطاع الصحي والمناقصات:**\n"
                        f"📌 {title}\n\n"
                        f"🔗 [عرض التفاصيل والمصدر]({item['link']})"
                    )
                    all_tenders.append(formatted_msg)
                    
    return all_tenders

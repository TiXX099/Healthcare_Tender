 import requests
from bs4 import BeautifulSoup

def fetch_tenders(url):
    """
    دالة لجلب بيانات المناقصات من الموقع المحدد
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tenders = []
        print("تم الاتصال بالموقع بنجاح!")
        
        return tenders

    except Exception as e:
        print(f"حدث خطأ أثناء جلب البيانات: {e}")
        return []

if name == "__main__":
    target_url = "https://example.com"
    fetch_tenders(target_url)

# chatbot/google_searcher.py (সরল)
from googlesearch import search
import requests
from bs4 import BeautifulSoup

class GoogleSearcher:
    def search_google(self, query, num_results=3):
        """সরল গুগল সার্চ"""
        try:
            results = []
            for url in search(query + " বাংলায়", num_results=num_results):
                # কিছু ওয়েবসাইট থেকে কন্টেন্ট নেওয়া
                content = self.get_web_content(url)
                results.append({
                    'url': url,
                    'content': content[:200] if content else f"'{query}' সম্পর্কিত তথ্য"
                })
            return results
        except:
            return []
    
    def get_web_content(self, url):
        """ওয়েবসাইট থেকে কন্টেন্ট"""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()[:500]  # প্রথম ৫০০ অক্ষর
            return ' '.join(text.split())  # স্পেস ক্লিন
        except:
            return None

import requests
from googlesearch import search
from bs4 import BeautifulSoup
import re
import time

class GoogleSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def search_google(self, query, num_results=3):
        """গুগল থেকে তথ্য খোঁজা"""
        try:
            # বাংলা query যোগ
            query_with_lang = f"{query} site:.bd OR site:.com বাংলায়"
            
            search_results = []
            urls = list(search(query_with_lang, num_results=num_results, advanced=True))
            
            for result in urls[:num_results]:
                try:
                    url = result.url
                    content = self.extract_content(url)
                    
                    if content and len(content) > 50:
                        search_results.append({
                            'url': url,
                            'title': getattr(result, 'title', 'No title'),
                            'content': content[:800],
                            'query': query
                        })
                except Exception as e:
                    continue
                
                time.sleep(0.5)  # Polite delay
            
            return search_results
            
        except Exception as e:
            print(f"গুগল সার্চ ত্রুটি: {e}")
            # Fallback to simple search
            return self.simple_search(query, num_results)
    
    def simple_search(self, query, num_results):
        """সরল সার্চ (বিকল্প)"""
        try:
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            results = ddgs.text(query + " বাংলায়", region='bn-bd', max_results=num_results)
            
            search_results = []
            for result in results:
                search_results.append({
                    'url': result.get('href', ''),
                    'title': result.get('title', ''),
                    'content': result.get('body', '')[:500],
                    'query': query
                })
            
            return search_results
            
        except:
            return []
    
    def extract_content(self, url):
        """ওয়েবসাইট থেকে মূল কন্টেন্ট বের করা"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # অপ্রয়োজনীয় ট্যাগ রিমুভ
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # মূল কন্টেন্ট এলাকা
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # বাংলা টেক্সট ফিল্টার
            bangla_text = []
            sentences = text.split('.')
            
            for sentence in sentences:
                # বাংলা ইউনিকোড চেক
                if re.search(r'[\u0980-\u09FF]', sentence):
                    clean_sentence = re.sub(r'\s+', ' ', sentence.strip())
                    if len(clean_sentence) > 10:
                        bangla_text.append(clean_sentence)
            
            return '. '.join(bangla_text[:15])  # প্রথম ১৫টি বাক্য
        
        except Exception as e:
            print(f"Content extraction error for {url}: {e}")
            return None

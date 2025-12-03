import requests
from bs4 import BeautifulSoup
import re

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_bangla_sites(self, query):
        """বাংলা ওয়েবসাইট স্ক্রেপ"""
        bangla_sites = [
            'https://bn.wikipedia.org/wiki/',
            'https://www.prothomalo.com/',
            'https://www.bbc.com/bengali',
            'https://www.kalerkantho.com/'
        ]
        
        results = []
        
        for site in bangla_sites:
            try:
                # Wikipedia বিশেষ হ্যান্ডলিং
                if 'wikipedia' in site:
                    wiki_result = self.scrape_wikipedia(query)
                    if wiki_result:
                        results.append(wiki_result)
                
                # অন্যান্য সাইট
                else:
                    content = self.scrape_site(site, query)
                    if content:
                        results.append({
                            'url': site,
                            'content': content[:500]
                        })
            
            except:
                continue
        
        return results
    
    def scrape_wikipedia(self, query):
        """উইকিপিডিয়া স্ক্রেপ"""
        try:
            import wikipediaapi
            
            wiki_wiki = wikipediaapi.Wikipedia(
                language='bn',
                user_agent='BanglaChatbot/1.0'
            )
            
            page = wiki_wiki.page(query)
            
            if page.exists():
                return {
                    'url': page.fullurl,
                    'content': page.summary[:800]
                }
        
        except:
            # সরল রিকোয়েস্ট
            try:
                url = f"https://bn.wikipedia.org/wiki/{query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    text = content_div.get_text(separator=' ', strip=True)
                    return {
                        'url': url,
                        'content': text[:800]
                    }
            
            except:
                pass
        
        return None
    
    def scrape_site(self, url, query):
        """সাধারণ সাইট স্ক্রেপ"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # বাংলা কন্টেন্ট ফিল্টার
            all_text = soup.get_text()
            bangla_sentences = []
            
            for sentence in all_text.split('.'):
                if re.search(r'[\u0980-\u09FF]', sentence):
                    clean_sent = re.sub(r'\s+', ' ', sentence.strip())
                    if len(clean_sent) > 20:
                        bangla_sentences.append(clean_sent)
            
            return '. '.join(bangla_sentences[:10])
        
        except:
            return None

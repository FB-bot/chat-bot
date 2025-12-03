from flask import Flask, render_template, request, jsonify, session
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bangla-chatbot-secret-2024')

class BengaliChatbot:
    def __init__(self):
        self.knowledge_file = 'knowledge.json'
        self.knowledge = self.load_knowledge()
        
    def load_knowledge(self):
        """জ্ঞান লোড"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_knowledge(self):
        """জ্ঞান সেভ"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_response(self, question):
        """উত্তর দাও"""
        question_lower = question.lower().strip()
        
        # ১. নিজের জ্ঞানে আছে কিনা চেক
        if question_lower in self.knowledge:
            return {
                'answer': self.knowledge[question_lower],
                'source': 'memory',
                'learned': False
            }
        
        # ২. না থাকলে গুগল সার্চ
        google_result = self.google_search(question)
        
        if google_result['found']:
            # ৩. শিখে নাও (মেমরিতে সেভ)
            self.knowledge[question_lower] = google_result['answer']
            self.save_knowledge()
            
            return {
                'answer': google_result['answer'],
                'source': 'google',
                'url': google_result.get('url'),
                'learned': True
            }
        
        # ৪. কিছু না পেলে
        return {
            'answer': 'দুঃখিত, এই প্রশ্নের উত্তর আমি খুঁজে পাইনি।',
            'source': 'none',
            'learned': False
        }
    
    def google_search(self, query):
        """গুগল থেকে তথ্য খোঁজা"""
        try:
            # বাংলা কোয়েরি
            search_query = f"{query} বাংলায়"
            
            # প্রথম ৩টি রেজাল্ট নাও
            urls = list(search(search_query, num_results=3, lang='bn'))
            
            if not urls:
                return {'found': False}
            
            # প্রথম ওয়েবসাইট থেকে কন্টেন্ট নাও
            for url in urls:
                content = self.scrape_website(url)
                if content and len(content) > 20:  # কিছু কন্টেন্ট থাকলে
                    return {
                        'found': True,
                        'answer': content[:400] + "..." if len(content) > 400 else content,
                        'url': url
                    }
            
            return {'found': False}
            
        except Exception as e:
            print(f"Google search error: {e}")
            return {'found': False}
    
    def scrape_website(self, url):
        """ওয়েবসাইট থেকে টেক্সট নেওয়া"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (BanglaChatBot/1.0; +https://github.com)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # সব টেক্সট নাও
            text = soup.get_text()
            
            # বাংলা টেক্সট ফিল্টার
            import re
            sentences = text.split('.')
            bangla_sentences = []
            
            for sentence in sentences:
                # বাংলা ইউনিকোড চেক
                if re.search(r'[\u0980-\u09FF]', sentence):
                    clean = ' '.join(sentence.strip().split())
                    if len(clean) > 10:
                        bangla_sentences.append(clean)
            
            if bangla_sentences:
                return '. '.join(bangla_sentences[:5]) + '.'
            
            # বাংলা না থাকলে ইংরেজি
            return text[:300] + "..."
            
        except:
            return None
    
    def manual_learn(self, question, answer):
        """ম্যানুয়ালি শেখানো"""
        self.knowledge[question.lower().strip()] = answer
        self.save_knowledge()
        return True

# চ্যাটবট তৈরি
chatbot = BengaliChatbot()

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().timestamp()}"
        session['search_count'] = 0
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'খালি মেসেজ'}), 400
        
        # চ্যাটবট থেকে উত্তর নাও
        response = chatbot.get_response(user_message)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learn', methods=['POST'])
def learn():
    try:
        data = request.json
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        
        if not question or not answer:
            return jsonify({'error': 'প্রশ্ন এবং উত্তর দিতে হবে'}), 400
        
        chatbot.manual_learn(question, answer)
        
        return jsonify({
            'success': True,
            'message': '✅ শিখে নিলাম!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        'total_knowledge': len(chatbot.knowledge),
        'knowledge_file': os.path.exists(chatbot.knowledge_file)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

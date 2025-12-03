import json
import random
import time
from datetime import datetime
from .memory import MemoryManager
from .safety import SafetyChecker
from .google_searcher import GoogleSearcher
from .smart_learner import SmartLearner
from .web_scraper import WebScraper

class BengaliChatbot:
    def __init__(self):
        self.memory = MemoryManager()
        self.safety = SafetyChecker()
        self.searcher = GoogleSearcher()
        self.learner = SmartLearner()
        self.scraper = WebScraper()
        
        # সেটিংস
        self.enable_web_search = True
        self.max_searches_per_day = 50
        self.search_delay = 2  # seconds
        
        # স্ট্যাটস
        self.total_searches = 0
        self.last_search_time = 0
        
        # প্রাথমিক জ্ঞান লোড
        self.base_knowledge = {
            "greeting": {
                "patterns": ["হ্যালো", "হাই", "নমস্কার", "কেমন আছ", "কি অবস্থা", "আসসালামু আলাইকুম"],
                "responses": [
                    "ওয়ালাইকুম আসসালাম! আমি আপনার বাংলা AI চ্যাটবট। 😊",
                    "হ্যালো! আমি আপনার সহায়ক বট। কিভাবে সাহায্য করতে পারি?",
                    "নমস্কার! আজকে আপনাকে কিভাবে সহায়তা করতে পারি?",
                    "হাই! কেমন আছেন আপনি?"
                ]
            },
            "farewell": {
                "patterns": ["বিদায়", "বাই", "চললাম", "আল্লাহ হাফেজ", "খোদা হাফেজ"],
                "responses": [
                    "বিদায়! আল্লাহ হাফেজ। 🙏",
                    "আবার কথা হবে ইনশাআল্লাহ!",
                    "চলুন, শুভকামনা রইল।"
                ]
            },
            "identity": {
                "patterns": ["তোমার নাম", "তুমি কে", "তোমাকে বানিয়েছে", "তোমার কাজ"],
                "responses": [
                    "আমার নাম বাংলা AI চ্যাটবট! আমি গুগল থেকে তথ্য নিয়ে আপনার প্রশ্নের উত্তর দিতে পারি।",
                    "আমি একজন স্মার্ট AI চ্যাটবট, বাংলায় কথা বলতে পারি এবং নতুন জিনিস শিখতে পারি।",
                    "আমাকে বানিয়েছে একজন বাংলাদেশি ডেভেলপার। আমি গুগল থেকে তথ্য সংগ্রহ করে উত্তর দেই।"
                ]
            },
            "capabilities": {
                "patterns": ["তুমি কি করতে পার", "তোমার ক্ষমতা", "তোমার ফিচার"],
                "responses": [
                    "আমি করতে পারি: ১. বাংলায় কথা বলা ২. গুগল থেকে তথ্য নিয়ে আসা ৩. নতুন জিনিস শেখা ৪. আপনার প্রশ্নের উত্তর দেওয়া",
                    "আমার বিশেষত্ব: আমি ইন্টারনেট থেকে তথ্য সংগ্রহ করে আপনাকে দেই এবং সেই তথ্য মনে রাখি পরেরবারের জন্য!",
                    "আমি একটি সেল্ফ-লার্নিং বট। আপনি যা শেখাবেন, আমি তা মনে রাখবো এবং গুগল থেকেও নতুন তথ্য শিখবো।"
                ]
            }
        }
    
    def process_message(self, user_input, user_id, web_search=True):
        """ইউজার মেসেজ প্রসেস"""
        # ১. ছোট করি
        user_input_lower = user_input.lower().strip()
        
        # ২. ফর্মাল রেসপন্স চেক
        formal_response = self.check_formal_queries(user_input_lower)
        if formal_response:
            return self._format_response(formal_response, "base_knowledge")
        
        # ৩. স্মার্ট লার্নার থেকে চেক
        smart_response = self.learner.get_auto_answer(user_input)
        if smart_response:
            return self._format_response(smart_response, "learned_smart")
        
        # ৪. মেমরি থেকে চেক
        memory_response = self.memory.get_response(user_input_lower)
        if memory_response:
            return self._format_response(memory_response, "learned")
        
        # ৫. ওয়েব সার্চ (যদি চালু থাকে)
        if web_search and self.enable_web_search and self.can_search():
            web_result = self.try_web_search(user_input, user_id)
            if web_result:
                return web_result
        
        # ৬. ডিফল্ট রেসপন্স
        return self._format_response(
            self._get_smart_response(user_input),
            "ai_generated"
        )
    
    def check_formal_queries(self, user_input):
        """বেসিক প্রশ্ন চেক"""
        for category, data in self.base_knowledge.items():
            for pattern in data["patterns"]:
                if pattern in user_input:
                    return random.choice(data["responses"])
        return None
    
    def can_search(self):
        """সার্চ করা যাবে কিনা চেক"""
        current_time = time.time()
        
        # রেট লিমিটিং
        if current_time - self.last_search_time < self.search_delay:
            return False
        
        # দৈনিক লিমিট
        if self.total_searches >= self.max_searches_per_day:
            return False
        
        return True
    
    def try_web_search(self, query, user_id):
        """ওয়েব সার্চ চেষ্টা"""
        try:
            self.last_search_time = time.time()
            self.total_searches += 1
            
            # গুগল সার্চ
            search_results = self.searcher.search_google(query, num_results=3)
            
            if search_results:
                # সবচেয়ে ভালো উত্তর বাছাই
                best_answer = self.extract_best_answer(query, search_results)
                
                if best_answer and len(best_answer) > 10:
                    # স্বয়ংক্রিয়ভাবে শিখে নেয়
                    self.auto_learn_from_web(query, best_answer, search_results[0]['url'], user_id)
                    
                    return self._format_response(
                        best_answer,
                        "web_search",
                        sources=[r['url'] for r in search_results[:2]]
                    )
        
        except Exception as e:
            print(f"Web search error: {e}")
        
        return None
    
    def extract_best_answer(self, query, search_results):
        """সার্চ রেজাল্ট থেকে সেরা উত্তর বের করা"""
        if not search_results:
            return None
        
        # সবচেয়ে রিলেভেন্ট কন্টেন্ট
        query_words = set(query.lower().split())
        best_score = 0
        best_content = ""
        
        for result in search_results:
            content = result.get('content', '').lower()
            
            # স্কোরিং
            score = sum(1 for word in query_words if word in content)
            
            # বোনাস: বাংলা কন্টেন্ট
            bangla_chars = sum(1 for char in content if '\u0980' <= char <= '\u09FF')
            if bangla_chars > 50:
                score += 3
            
            if score > best_score:
                best_score = score
                best_content = result.get('content', '')
        
        # কন্টেন্ট পরিষ্কার ও সংক্ষেপণ
        if best_content:
            cleaned = self.clean_content(best_content, query)
            return self.summarize_content(cleaned, query)
        
        return search_results[0].get('content', '')[:300] + "..."
    
    def clean_content(self, content, query):
        """কন্টেন্ট পরিষ্কার"""
        # অপ্রয়োজনীয় অংশ রিমুভ
        unwanted = [
            'সাইন ইন', 'লগইন', 'কুকি', 'প্রাইভেসি', 'কপিরাইট',
            'সম্পর্কিত', 'আরও পড়ুন', 'সূত্র', 'তথ্যসূত্র'
        ]
        
        for word in unwanted:
            content = content.replace(word, '')
        
        # এক্সট্রা স্পেস রিমুভ
        content = ' '.join(content.split())
        
        return content
    
    def summarize_content(self, content, query):
        """কন্টেন্ট সংক্ষেপণ"""
        if len(content) <= 300:
            return content
        
        # প্রশ্নের উত্তর দেয় এমন অংশ খোঁজা
        sentences = content.split('।')
        relevant = []
        
        for sentence in sentences:
            if any(word in sentence.lower() for word in query.lower().split()):
                relevant.append(sentence)
        
        if relevant:
            return '। '.join(relevant[:3]) + '।'
        
        # প্রথম অংশ রিটার্ন
        return content[:300] + "..."
    
    def auto_learn_from_web(self, question, answer, source, user_id):
        """ওয়েব থেকে স্বয়ংক্রিয় শেখা"""
        # সেফটি চেক
        safety_check = self.safety.check_content(question, answer)
        
        if safety_check["safe"] and len(answer) > 20:
            # স্মার্ট লার্নারে সেভ
            self.learner.learn_from_web(question, answer, source)
            
            # মেমরিতেও সেভ
            self.memory.learn_new(question, answer, user_id)
            
            # লগ
            self.log_auto_learning(question, source, user_id)
            
            return True
        
        return False
    
    def auto_learn_manual(self, question, answer, source, user_id):
        """ম্যানুয়ালি অটো লার্ন"""
        return self.auto_learn_from_web(question, answer, source, user_id)
    
    def log_auto_learning(self, question, source, user_id):
        """অটো লার্নিং লগ"""
        log_entry = {
            'question': question[:100],
            'source': source,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'auto_learned'
        }
        
        try:
            with open('data/auto_learn_log.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except:
            pass
    
    def web_search(self, query):
        """সরাসরি ওয়েব সার্চ"""
        if not self.can_search():
            return []
        
        self.last_search_time = time.time()
        self.total_searches += 1
        
        return self.searcher.search_google(query, num_results=3)
    
    def teach_new_thing(self, question, answer, user_id):
        """নতুন জিনিস শেখানো"""
        # সেফটি চেক
        safety_result = self.safety.check_content(question, answer)
        if not safety_result["safe"]:
            return {
                "success": False,
                "message": safety_result["reason"],
                "can_override": safety_result["can_override"]
            }
        
        # ইতিমধ্যে জানা কিনা চেক
        if self.memory.question_exists(question):
            return {
                "success": False,
                "message": "এই প্রশ্নের উত্তর ইতিমধ্যে জানা আছে!",
                "existing_answer": self.memory.get_response(question)
            }
        
        # শেখানো
        success_memory = self.memory.learn_new(question, answer, user_id)
        success_learner = self.learner.learn_from_web(question, answer, "user_taught")
        
        if success_memory or success_learner:
            # ইউজারের ট্রাস্ট স্কোর বাড়ানো
            self.memory.increase_trust_score(user_id)
            
            return {
                "success": True,
                "message": "✅ ধন্যবাদ! আমি শিখে নিলাম।",
                "question": question,
                "answer": answer
            }
        else:
            return {
                "success": False,
                "message": "শেখাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।"
            }
    
    def undo_last_learning(self, user_id):
        """শেষ শেখা জিনিস বাতিল"""
        return self.memory.undo_last_learning(user_id)
    
    def get_user_trust_score(self, user_id):
        """ইউজারের ট্রাস্ট স্কোর"""
        return self.memory.get_user_trust_score(user_id)
    
    def get_statistics(self):
        """সব স্ট্যাটিস্টিক্স"""
        memory_stats = self.memory.get_statistics()
        learner_stats = self.learner.get_knowledge_stats()
        
        return {
            **memory_stats,
            **learner_stats,
            "total_searches": self.total_searches,
            "web_search_enabled": self.enable_web_search,
            "remaining_searches": self.max_searches_per_day - self.total_searches
        }
    
    def _get_smart_response(self, user_input):
        """স্মার্ট রেসপন্স জেনারেট"""
        smart_responses = [
            "দুঃখিত, আমি এই প্রশ্নের উত্তর খুঁজে পাইনি। আপনি কি 'গুগল সার্চ' বাটন টিপে ইন্টারনেট থেকে উত্তর খুঁজে নিতে চান?",
            "আমি এখনও এটি শিখিনি। আপনি আমাকে শেখাতে পারেন অথবা গুগল থেকে সার্চ করতে পারেন।",
            "এই বিষয়ে আমার জ্ঞান নেই। আপনি কি সঠিক উত্তরটি জানেন? তাহলে আমাকে শেখাতে পারেন!",
            "আমি এই প্রশ্নের উত্তর এখনও জানি না। নিচে 'শেখান' বাটনে ক্লিক করে আমাকে শেখাতে পারেন!"
        ]
        
        return random.choice(smart_responses)
    
    def _format_response(self, response_text, response_type, sources=None):
        """রেসপন্স ফরম্যাট"""
        return {
            "response": response_text,
            "type": response_type,
            "timestamp": datetime.now().isoformat(),
            "sources": sources or []
        }

# chatbot/brain.py (সরল)
import random
import time
from datetime import datetime
from .memory import MemoryManager
from .safety import SafetyChecker
from .google_searcher import GoogleSearcher

class BengaliChatbot:
    def __init__(self):
        self.memory = MemoryManager()
        self.safety = SafetyChecker()
        self.searcher = GoogleSearcher()
        
        # বেসিক জ্ঞান
        self.base_knowledge = {
            "হ্যালো": ["হ্যালো! আমি বাংলা চ্যাটবট।", "নমস্কার! কিভাবে সাহায্য করতে পারি?"],
            "তোমার নাম কি": ["আমার নাম বাংলা চ্যাটবট।", "আমাকে বলতে পারেন বট!"],
            "ধন্যবাদ": ["আপনাকেও ধন্যবাদ!", "কিছু মনে করবেন না!"],
        }
    
    def process_message(self, user_input, user_id, web_search=True):
        """মেসেজ প্রসেস"""
        user_input_lower = user_input.lower()
        
        # বেসিক জ্ঞান চেক
        if user_input_lower in self.base_knowledge:
            return self._format_response(
                random.choice(self.base_knowledge[user_input_lower]),
                "base"
            )
        
        # মেমরি চেক
        memory_answer = self.memory.get_response(user_input_lower)
        if memory_answer:
            return self._format_response(memory_answer, "learned")
        
        # গুগল সার্চ
        if web_search:
            web_answer = self.try_web_search(user_input)
            if web_answer:
                # শিখে নেওয়া
                self.memory.learn_new(user_input, web_answer, user_id)
                return self._format_response(web_answer, "web_search")
        
        # ডিফল্ট
        return self._format_response(
            "দুঃখিত, উত্তর জানি না। আপনি আমাকে শেখাতে পারেন!",
            "unknown"
        )
    
    def try_web_search(self, query):
        """গুগল সার্চ চেষ্টা"""
        try:
            results = self.searcher.search_google(query, num_results=1)
            if results and 'content' in results[0]:
                return results[0]['content'][:300] + "..."
        except:
            pass
        return None
    
    def _format_response(self, text, response_type):
        """রেসপন্স ফরম্যাট"""
        return {
            "response": text,
            "type": response_type,
            "timestamp": datetime.now().isoformat()
        }

import re

class SafetyChecker:
    def __init__(self):
        self.banned_words = [
            "মিথ্যা", "গুজব", "অপপ্রচার", "ঘৃণা", "বিদ্বেষ",
            "অশ্লীল", "অভদ্র", "খারাপ", "ভুল", "বানোয়াট",
            "মিথ্যা খবর", "ফেইক", "জালিয়াতি"
        ]
        
        self.sensitive_topics = [
            "রাজনীতি", "ধর্ম", "জাতিগত", "সন্ত্রাস", "হিংসা",
            "বোমা", "আতঙ্ক", "দাঙ্গা"
        ]
        
        self.min_answer_length = 3
        self.max_answer_length = 1000
    
    def check_content(self, question, answer):
        """কন্টেন্ট চেক"""
        # খালি চেক
        if not question.strip() or not answer.strip():
            return {
                "safe": False,
                "reason": "প্রশ্ন বা উত্তর খালি থাকতে পারে না",
                "can_override": False
            }
        
        # দৈর্ঘ্য চেক
        if len(answer.strip()) < self.min_answer_length:
            return {
                "safe": False,
                "reason": f"উত্তর খুব ছোট (কমপক্ষে {self.min_answer_length} অক্ষর)",
                "can_override": False
            }
        
        if len(answer.strip()) > self.max_answer_length:
            return {
                "safe": True,
                "reason": f"উত্তর খুব বড় ({self.max_answer_length} অক্ষরে কাটা হয়েছে)",
                "can_override": True
            }
        
        # নিষিদ্ধ শব্দ
        text_lower = (question + " " + answer).lower()
        
        for word in self.banned_words:
            if word in text_lower:
                return {
                    "safe": False,
                    "reason": f"নিষিদ্ধ শব্দ পাওয়া গেছে: '{word}'",
                    "can_override": False
                }
        
        # সেনসিটিভ টপিক সতর্কতা
        warning_topics = []
        for topic in self.sensitive_topics:
            if topic in text_lower:
                warning_topics.append(topic)
        
        if warning_topics:
            return {
                "safe": True,
                "reason": f"সতর্কতা: {', '.join(warning_topics)} বিষয় সংবলিত",
                "can_override": True,
                "warning": True
            }
        
        # URL/লিংক চেক
        if re.search(r'http[s]?://', answer):
            return {
                "safe": True,
                "reason": "উত্তরে লিংক পাওয়া গেছে",
                "can_override": True,
                "warning": True
            }
        
        # সব ঠিক
        return {
            "safe": True,
            "reason": "সবকিছু ঠিক আছে",
            "can_override": False
        }
    
    def sanitize_text(self, text):
        """টেক্সট পরিষ্কার"""
        # HTML ট্যাগ রিমুভ
        text = re.sub(r'<[^>]+>', '', text)
        
        # এক্সট্রা স্পেস
        text = ' '.join(text.split())
        
        # বিশেষ ক্যারেক্টার লিমিট
        text = re.sub(r'[^\w\u0980-\u09FF\s.,!?-]', '', text)
        
        return text.strip()

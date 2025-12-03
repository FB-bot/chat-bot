import json
import os
import sqlite3
from datetime import datetime
from collections import deque

class MemoryManager:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # ফাইল পাথ
        self.knowledge_file = os.path.join(self.data_dir, "knowledge_base.json")
        self.trust_file = os.path.join(self.data_dir, "user_trust.json")
        self.log_file = os.path.join(self.data_dir, "learning_log.json")
        
        # ডেটা লোড
        self.knowledge_base = self._load_json(self.knowledge_file, {})
        self.user_trust = self._load_json(self.trust_file, {})
        self.learning_log = self._load_json(self.log_file, [])
        
        # আনডো বাফার
        self.undo_buffer = deque(maxlen=15)
    
    def _load_json(self, filepath, default):
        """JSON লোড"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default
    
    def _save_json(self, filepath, data):
        """JSON সেভ"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_response(self, question):
        """উত্তর খোঁজা"""
        return self.knowledge_base.get(question.lower().strip())
    
    def question_exists(self, question):
        """প্রশ্ন আছে কিনা"""
        return question.lower().strip() in self.knowledge_base
    
    def learn_new(self, question, answer, user_id):
        """নতুন শেখা"""
        try:
            question_key = question.lower().strip()
            
            # পুরাতন উত্তর সংরক্ষণ (যদি থাকে)
            old_answer = self.knowledge_base.get(question_key)
            
            self.undo_buffer.append({
                "question": question_key,
                "old_answer": old_answer,
                "new_answer": answer,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # আপডেট
            self.knowledge_base[question_key] = answer
            
            # লগ
            self.learning_log.append({
                "question": question,
                "answer": answer,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "action": "learned"
            })
            
            # সেভ
            self._save_json(self.knowledge_file, self.knowledge_base)
            self._save_json(self.log_file, self.learning_log)
            
            return True
            
        except Exception as e:
            print(f"Learn error: {e}")
            return False
    
    def increase_trust_score(self, user_id, amount=5):
        """ট্রাস্ট বাড়ানো"""
        current = self.user_trust.get(user_id, 50)
        new_score = min(100, current + amount)
        self.user_trust[user_id] = new_score
        self._save_json(self.trust_file, self.user_trust)
        return new_score
    
    def decrease_trust_score(self, user_id, amount=10):
        """ট্রাস্ট কমানো"""
        current = self.user_trust.get(user_id, 50)
        new_score = max(0, current - amount)
        self.user_trust[user_id] = new_score
        self._save_json(self.trust_file, self.user_trust)
        return new_score
    
    def get_user_trust_score(self, user_id):
        """ট্রাস্ট স্কোর"""
        return self.user_trust.get(user_id, 50)
    
    def undo_last_learning(self, user_id):
        """শেষ শেখা বাতিল"""
        try:
            if not self.undo_buffer:
                return {
                    "success": False,
                    "message": "কোন শেখা জিনিস নেই"
                }
            
            last = self.undo_buffer.pop()
            
            if last["old_answer"] is None:
                # নতুন প্রশ্ন ছিল, ডিলিট
                del self.knowledge_base[last["question"]]
            else:
                # পুরাতন উত্তর রিস্টোর
                self.knowledge_base[last["question"]] = last["old_answer"]
            
            # লগ
            self.learning_log.append({
                "question": last["question"],
                "old_answer": last["new_answer"],
                "new_answer": last["old_answer"],
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "action": "undid"
            })
            
            # সেভ
            self._save_json(self.knowledge_file, self.knowledge_base)
            self._save_json(self.log_file, self.learning_log)
            
            # ট্রাস্ট কমানো
            self.decrease_trust_score(user_id, 5)
            
            return {
                "success": True,
                "message": "✅ শেষ শেখা জিনিস বাতিল করা হয়েছে",
                "question": last["question"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"ত্রুটি: {str(e)}"
            }
    
    def get_statistics(self):
        """পরিসংখ্যান"""
        return {
            "total_learned": len(self.knowledge_base),
            "today_learned": self._count_today_learned(),
            "total_logs": len(self.learning_log),
            "total_users": len(self.user_trust),
            "undo_available": len(self.undo_buffer)
        }
    
    def _count_today_learned(self):
        """আজকের শেখা গণনা"""
        today = datetime.now().date().isoformat()
        count = 0
        
        for log in self.learning_log:
            if log.get("timestamp", "").startswith(today) and log.get("action") == "learned":
                count += 1
        
        return count

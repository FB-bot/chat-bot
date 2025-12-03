import json
import sqlite3
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

class SmartLearner:
    def __init__(self):
        # মডেল লোড
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except:
            # ফallback মডেল
            self.model = None
        
        # ডেটাবেজ
        self.db_path = "data/smart_knowledge.db"
        self.init_database()
        
        # ক্যাশে
        self.cache = {}
    
    def init_database(self):
        """স্মার্ট ডেটাবেজ তৈরি"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT,
                question_vec BLOB,
                answer_vec BLOB,
                source TEXT,
                confidence REAL DEFAULT 0.8,
                use_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_question ON knowledge(question)
        ''')
        
        conn.commit()
        conn.close()
    
    def vectorize(self, text):
        """টেক্সট ভেক্টরাইজ"""
        if self.model and text:
            vector = self.model.encode(text)
            return vector.tobytes()
        return None
    
    def learn_from_web(self, question, answer, source):
        """ওয়েব থেকে শেখা"""
        try:
            # ভেক্টর তৈরি
            q_vec = self.vectorize(question)
            a_vec = self.vectorize(answer)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # চেক করা প্রশ্ন আছে কিনা
            cursor.execute('SELECT id FROM knowledge WHERE question = ?', (question,))
            existing = cursor.fetchone()
            
            if existing:
                # আপডেট
                cursor.execute('''
                    UPDATE knowledge 
                    SET answer = ?, answer_vec = ?, source = ?, last_used = ?
                    WHERE id = ?
                ''', (answer, a_vec, source, datetime.now(), existing[0]))
            else:
                # নতুন
                cursor.execute('''
                    INSERT INTO knowledge 
                    (question, answer, question_vec, answer_vec, source, last_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (question, answer, q_vec, a_vec, source, datetime.now()))
            
            conn.commit()
            conn.close()
            
            # ক্যাশে আপডেট
            self.cache[question] = answer
            
            return True
            
        except Exception as e:
            print(f"Smart learn error: {e}")
            return False
    
    def get_auto_answer(self, question):
        """স্বয়ংক্রিয় উত্তর"""
        # ক্যাশে চেক
        if question in self.cache:
            return self.cache[question]
        
        # সিমিলার প্রশ্ন খোঁজা
        similar = self.find_similar_question(question)
        if similar:
            return similar['answer']
        
        return None
    
    def find_similar_question(self, question, threshold=0.7):
        """মিল আছে এমন প্রশ্ন খোঁজা"""
        if not self.model:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, question, question_vec FROM knowledge')
            rows = cursor.fetchall()
            
            if not rows:
                conn.close()
                return None
            
            # প্রশ্নের ভেক্টর
            q_vector = self.model.encode(question)
            
            best_match = None
            best_score = 0
            
            for row in rows:
                row_id, row_question, row_vec_bytes = row
                
                if row_vec_bytes:
                    row_vector = np.frombuffer(row_vec_bytes, dtype=np.float32)
                    similarity = util.pytorch_cos_sim(q_vector, row_vector).item()
                    
                    if similarity > best_score and similarity > threshold:
                        best_score = similarity
                        best_match = row_id
            
            conn.close()
            
            if best_match:
                return self.get_by_id(best_match)
            
        except Exception as e:
            print(f"Similarity search error: {e}")
        
        return None
    
    def get_by_id(self, knowledge_id):
        """ID দিয়ে জ্ঞান নিন"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT question, answer, confidence FROM knowledge WHERE id = ?',
            (knowledge_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'question': row[0],
                'answer': row[1],
                'confidence': row[2]
            }
        
        return None
    
    def get_knowledge_stats(self):
        """পরিসংখ্যান"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(use_count) FROM knowledge')
        total_uses = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(DISTINCT source) FROM knowledge')
        unique_sources = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'smart_knowledge': total,
            'smart_uses': total_uses,
            'unique_sources': unique_sources,
            'cache_size': len(self.cache)
        }

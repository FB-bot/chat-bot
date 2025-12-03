from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bangla-chatbot-secret-2024')

# সরল চ্যাটবট ক্লাস
class SimpleChatbot:
    def __init__(self):
        self.knowledge = {
            "হ্যালো": "হ্যালো! আমি বাংলা চ্যাটবট। 😊",
            "তোমার নাম কি": "আমার নাম বট!",
            "ধন্যবাদ": "আপনাকেও ধন্যবাদ! 🙏",
            "কেমন আছ": "ভালো আছি, আপনিই বলুন!",
            "বিদায়": "বিদায়! আবার কথা হবে।",
            "তুমি কি করতে পার": "আমি বাংলায় কথা বলতে পারি এবং কিছু প্রশ্নের উত্তর দিতে পারি।"
        }
    
    def get_response(self, question):
        question = question.lower().strip()
        if question in self.knowledge:
            return self.knowledge[question]
        
        # কিছু সাধারণ প্যাটার্ন
        if "নাম" in question:
            return "আমার নাম বাংলা চ্যাটবট।"
        elif "কী" in question or "কি" in question:
            return "দুঃখিত, এই প্রশ্নের উত্তর এখনও জানি না।"
        else:
            return "আমি এখনও শিখছি! আপনি আমাকে শেখাতে পারেন।"

chatbot = SimpleChatbot()

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().timestamp()}"
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'খালি মেসেজ'}), 400
        
        # চ্যাটবট থেকে উত্তর
        response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': response,
            'success': True
        })
        
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
        
        # নতুন শেখানো
        chatbot.knowledge[question.lower()] = answer
        
        return jsonify({
            'success': True,
            'message': '✅ শিখে নিলাম!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

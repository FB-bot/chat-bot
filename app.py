from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
from chatbot.brain import BengaliChatbot

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bangla-ai-chatbot-secret-2024')

# চ্যাটবট ইনিশিয়ালাইজ
chatbot = BengaliChatbot()

@app.route('/')
def home():
    """হোমপেজ"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().timestamp()}"
        session['trust_score'] = 50
        session['search_count'] = 0
    
    return render_template('index.html', 
                         user_id=session['user_id'],
                         trust_score=session['trust_score'],
                         search_count=session.get('search_count', 0))

@app.route('/api/chat', methods=['POST'])
def chat():
    """চ্যাট এন্ডপয়েন্ট"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        user_id = session.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'error': 'খালি মেসেজ'}), 400
        
        # সার্চ কাউন্ট চেক
        if session.get('search_count', 0) >= 50:  # দৈনিক লিমিট
            web_search = False
        else:
            web_search = data.get('web_search', True)
            if web_search:
                session['search_count'] = session.get('search_count', 0) + 1
        
        # চ্যাটবট থেকে রেসপন্স পান
        response_data = chatbot.process_message(user_message, user_id, web_search=web_search)
        
        # ট্রাস্ট স্কোর আপডেট
        session['trust_score'] = chatbot.get_user_trust_score(user_id)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learn', methods=['POST'])
def learn():
    """নতুন জিনিস শেখার এন্ডপয়েন্ট"""
    try:
        data = request.json
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        user_id = session.get('user_id', 'anonymous')
        
        if not question or not answer:
            return jsonify({'error': 'প্রশ্ন এবং উত্তর দিতে হবে'}), 400
        
        # নতুন জিনিস শেখানোর চেষ্টা
        result = chatbot.teach_new_thing(question, answer, user_id)
        
        if result['success']:
            session['trust_score'] = chatbot.get_user_trust_score(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/undo', methods=['POST'])
def undo_learning():
    """শেষ শেখা জিনিস বাতিল"""
    try:
        user_id = session.get('user_id', 'anonymous')
        result = chatbot.undo_last_learning(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/web_search', methods=['POST'])
def web_search_endpoint():
    """সরাসরি গুগল সার্চ"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        user_id = session.get('user_id', 'anonymous')
        
        if not query:
            return jsonify({'error': 'খালি কোয়েরি'}), 400
        
        # সার্চ কাউন্ট চেক
        if session.get('search_count', 0) >= 50:
            return jsonify({'error': 'দৈনিক সার্চ লিমিট শেষ'}), 429
        
        session['search_count'] = session.get('search_count', 0) + 1
        
        # গুগল সার্চ
        results = chatbot.web_search(query)
        
        if results:
            # স্বয়ংক্রিয় শেখা
            chatbot.auto_learn_from_web(query, results[0], user_id)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'search_count': session['search_count']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/stats', methods=['GET'])
def knowledge_stats():
    """স্মার্ট নলেজ স্ট্যাটস"""
    stats = chatbot.get_statistics()
    return jsonify(stats)

@app.route('/api/search_stats', methods=['GET'])
def search_stats():
    """সার্চ স্ট্যাটিস্টিক্স"""
    return jsonify({
        'search_count': session.get('search_count', 0),
        'remaining': 50 - session.get('search_count', 0)
    })

@app.route('/api/auto_learn', methods=['POST'])
def auto_learn():
    """স্বয়ংক্রিয় শেখা"""
    try:
        data = request.json
        question = data.get('question', '')
        answer = data.get('answer', '')
        source = data.get('source', 'manual')
        user_id = session.get('user_id', 'anonymous')
        
        if question and answer:
            success = chatbot.auto_learn_manual(question, answer, source, user_id)
            return jsonify({
                'success': success,
                'message': 'স্বয়ংক্রিয়ভাবে শিখে নেওয়া হয়েছে' if success else 'ব্যর্থ'
            })
        
        return jsonify({'error': 'প্রশ্ন এবং উত্তর প্রয়োজন'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """সেশন রিসেট"""
    session.clear()
    return jsonify({'success': True, 'message': 'সেশন রিসেট করা হয়েছে'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

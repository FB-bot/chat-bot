class AdvancedChatbotUI {
    constructor() {
        // এলিমেন্টস
        this.chatBox = document.getElementById('chatBox');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.learnBtn = document.getElementById('learnBtn');
        this.webSearchBtn = document.getElementById('webSearchBtn');
        this.undoBtn = document.getElementById('undoBtn');
        this.statsBtn = document.getElementById('statsBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.learningMode = document.getElementById('learningMode');
        this.teachBtn = document.getElementById('teachBtn');
        this.sourcesModal = document.getElementById('sourcesModal');
        
        // স্টেট
        this.isLearningMode = false;
        this.trustScore = 50;
        this.searchCount = 0;
        this.activeTab = 'chat';
        
        this.init();
    }
    
    init() {
        // ইভেন্ট লিসেনার
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        this.learnBtn.addEventListener('click', () => this.toggleLearningMode());
        this.webSearchBtn.addEventListener('click', () => this.webSearchCurrent());
        this.undoBtn.addEventListener('click', () => this.undoLearning());
        this.statsBtn.addEventListener('click', () => this.showStats());
        this.resetBtn.addEventListener('click', () => this.resetSession());
        this.teachBtn.addEventListener('click', () => this.teachBot());
        
        // ট্যাব
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // মোডাল
        document.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
        this.sourcesModal.addEventListener('click', (e) => {
            if (e.target === this.sourcesModal) this.closeModal();
        });
        
        // ওয়েলকাম মেসেজ
        this.addWelcomeMessage();
        this.updateStats();
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        this.addMessage('আপনি', message, 'user');
        this.userInput.value = '';
        
        const loadingId = this.showLoading();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message,
                    web_search: this.shouldWebSearch()
                })
            });
            
            const data = await response.json();
            this.hideLoading(loadingId);
            
            if (data.error) {
                this.addMessage('বট', `ত্রুটি: ${data.error}`, 'error');
            } else {
                this.addMessage('বট', data.response, data.type, data.sources);
                this.updateStats();
            }
            
        } catch (error) {
            this.hideLoading(loadingId);
            this.addMessage('বট', 'নেটওয়ার্ক ত্রুটি! আবার চেষ্টা করুন।', 'error');
            console.error('Error:', error);
        }
    }
    
    async webSearchCurrent() {
        const message = this.userInput.value.trim();
        if (!message) {
            alert('প্রথমে কিছু লিখুন!');
            return;
        }
        
        this.addMessage('আপনি', `[গুগল সার্চ] ${message}`, 'user');
        
        const loadingId = this.showLoading();
        
        try {
            const response = await fetch('/api/web_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });
            
            const data = await response.json();
            this.hideLoading(loadingId);
            
            if (data.error) {
                this.addMessage('বট', `সার্চ ত্রুটি: ${data.error}`, 'error');
            } else if (data.results && data.results.length > 0) {
                const firstResult = data.results[0];
                this.addMessage('বট', firstResult.content || 'কোন তথ্য পাওয়া যায়নি', 'web_search', data.results);
                this.updateStats();
            } else {
                this.addMessage('বট', 'কোন ফলাফল পাওয়া যায়নি', 'web_search');
            }
            
        } catch (error) {
            this.hideLoading(loadingId);
            this.addMessage('বট', 'সার্চ ত্রুটি!', 'error');
            console.error('Search error:', error);
        }
    }
    
    async directWebSearch(query) {
        try {
            const response = await fetch('/api/web_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                return data.results[0].content;
            }
            
            return null;
            
        } catch (error) {
            console.error('Direct search error:', error);
            return null;
        }
    }
    
    toggleLearningMode() {
        this.isLearningMode = !this.isLearningMode;
        this.learningMode.classList.toggle('active');
        this.learnBtn.innerHTML = this.isLearningMode ? 
            '<i class="fas fa-comment"></i> চ্যাট' : 
            '<i class="fas fa-graduation-cap"></i> শেখান';
    }
    
    async teachBot() {
        const question = document.getElementById('teachQuestion').value.trim();
        const answer = document.getElementById('teachAnswer').value.trim();
        
        if (!question || !answer) {
            alert('প্রশ্ন এবং উত্তর উভয়ই দিতে হবে!');
            return;
        }
        
        try {
            const response = await fetch('/api/learn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, answer })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                document.getElementById('teachQuestion').value = '';
                document.getElementById('teachAnswer').value = '';
                this.toggleLearningMode();
                this.updateStats();
                this.addMessage('বট', `নতুন শিখলাম: ${question} → ${answer}`, 'learned');
            } else {
                if (data.existing_answer) {
                    const confirmOverride = confirm(
                        `এই প্রশ্নের উত্তর ইতিমধ্যে আছে:\n"${data.existing_answer}"\n\nআপনার উত্তর:\n"${answer}"\n\nআপনার উত্তরটি রাখতে চান?`
                    );
                    
                    if (confirmOverride) {
                        const override = await fetch('/api/learn', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                question, 
                                answer,
                                override: true 
                            })
                        });
                        
                        const overrideData = await override.json();
                        alert(overrideData.message || 'আপডেট করা হয়েছে!');
                        this.toggleLearningMode();
                    }
                } else {
                    alert(data.message);
                }
            }
            
        } catch (error) {
            alert('শেখাতে সমস্যা হয়েছে!');
            console.error('Error:', error);
        }
    }
    
    async undoLearning() {
        if (!confirm('শেষ শেখা জিনিসটি বাতিল করতে চান?')) return;
        
        try {
            const response = await fetch('/api/undo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            alert(data.message);
            this.updateStats();
            
            if (data.success) {
                this.addMessage('সিস্টেম', data.message, 'system');
            }
            
        } catch (error) {
            alert('বাতিল করতে সমস্যা হয়েছে!');
            console.error('Error:', error);
        }
    }
    
    async showStats() {
        try {
            const [statsRes, searchRes] = await Promise.all([
                fetch('/api/knowledge/stats'),
                fetch('/api/search_stats')
            ]);
            
            const stats = await statsRes.json();
            const searchStats = await searchRes.json();
            
            const statsText = `
📊 বটের পরিসংখ্যান:

🧠 জ্ঞান ভাণ্ডার:
• মোট শেখা: ${stats.total_learned || 0}
• স্মার্ট জ্ঞান: ${stats.smart_knowledge || 0}
• আজ শেখা: ${stats.today_learned || 0}
• মোট ইউজার: ${stats.total_users || 0}

🔍 সার্চ তথ্য:
• আজকের সার্চ: ${searchStats.search_count || 0}
• বাকি সার্চ: ${searchStats.remaining || 0}
• আনডো সম্ভব: ${stats.undo_available || 0}

📈 ব্যবহার:
• মোট ব্যবহার: ${stats.total_logs || 0}
• ট্রাস্ট স্কোর: ${this.trustScore}%
• ক্যাশে সাইজ: ${stats.cache_size || 0}
            `;
            
            alert(statsText);
            
        } catch (error) {
            alert('পরিসংখ্যান লোড করতে সমস্যা!');
            console.error('Error:', error);
        }
    }
    
    async resetSession() {
        if (!confirm('সেশন রিসেট করবেন? এটি আপনার ট্রাস্ট স্কোর রিসেট করবে।')) return;
        
        try {
            const response = await fetch('/api/reset_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload();
            }
            
        } catch (error) {
            alert('রিসেট করতে সমস্যা!');
            console.error('Error:', error);
        }
    }
    
    async updateStats() {
        try {
            const response = await fetch('/api/search_stats');
            const data = await response.json();
            
            this.searchCount = data.search_count || 0;
            
            // UI আপডেট
            document.querySelectorAll('.trust-value').forEach(el => {
                el.textContent = `${this.trustScore}%`;
            });
            
            document.querySelectorAll('.search-value').forEach(el => {
                el.textContent = `${this.searchCount}/50`;
            });
            
        } catch (error) {
            console.error('Stats update error:', error);
        }
    }
    
    addWelcomeMessage() {
        const welcome = `
🤖 বাংলা AI চ্যাটবটে স্বাগতম!

আমি যা করতে পারি:
✅ বাংলায় প্রাকৃতিক কথোপকথন
🔍 গুগল থেকে তথ্য নিয়ে আসা
🧠 নতুন জিনিস শেখা ও মনে রাখা
🛡️ নিরাপদ কন্টেন্ট ফিল্টারিং
📊 সময়ের সাথে উন্নতি করা

আপনার যে কোনো প্রশ্ন করুন, আমি উত্তর দেওয়ার চেষ্টা করব!
        `;
        
        this.addMessage('বট', welcome, 'welcome');
    }
    
    addMessage(sender, message, type, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'আপনি' ? 'user-message' : 'bot-message'}`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('bn-BD', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // টাইপ ম্যাপিং
        const typeMap = {
            'base_knowledge': 'বেসিক',
            'learned': 'শেখা',
            'learned_smart': 'স্মার্ট',
            'web_search': 'গুগল',
            'ai_generated': 'AI',
            'error': 'ত্রুটি',
            'welcome': 'স্বাগতম',
            'system': 'সিস্টেম'
        };
        
        const typeText = typeMap[type] || type;
        const typeClass = `type-${type}`;
        
        // সোর্স বাটন
        let sourcesBtn = '';
        if (sources && sources.length > 0) {
            sourcesBtn = `<span class="message-sources" onclick="chatbot.showSources(${JSON.stringify(sources).replace(/"/g, '&quot;')})">
                <i class="fas fa-link"></i> ${sources.length} সোর্স
            </span>`;
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender">${sender}</span>
                <span class="message-type ${typeClass}">${typeText}</span>
            </div>
            <div class="message-text">${this.escapeHtml(message)}</div>
            <div class="message-footer">
                <span class="message-time">${timeString}</span>
                ${sourcesBtn}
            </div>
        `;
        
        this.chatBox.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showSources(sources) {
        const modalContent = this.sourcesModal.querySelector('.modal-content');
        let sourcesHtml = '<h3><i class="fas fa-external-link-alt"></i> তথ্যসূত্র</h3>';
        
        sources.forEach((source, index) => {
            sourcesHtml += `
                <div class="source-item">
                    <strong>সূত্র ${index + 1}:</strong><br>
                    ${source.url ? `<a href="${source.url}" target="_blank">${source.title || source.url}</a>` : 'Unknown source'}<br>
                    <small>${source.content ? source.content.substring(0, 150) + '...' : 'No content'}</small>
                </div>
            `;
        });
        
        modalContent.innerHTML = `
            <div class="modal-header">
                <h3><i class="fas fa-external-link-alt"></i> তথ্যসূত্র</h3>
                <button class="close-modal">&times;</button>
            </div>
            ${sourcesHtml}
        `;
        
        this.sourcesModal.style.display = 'flex';
        this.sourcesModal.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
    }
    
    closeModal() {
        this.sourcesModal.style.display = 'none';
    }
    
    switchTab(tabName) {
        this.activeTab = tabName;
        
        // ট্যাব আপডেট
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // কন্টেন্ট আপডেট
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
        
        if (tabName === 'search') {
            this.loadSearchTab();
        }
    }
    
    async loadSearchTab() {
        // সার্চ ট্যাব কন্টেন্ট লোড
        const searchTab = document.getElementById('search-tab');
        searchTab.innerHTML = `
            <h3><i class="fas fa-search"></i> সরাসরি গুগল সার্চ</h3>
            <div class="search-input">
                <input type="text" id="directSearchInput" placeholder="গুগলে কী সার্চ করবেন...">
                <button onclick="chatbot.directSearch()" class="btn btn-primary">
                    <i class="fas fa-search"></i> সার্চ
                </button>
            </div>
            <div id="searchResults"></div>
        `;
    }
    
    async directSearch() {
        const query = document.getElementById('directSearchInput').value.trim();
        if (!query) return;
        
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '<div class="loading"></div> সার্চ করা হচ্ছে...';
        
        try {
            const response = await fetch('/api/web_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (data.error) {
                resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
            } else if (data.results && data.results.length > 0) {
                let resultsHtml = `<h4>${data.results.length}টি ফলাফল পাওয়া গেছে:</h4>`;
                
                data.results.forEach((result, index) => {
                    resultsHtml += `
                        <div class="search-result">
                            <h5><a href="${result.url}" target="_blank">${result.title || 'No title'}</a></h5>
                            <p>${result.content ? result.content.substring(0, 200) + '...' : 'No content'}</p>
                            <button onclick="chatbot.autoLearnFromSearch('${this.escapeString(query)}', '${this.escapeString(result.content)}', '${this.escapeString(result.url)}')" class="btn btn-small">
                                <i class="fas fa-save"></i> শেখান
                            </button>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = resultsHtml;
                this.updateStats();
            } else {
                resultsDiv.innerHTML = '<div class="no-results">কোন ফলাফল পাওয়া যায়নি</div>';
            }
            
        } catch (error) {
            resultsDiv.innerHTML = '<div class="error">সার্চ ত্রুটি</div>';
            console.error('Direct search error:', error);
        }
    }
    
    async autoLearnFromSearch(question, answer, source) {
        try {
            const response = await fetch('/api/auto_learn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    answer: answer.substring(0, 500),
                    source: source
                })
            });
            
            const data = await response.json();
            alert(data.message);
            
        } catch (error) {
            alert('শেখাতে সমস্যা!');
            console.error('Auto learn error:', error);
        }
    }
    
    shouldWebSearch() {
        // যেসব প্রশ্নে ওয়েব সার্চ করা উচিত
        const searchPatterns = [
            'কী', 'কি', 'কেন', 'কিভাবে', 'কখন', 'কোথায়',
            'কত', 'কে', 'কাদের', 'কিসের', 'কোন'
        ];
        
        const currentMessage = this.userInput.value.toLowerCase();
        return searchPatterns.some(pattern => currentMessage.includes(pattern));
    }
    
    showLoading() {
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'message bot-message';
        loadingDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender">বট</span>
                <span class="message-type">চিন্তা করছি...</span>
            </div>
            <div class="message-text">
                <div class="loading"></div> উত্তর খুঁজছি...
            </div>
        `;
        
        this.chatBox.appendChild(loadingDiv);
        this.scrollToBottom();
        return loadingId;
    }
    
    hideLoading(loadingId) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }
    
    scrollToBottom() {
        this.chatBox.scrollTop = this.chatBox.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    escapeString(str) {
        return str ? str.replace(/'/g, "\\'").replace(/"/g, '\\"') : '';
    }
}

// চ্যাটবট শুরু
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new AdvancedChatbotUI();
});

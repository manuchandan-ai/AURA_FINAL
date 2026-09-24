/**
 * AURA — Adaptive Unified Reasoning Assistant
 * Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Flash Message Auto-dismiss
    const flashMessages = document.querySelectorAll('.aura-flash');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(msg);
                bsAlert.close();
            }
        }, 5000);
    });

    const chatForm = document.getElementById('aura-form');
    const chatInput = document.getElementById('analyze_text');
    const resultsArea = document.getElementById('analysis-results');
    const conversationIdInput = document.getElementById('conversation_id');
    const goalsContainer = document.getElementById('your-goals');
    const remindersContainer = document.getElementById('your-reminders');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Fetch initial dashboard data
    fetchDashboardData();

    // Auto-resize textarea
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (typeof chatForm.requestSubmit === 'function') {
                    chatForm.requestSubmit();
                } else {
                    chatForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            }
        });
    }

    // Chat Submission
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const textContent = chatInput.value.trim();
            if (!textContent) return;
            
            // Append User message
            const userBubble = `
                <div class="d-flex justify-content-end w-100 mb-3">
                    <div class="aura-chat-bubble user p-3 text-white" style="background: rgba(255,255,255,0.1); border-radius: 16px 16px 0 16px;">
                        ${textContent.replace(/\n/g, '<br>')}
                    </div>
                </div>
            `;
            if (resultsArea) {
                resultsArea.insertAdjacentHTML('beforeend', userBubble);
                resultsArea.scrollTop = resultsArea.scrollHeight;
            }
            
            chatInput.value = '';
            chatInput.style.height = 'auto';
            if(analyzeBtn) analyzeBtn.disabled = true;
            
            // Append Loading Bubble
            const loadingId = 'loading-' + Date.now();
            const loadingBubble = `
                <div id="${loadingId}" class="d-flex align-items-start gap-3 w-100 mb-3">
                    <div class="rounded-circle d-flex justify-content-center align-items-center shadow-lg" style="width: 40px; height: 40px; background: rgba(139, 92, 246, 0.2); border: 1px solid #8b5cf6;">
                        <i class="bi bi-cpu text-white fs-5"></i>
                    </div>
                    <div class="aura-chat-bubble aura p-3 d-flex align-items-center gap-3" style="background: rgba(6, 182, 212, 0.1); border-radius: 16px 16px 16px 0; border: 1px solid rgba(6,182,212,0.3);">
                        <div class="spinner-grow spinner-grow-sm text-info" role="status"></div>
                        <span class="text-secondary small">AURA is thinking...</span>
                    </div>
                </div>
            `;
            if (resultsArea) {
                resultsArea.insertAdjacentHTML('beforeend', loadingBubble);
                resultsArea.scrollTop = resultsArea.scrollHeight;
            }

            try {
                const formData = new FormData();
                formData.append('text', textContent);
                if(conversationIdInput) {
                    formData.append('conversation_id', conversationIdInput.value);
                }

                // Add 120 second timeout for local Ollama
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 120000);

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    if (conversationIdInput) {
                        conversationIdInput.value = data.conversation_id;
                    }
                    
                    const responseBubble = `
                        <div class="d-flex align-items-start gap-3 w-100 mb-3">
                            <div class="rounded-circle d-flex justify-content-center align-items-center shadow-lg" style="width: 40px; height: 40px; background: rgba(139, 92, 246, 0.2); border: 1px solid #8b5cf6;">
                                <i class="bi bi-cpu text-white fs-5"></i>
                            </div>
                            <div class="aura-chat-bubble aura p-3 flex-grow-1" style="background: rgba(6, 182, 212, 0.1); border-radius: 16px 16px 16px 0; border: 1px solid rgba(6,182,212,0.3);">
                                <div class="d-flex align-items-center gap-2 mb-2">
                                    <span class="badge bg-primary bg-opacity-25 text-primary border border-primary border-opacity-25">${data.module}</span>
                                    <span class="badge bg-secondary bg-opacity-25 text-secondary border border-secondary border-opacity-25">${data.decision}</span>
                                </div>
                                <div class="text-white small" style="line-height: 1.6;">
                                    ${parseMarkdown(data.explanation)}
                                </div>
                            </div>
                        </div>
                    `;
                    document.getElementById(loadingId).outerHTML = responseBubble;
                    
                    // Refresh dashboard data silently in case a goal was added
                    fetchDashboardData();
                } else {
                    document.getElementById(loadingId).outerHTML = `<div class="text-danger small p-2">Error: ${data.message}</div>`;
                }
            } catch (err) {
                console.error(err);
                const el = document.getElementById(loadingId);
                if (el) {
                    if (err.name === 'AbortError') {
                        el.outerHTML = `<div class="text-danger small p-2">Network Timeout: AURA took too long to respond. Please check your internet connection and try again.</div>`;
                    } else {
                        el.outerHTML = `<div class="text-danger small p-2">Network Error. Check console.</div>`;
                    }
                }
            } finally {
                if(analyzeBtn) analyzeBtn.disabled = false;
                if(resultsArea) resultsArea.scrollTop = resultsArea.scrollHeight;
            }
        });
    }

    async function fetchDashboardData() {
        if (!goalsContainer && !remindersContainer) return;
        
        try {
            const [goalsRes, remRes] = await Promise.all([
                fetch('/api/goals'),
                fetch('/api/reminders')
            ]);
            
            const goalsData = await goalsRes.json();
            const remData = await remRes.json();
            
            if (goalsContainer && goalsData.status === 'success') {
                if (goalsData.goals.length === 0) {
                    goalsContainer.innerHTML = `<div class="text-center text-secondary small py-3">No active goals. Ask AURA to set one up!</div>`;
                } else {
                    goalsContainer.innerHTML = goalsData.goals.slice(0, 3).map(g => `
                        <div>
                            <div class="d-flex justify-content-between mb-1">
                                <span class="text-white small fw-semibold">${g.title}</span>
                                <span class="text-secondary small">${g.progress}%</span>
                            </div>
                            <div class="progress bg-secondary bg-opacity-25" style="height: 6px;">
                                <div class="progress-bar bg-info" style="width: ${g.progress}%"></div>
                            </div>
                        </div>
                    `).join('');
                }
            }
            
            if (remindersContainer && remData.status === 'success') {
                if (remData.reminders.length === 0) {
                    remindersContainer.innerHTML = `<div class="text-center text-secondary small py-2">No pending reminders.</div>`;
                } else {
                    remindersContainer.innerHTML = remData.reminders.slice(0, 3).map(r => `
                        <div class="d-flex align-items-center gap-2 p-2 rounded bg-secondary bg-opacity-10 border border-secondary border-opacity-10">
                            <i class="bi bi-circle text-secondary"></i>
                            <div class="d-flex flex-column">
                                <span class="text-white small lh-1">${r.task}</span>
                                <span class="text-secondary" style="font-size: 0.7rem;">${r.due_date || 'No due date'}</span>
                            </div>
                            <span class="badge bg-${r.priority === 'high' ? 'danger' : 'secondary'} ms-auto" style="font-size: 0.6rem;">${r.priority}</span>
                        </div>
                    `).join('');
                }
            }
        } catch (e) {
            console.error('Failed to fetch dashboard data', e);
        }
    }

    function parseMarkdown(text) {
        if (!text) return '';
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        return html;
    }
});

// Expose quickAction to global scope for onclick handlers
window.quickAction = function(text) {
    const chatInput = document.getElementById('analyze_text');
    const chatForm = document.getElementById('aura-form');
    if (chatInput && chatForm) {
        chatInput.value = text;
        chatInput.focus();
    }
};

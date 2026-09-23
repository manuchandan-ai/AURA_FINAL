/**
 * AURA — Adaptive Unified Reasoning Assistant
 * Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {

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
                chatForm.dispatchEvent(new Event('submit'));
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
            resultsArea.insertAdjacentHTML('beforeend', userBubble);
            resultsArea.scrollTop = resultsArea.scrollHeight;
            
            chatInput.value = '';
            chatInput.style.height = 'auto';
            analyzeBtn.disabled = true;
            
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
            resultsArea.insertAdjacentHTML('beforeend', loadingBubble);
            resultsArea.scrollTop = resultsArea.scrollHeight;

            try {
                const formData = new FormData();
                formData.append('text', textContent);
                formData.append('conversation_id', conversationIdInput.value);

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    conversationIdInput.value = data.conversation_id;
                    
                    const responseBubble = `
                        <div class="d-flex align-items-start gap-3 w-100 mb-3">
                            <div class="rounded-circle d-flex justify-content-center align-items-center shadow-lg" style="width: 40px; height: 40px; background: rgba(139, 92, 246, 0.2); border: 1px solid #8b5cf6;">
                                <i class="bi bi-cpu text-white fs-5"></i>
                            </div>
                            <div class="aura-chat-bubble aura p-3" style="background: rgba(6, 182, 212, 0.1); border-radius: 16px 16px 16px 0; border: 1px solid rgba(6,182,212,0.3);">
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
                document.getElementById(loadingId).outerHTML = `<div class="text-danger small p-2">Network Error</div>`;
            } finally {
                analyzeBtn.disabled = false;
                resultsArea.scrollTop = resultsArea.scrollHeight;
            }
        });
    }

    async function fetchDashboardData() {
        if (!goalsContainer) return;
        
        try {
            const [goalsRes, remRes] = await Promise.all([
                fetch('/api/goals'),
                fetch('/api/reminders')
            ]);
            
            const goalsData = await goalsRes.json();
            const remData = await remRes.json();
            
            if (goalsData.status === 'success') {
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
            
            if (remData.status === 'success') {
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
        // Simple markdown parser for bold and lists
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        return html;
    }

});
    
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ==========================================
    // 1. Particle System
    // ==========================================
    class AuraParticles {
        constructor(canvasId) {
            this.canvas = document.getElementById(canvasId);
            if (!this.canvas) return;
            
            this.ctx = this.canvas.getContext('2d');
            this.particles = [];
            
            // Adjust count based on motion preference
            this.particleCount = prefersReducedMotion ? 20 : 60;
            this.colors = ['#ffffff', '#00d4ff', '#7b2ff7'];
            
            this.init();
            
            window.addEventListener('resize', () => {
                this.resize();
            });
        }
        
        init() {
            this.resize();
            this.createParticles();
            this.animate();
        }
        
        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        
        createParticles() {
            this.particles = [];
            for (let i = 0; i < this.particleCount; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    radius: Math.random() * 2 + 0.5,
                    vx: (Math.random() - 0.5) * (prefersReducedMotion ? 0.1 : 0.5),
                    vy: (Math.random() - 0.5) * (prefersReducedMotion ? 0.1 : 0.5),
                    color: this.colors[Math.floor(Math.random() * this.colors.length)],
                    opacity: Math.random() * 0.3 + 0.1
                });
            }
        }
        
        draw() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Draw particles
            this.particles.forEach(p => {
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fillStyle = p.color;
                this.ctx.globalAlpha = p.opacity;
                this.ctx.fill();
            });
            
            // Draw connections if not reduced motion
            if (!prefersReducedMotion) {
                for (let i = 0; i < this.particles.length; i++) {
                    for (let j = i + 1; j < this.particles.length; j++) {
                        const p1 = this.particles[i];
                        const p2 = this.particles[j];
                        const dx = p1.x - p2.x;
                        const dy = p1.y - p2.y;
                        const dist = Math.sqrt(dx*dx + dy*dy);
                        
                        if (dist < 120) {
                            this.ctx.beginPath();
                            this.ctx.moveTo(p1.x, p1.y);
                            this.ctx.lineTo(p2.x, p2.y);
                            this.ctx.strokeStyle = '#ffffff';
                            this.ctx.globalAlpha = 0.1 * (1 - dist/120);
                            this.ctx.stroke();
                        }
                    }
                }
            }
            this.ctx.globalAlpha = 1;
        }
        
        update() {
            this.particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                
                // Bounce off edges
                if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            });
        }
        
        animate = () => {
            this.update();
            this.draw();
            requestAnimationFrame(this.animate);
        }
    }
    
    new AuraParticles('aura-particles');

    // ==========================================
    // 2. Navbar Scroll Effect
    // ==========================================
    const navbar = document.querySelector('.aura-navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ==========================================
    // 3. Intersection Observer (Fade-in)
    // ==========================================
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
        const fadeElements = document.querySelectorAll('.aura-fade-in');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Special case for pipeline stages
                    if (entry.target.classList.contains('aura-pipeline')) {
                        animatePipeline(entry.target);
                    }
                }
            });
        }, { threshold: 0.1 });
        
        fadeElements.forEach(el => observer.observe(el));
    } else {
        // Fallback for reduced motion or old browsers
        document.querySelectorAll('.aura-fade-in').forEach(el => el.classList.add('visible'));
    }

    // ==========================================
    // 4. Analysis Console Interactions
    // ==========================================
    const textInput = document.getElementById('aura-input');
    const charCount = document.getElementById('char-count');
    const fileUpload = document.getElementById('file-upload');
    const fileInfo = document.getElementById('file-info');
    const fileNameSpan = document.getElementById('file-name');
    const clearFileBtn = document.getElementById('clear-file');
    const toggleUrlBtn = document.getElementById('toggle-url');
    const urlContainer = document.getElementById('url-container');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsArea = document.getElementById('analysis-results');
    
    if (textInput && charCount) {
        textInput.addEventListener('input', (e) => {
            charCount.textContent = e.target.value.length;
        });
    }
    
    if (fileUpload && fileInfo) {
        fileUpload.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                fileNameSpan.textContent = e.target.files[0].name;
                fileInfo.classList.remove('d-none');
            }
        });
        
        clearFileBtn.addEventListener('click', () => {
            fileUpload.value = '';
            fileInfo.classList.add('d-none');
        });
    }
    
    if (toggleUrlBtn && urlContainer) {
        toggleUrlBtn.addEventListener('click', () => {
            urlContainer.classList.toggle('d-none');
        });
    }
    
    if (analyzeBtn && resultsArea) {
        analyzeBtn.addEventListener('click', async () => {
            const textContent = textInput ? textInput.value : '';
            const hasFile = fileUpload && fileUpload.files.length > 0;
            const urlContent = document.getElementById('url-input') ? document.getElementById('url-input').value : '';
            
            if (!textContent && !hasFile && !urlContent) {
                alert('Please provide text, a file, or a URL to analyze.');
                return;
            }
            
            resultsArea.classList.remove('d-none');
            
            let userContent = textContent;
            if (hasFile) userContent += `<br><span class="text-info small"><i class="bi bi-paperclip"></i> ${fileUpload.files[0].name}</span>`;
            if (urlContent) userContent += `<br><span class="text-info small"><i class="bi bi-link-45deg"></i> ${urlContent}</span>`;
            
            const userBubble = `
                <div class="d-flex justify-content-end w-100 mb-3">
                    <div class="aura-chat-bubble user">
                        ${userContent.replace(/\n/g, '<br>')}
                    </div>
                </div>
            `;
            
            const loadingId = 'loading-' + Date.now();
            const loadingBubble = `
                <div id="${loadingId}" class="d-flex align-items-start gap-3 w-100 mb-3">
                    <div class="flex-shrink-0 mt-1">
                        <div class="rounded-circle d-flex justify-content-center align-items-center shadow-lg" style="width: 40px; height: 40px; background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%); opacity: 0.7;">
                            <i class="bi bi-cpu text-white fs-5"></i>
                        </div>
                    </div>
                    <div class="aura-chat-bubble aura d-flex align-items-center gap-3">
                        <div class="spinner-grow spinner-grow-sm text-info" role="status"></div>
                        <span class="text-secondary">AURA is analyzing context...</span>
                    </div>
                </div>
            `;
            
            if (resultsArea.innerHTML.trim() === '<!-- Content injected via JS as chat bubbles -->') {
                resultsArea.innerHTML = userBubble + loadingBubble;
            } else {
                resultsArea.innerHTML += userBubble + loadingBubble;
            }
            
            // clear input
            if(textInput) { textInput.value = ''; charCount.textContent = '0'; }
            if(urlContent) { document.getElementById('url-input').value = ''; }
            
            analyzeBtn.disabled = true;
            
            try {
                // Prepare form data
                const formData = new FormData();
                formData.append('text', textContent);
                if (urlContent) formData.append('url', urlContent);
                if (hasFile) formData.append('file', fileUpload.files[0]);
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    let signalsHtml = '';
                    if (data.signals && data.signals.length > 0) {
                        signalsHtml = data.signals.map(s => 
                            `<span class="badge bg-dark bg-opacity-50 border border-secondary border-opacity-50 text-light fw-normal px-2 py-1"><i class="bi bi-tag text-info me-1"></i> ${s.name}</span>`
                        ).join('');
                    }
                    
                    let decisionBadgeClass = 'info';
                    if (data.decision.toLowerCase().includes('high risk') || data.decision.toLowerCase().includes('fake')) decisionBadgeClass = 'danger';
                    if (data.decision.toLowerCase().includes('safe') || data.decision.toLowerCase().includes('authentic')) decisionBadgeClass = 'success';
                    
                    const responseBubble = `
                        <div class="d-flex align-items-start gap-3 w-100 mb-3">
                            <div class="flex-shrink-0 mt-1">
                                <div class="rounded-circle d-flex justify-content-center align-items-center shadow-lg" style="width: 40px; height: 40px; background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%); box-shadow: 0 0 15px rgba(123,47,247,0.4) !important;">
                                    <i class="bi bi-cpu-fill text-white fs-5"></i>
                                </div>
                            </div>
                            <div class="aura-chat-bubble aura flex-grow-1">
                                <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 pb-2 border-bottom border-light border-opacity-10 gap-2">
                                    <div class="d-flex align-items-center gap-2">
                                        <span class="badge bg-white bg-opacity-10 border border-light border-opacity-25 text-light px-2 py-1"><i class="bi bi-cpu text-info me-1"></i> ${data.module.toUpperCase()}</span>
                                        <span class="badge bg-${decisionBadgeClass} bg-opacity-25 border border-${decisionBadgeClass} text-${decisionBadgeClass} px-2 py-1">${data.decision}</span>
                                    </div>
                                    <div class="text-secondary small">Confidence: <strong class="text-white">${data.confidence}%</strong></div>
                                </div>
                                
                                <div class="text-white fs-6 mb-3" style="line-height: 1.7; font-weight: 300;">
                                    ${data.explanation.replace(/\n/g, '<br>')}
                                </div>
                                
                                ${signalsHtml ? `<div class="d-flex flex-wrap gap-2 mt-3 pt-3 border-top border-light border-opacity-10">${signalsHtml}</div>` : ''}
                            </div>
                        </div>
                    `;
                    document.getElementById(loadingId).outerHTML = responseBubble;
                } else {
                    document.getElementById(loadingId).outerHTML = `<div class="aura-chat-bubble aura text-danger border-danger">${data.message || 'Analysis failed.'}</div>`;
                }
                
                // Scroll to bottom of results
                resultsArea.scrollTop = resultsArea.scrollHeight;
            } catch (error) {
                console.error('Analysis error:', error);
                document.getElementById(loadingId).outerHTML = `<div class="aura-chat-bubble aura text-danger border-danger">Network error connecting to AURA Core.</div>`;
            } finally {
                analyzeBtn.disabled = false;
                // clear file
                if(fileUpload) { fileUpload.value = ''; document.getElementById('file-info').classList.add('d-none'); }
            }
        });
    }

    // ==========================================
    // 5. Pipeline Animation
    // ==========================================
    function animatePipeline(container) {
        if (prefersReducedMotion) return;
        
        const stages = container.querySelectorAll('.aura-pipeline-stage');
        stages.forEach((stage, index) => {
            setTimeout(() => {
                stage.classList.add('active');
            }, index * 400); // 400ms delay between stages
        });
    }

    // ==========================================
    // 6. Flash Message Auto-dismiss
    // ==========================================
    const flashMessages = document.querySelectorAll('.aura-flash');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(msg);
            bsAlert.close();
        }, 5000);
    });

});

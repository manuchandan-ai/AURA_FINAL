/**
 * AURA — Adaptive Unified Reasoning Assistant
 * Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    
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
            resultsArea.innerHTML = `
                <div class="d-flex align-items-center justify-content-center p-5">
                    <div class="spinner-border text-info me-3" role="status" style="width: 3rem; height: 3rem;"></div>
                    <div class="text-start">
                        <h4 class="text-info mb-1">Intelligence Core Active</h4>
                        <div class="text-secondary small">Routing to optimal module...</div>
                    </div>
                </div>
            `;
            
            analyzeBtn.disabled = true;
            
            try {
                // Prepare form data (simulate for now since API isn't fully built for files)
                const formData = new FormData();
                formData.append('text', textContent);
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Calculate degree for score ring (e.g. 92% = 331deg)
                    const deg = (data.confidence / 100) * 360;
                    
                    let signalsHtml = '';
                    if (data.signals && data.signals.length > 0) {
                        signalsHtml = data.signals.map(s => 
                            `<span class="aura-signal-badge ${s.type}"><i class="bi bi-tag-fill"></i> ${s.name}</span>`
                        ).join('');
                    }
                    
                    resultsArea.innerHTML = `
                        <div class="aura-result-card aura-fade-in visible">
                            <div class="d-flex justify-content-between align-items-start mb-4">
                                <div>
                                    <h6 class="text-secondary text-uppercase tracking-wide mb-1">Detected Module</h6>
                                    <h4 class="text-white mb-0"><i class="bi bi-cpu text-primary me-2"></i>${data.module}</h4>
                                </div>
                                <div class="d-flex align-items-center gap-3">
                                    <div class="text-end">
                                        <div class="text-white fw-bold fs-5">${data.decision}</div>
                                        <div class="text-secondary small">Confidence</div>
                                    </div>
                                    <div class="aura-score-ring" style="--score-deg: ${deg}deg">
                                        <span>${data.confidence}%</span>
                                    </div>
                                </div>
                            </div>
                            
                            ${signalsHtml ? `<div class="mb-4 d-flex flex-wrap gap-2">${signalsHtml}</div>` : ''}
                            
                            <div class="aura-explanation-box">
                                <strong>Explanation:</strong> ${data.explanation}
                            </div>
                        </div>
                    `;
                } else {
                    resultsArea.innerHTML = `<div class="alert alert-danger bg-danger bg-opacity-10 border-0 text-danger">${data.message || 'Analysis failed.'}</div>`;
                }
            } catch (error) {
                console.error('Analysis error:', error);
                resultsArea.innerHTML = `<div class="alert alert-danger bg-danger bg-opacity-10 border-0 text-danger">Network error connecting to AURA Core.</div>`;
            } finally {
                analyzeBtn.disabled = false;
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

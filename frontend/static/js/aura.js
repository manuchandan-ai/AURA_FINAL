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
        analyzeBtn.addEventListener('click', () => {
            resultsArea.classList.remove('d-none');
            resultsArea.innerHTML = `
                <div class="d-flex align-items-center mb-3">
                    <div class="spinner-border spinner-border-sm text-info me-3" role="status"></div>
                    <span class="text-info fw-bold">Intelligence Core initializing...</span>
                </div>
            `;
            
            analyzeBtn.disabled = true;
            
            setTimeout(() => {
                resultsArea.innerHTML = `
                    <div class="alert alert-success border-0 bg-success bg-opacity-10 text-success mb-0">
                        <i class="bi bi-check-circle-fill me-2"></i>
                        System ready. Full analysis capabilities will be available after Stage 6 activation.
                    </div>
                `;
                analyzeBtn.disabled = false;
            }, 1500);
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

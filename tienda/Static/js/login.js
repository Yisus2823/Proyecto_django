document.addEventListener('DOMContentLoaded', () => {

    // ── PARTÍCULAS DE HUELLAS EN CANVAS ─── //
    const canvas = document.getElementById('pawCanvas');
    const ctx    = canvas.getContext('2d');
    let W, H;

    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Dibujar una huella de pata en canvas
    function drawPaw(x, y, size, alpha, color) {
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.fillStyle   = color;

        // Almohadilla central
        ctx.beginPath();
        ctx.ellipse(x, y, size * 0.55, size * 0.45, 0, 0, Math.PI * 2);
        ctx.fill();

        // 4 deditos
        const toes = [
            { ox: -size * 0.5, oy: -size * 0.55, rx: size * 0.22, ry: size * 0.2 },
            { ox:  0,           oy: -size * 0.72, rx: size * 0.22, ry: size * 0.2 },
            { ox:  size * 0.5,  oy: -size * 0.55, rx: size * 0.22, ry: size * 0.2 },
            { ox: -size * 0.28, oy: -size * 0.35, rx: size * 0.18, ry: size * 0.16 },
        ];
        toes.forEach(t => {
            ctx.beginPath();
            ctx.ellipse(x + t.ox, y + t.oy, t.rx, t.ry, 0, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();
    }

    // Partículas
    const COLORS = ['#FFD166', '#06D6A0', '#A78BFA', '#FF6B6B', '#4ECDC4'];
    const particles = [];

    class Particle {
        constructor() { this.reset(true); }
        reset(init = false) {
            this.x     = Math.random() * W;
            this.y     = init ? Math.random() * H : H + 40;
            this.size  = Math.random() * 10 + 6;
            this.speed = Math.random() * 0.4 + 0.15;
            this.alpha = 0;
            this.targetAlpha = Math.random() * 0.18 + 0.04;
            this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
            this.angle = Math.random() * Math.PI * 2;
            this.drift = (Math.random() - 0.5) * 0.3;
            this.wobble = Math.random() * Math.PI * 2;
            this.wobbleSpeed = Math.random() * 0.02 + 0.005;
        }
        update() {
            this.y       -= this.speed;
            this.wobble  += this.wobbleSpeed;
            this.x       += Math.sin(this.wobble) * this.drift;
            this.angle   += 0.005;
            // Fade in al aparecer, fade out al llegar arriba
            if (this.y > H * 0.8) {
                this.alpha = Math.min(this.alpha + 0.003, this.targetAlpha);
            } else {
                this.alpha = Math.max(this.alpha - 0.001, 0);
            }
            if (this.y < -40) this.reset();
        }
        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);
            ctx.translate(-this.x, -this.y);
            drawPaw(this.x, this.y, this.size, this.alpha, this.color);
            ctx.restore();
        }
    }

    for (let i = 0; i < 55; i++) particles.push(new Particle());

    function animateParticles() {
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animateParticles);
    }
    animateParticles();

    // ── TOGGLE CONTRASEÑA ──── //
    const toggleBtn = document.getElementById('togglePass');
    const passInput = document.getElementById('id_password');
    toggleBtn?.addEventListener('click', () => {
        const isPass = passInput.type === 'password';
        passInput.type = isPass ? 'text' : 'password';
        toggleBtn.textContent = isPass ? '🙈' : '👁️';
    });

    // ── RIPPLE EN BOTÓN ──  //
    const btnLogin = document.getElementById('btnLogin');
    btnLogin?.addEventListener('click', function(e) {
        const ripple = this.querySelector('.btn-ripple');
        const rect   = this.getBoundingClientRect();
        const size   = Math.max(rect.width, rect.height);
        ripple.style.width  = ripple.style.height = size + 'px';
        ripple.style.left   = (e.clientX - rect.left  - size / 2) + 'px';
        ripple.style.top    = (e.clientY - rect.top   - size / 2) + 'px';
        ripple.classList.remove('animate');
        void ripple.offsetWidth; // reflow
        ripple.classList.add('animate');
    });

    // ── LOADING STATE AL ENVIAR ── //
    const form = document.getElementById('loginForm');
    form?.addEventListener('submit', () => {
        btnLogin.classList.add('loading');
        btnLogin.disabled = true;
        const span = btnLogin.querySelector('.btn-text');
        span.textContent = 'Ingresando';
    });

    // ── FOCUS GLOW en inputs ─── //
    document.querySelectorAll('.input-wrap input').forEach(input => {
        input.addEventListener('focus', () => {
            input.closest('.field-group').style.transform = 'scale(1.01)';
            input.closest('.field-group').style.transition = 'transform .2s';
        });
        input.addEventListener('blur', () => {
            input.closest('.field-group').style.transform = 'scale(1)';
        });
    });

});

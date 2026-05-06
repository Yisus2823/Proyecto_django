
document.addEventListener('DOMContentLoaded', () => {

    // ── NAVBAR scroll effect ─────────────────────
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 20);
    });

    // ── HAMBURGER menú ──//
    const hamburger = document.getElementById('hamburger');
    const navLinks  = document.querySelector('.nav-links');
    hamburger?.addEventListener('click', () => {
        navLinks.classList.toggle('open');
    });
    // Cerrar menú al hacer click en un link
    navLinks?.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => navLinks.classList.remove('open'));
    });

    // ── CARRUSEL ── //
    const slides    = document.querySelectorAll('.slide');
    const dots      = document.querySelectorAll('.dot');
    const prevBtn   = document.getElementById('prevBtn');
    const nextBtn   = document.getElementById('nextBtn');
    let current     = 0;
    let autoTimer   = null;

    function goTo(index) {
        slides[current].classList.remove('active');
        dots[current].classList.remove('active');
        current = (index + slides.length) % slides.length;
        slides[current].classList.add('active');
        dots[current].classList.add('active');
    }

    function startAuto() {
        autoTimer = setInterval(() => goTo(current + 1), 4500);
    }
    function resetAuto() {
        clearInterval(autoTimer);
        startAuto();
    }

    prevBtn?.addEventListener('click', () => { goTo(current - 1); resetAuto(); });
    nextBtn?.addEventListener('click', () => { goTo(current + 1); resetAuto(); });
    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            goTo(parseInt(dot.dataset.index));
            resetAuto();
        });
    });

    // Swipe táctil
    let touchStartX = 0;
    const track = document.getElementById('carouselTrack');
    track?.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; });
    track?.addEventListener('touchend', e => {
        const diff = touchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) {
            goTo(diff > 0 ? current + 1 : current - 1);
            resetAuto();
        }
    });

    startAuto();

    // ── CATEGORY PILLS ── //
    const pills = document.querySelectorAll('.pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
        });
    });

    // ── SCROLL REVEAL (Intersection Observer) ── //
    const revealEls = document.querySelectorAll(
        '.producto-card, .nosotros-grid, .promo-banner, .stat-chip, .feature'
    );
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    revealEls.forEach((el, i) => {
        // Solo aplica a cards que no son skeleton
        if (!el.classList.contains('skeleton')) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = `opacity .5s ease ${i * 80}ms, transform .5s ease ${i * 80}ms`;
            observer.observe(el);
        }
    });

});
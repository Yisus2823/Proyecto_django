document.addEventListener('DOMContentLoaded', () => {

    // ── Estado de filtros activos ────────────────
    const params = new URLSearchParams(window.location.search);
    let estado = {
        q:         params.get('q')         || '',
        especie:   params.get('especie')   || '',
        categoria: params.get('categoria') || '',
        orden:     params.get('orden')     || '',
    };

    function aplicarFiltros() {
        const url = new URLSearchParams();
        if (estado.q)         url.set('q',         estado.q);
        if (estado.especie)   url.set('especie',   estado.especie);
        if (estado.categoria) url.set('categoria', estado.categoria);
        if (estado.orden)     url.set('orden',     estado.orden);
        window.location.href = '/catalogo/?' + url.toString();
    }

    // ── BUSCADOR con debounce ────────────────────
    const searchInput = document.getElementById('searchInput');
    let timer = null;
    searchInput?.addEventListener('input', () => {
        clearTimeout(timer);
        estado.q = searchInput.value.trim();
        timer = setTimeout(aplicarFiltros, 600);
    });

    // ── PILLS de especie ─────────────────────────
    document.querySelectorAll('.pill-especie').forEach(btn => {
        btn.addEventListener('click', () => {
            estado.especie = btn.dataset.value;
            aplicarFiltros();
        });
    });

    // ── PILLS de categoría ───────────────────────
    document.querySelectorAll('.pill-cat').forEach(btn => {
        btn.addEventListener('click', () => {
            estado.categoria = btn.dataset.value;
            aplicarFiltros();
        });
    });

    // ── SELECT ordenar ───────────────────────────
    document.getElementById('ordenSelect')?.addEventListener('change', function() {
        estado.orden = this.value;
        aplicarFiltros();
    });

    // ── Limpiar búsqueda ─────────────────────────
    document.querySelector('.search-clear')?.addEventListener('click', () => {
        estado.q = '';
        searchInput.value = '';
        aplicarFiltros();
    });

    // ── NAVBAR scroll ────────────────────────────
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 20);
    });

    // ── HAMBURGER ────────────────────────────────
    document.getElementById('hamburger')?.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.toggle('open');
    });

    // ── ANIMACIÓN cards ──────────────────────────
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.style.opacity = '1';
                e.target.style.transform = 'translateY(0)';
                observer.unobserve(e.target);
            }
        });
    }, { threshold: 0.08 });

    document.querySelectorAll('.producto-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(24px)';
        card.style.transition = `opacity .4s ease ${i * 40}ms, transform .4s ease ${i * 40}ms`;
        observer.observe(card);
    });

    // ── HIGHLIGHT búsqueda ───────────────────────
    const query = estado.q;
    if (query) {
        const regex = new RegExp(`(${query})`, 'gi');
        document.querySelectorAll('.card-title, .card-desc').forEach(el => {
            el.innerHTML = el.textContent.replace(
                regex,
                '<mark style="background:rgba(255,209,102,0.5);border-radius:3px;padding:0 2px">$1</mark>'
            );
        });
    }
});
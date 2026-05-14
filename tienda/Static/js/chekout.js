
/* ════════════════════════════════════
   TABS DE MÉTODOS DE PAGO
════════════════════════════════════ */
document.querySelectorAll('.metodo-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        if (tab.disabled) return;
        const metodo = tab.dataset.metodo;

        document.querySelectorAll('.metodo-tab').forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.metodo-panel').forEach(p => {
            p.classList.remove('active');
        });

        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        document.getElementById(`panel-${metodo}`).classList.add('active');
    });
});

/* ════════════════════════════════════
   COPIAR AL PORTAPAPELES
════════════════════════════════════ */
function copiar(id, btn) {
    const texto = document.getElementById(id).textContent.trim();
    navigator.clipboard.writeText(texto).then(() => {
        const orig = btn.textContent;
        btn.textContent = '✅';
        setTimeout(() => btn.textContent = orig, 1800);
    });
}

/* ════════════════════════════════════
   CANVAS — PARTÍCULAS DE PATITAS
   (mismo sistema que login.js)
════════════════════════════════════ */
(function () {
    const canvas = document.getElementById('pawCanvas');
    const ctx = canvas.getContext('2d');
    let paws = [];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    function nuevaPata() {
        return {
            x: Math.random() * canvas.width,
            y: canvas.height + 30,
            size: Math.random() * 14 + 8,
            speed: Math.random() * 0.6 + 0.3,
            opacity: Math.random() * 0.12 + 0.04,
            rot: Math.random() * Math.PI * 2,
            rotSpeed: (Math.random() - 0.5) * 0.02,
        };
    }

    function dibujarPata(p) {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.globalAlpha = p.opacity;
        ctx.font = `${p.size * 2}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🐾', 0, 0);
        ctx.restore();
    }

    function animar() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (Math.random() < 0.04) paws.push(nuevaPata());
        paws.forEach(p => {
            p.y -= p.speed;
            p.rot += p.rotSpeed;
            dibujarPata(p);
        });
        paws = paws.filter(p => p.y > -40);
        requestAnimationFrame(animar);
    }
    animar();
})();


document.getElementById('btn-paypal').addEventListener('click', async function () {
    const btn = this;
    btn.disabled = true;
    btn.querySelector('.btn-pagar-text').textContent = 'Conectando con PayPal...';

    // Obtener CSRF desde la cookie, más confiable que el template tag
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    try {
        const res = await fetch('/pago/paypal/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            // Sin Content-Type — Django lo maneja mejor así para CSRF
        });

        // Verificar que la respuesta sea JSON antes de parsear
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error(`Respuesta inesperada del servidor (${res.status})`);
        }

        const data = await res.json();

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            alert('Error PayPal: ' + (data.error || 'intenta de nuevo'));
            btn.disabled = false;
            btn.querySelector('.btn-pagar-text').textContent = 'Pagar con PayPal';
        }
    } catch (err) {
        console.error('Error fetch PayPal:', err);
        alert('Error: ' + err.message);
        btn.disabled = false;
        btn.querySelector('.btn-pagar-text').textContent = 'Pagar con PayPal';
    }
});



/* ════════════════════════════════════
   MERCADO PAGO — fetch + redirect
════════════════════════════════════ */
document.getElementById('btn-mercadopago')?.addEventListener('click', async function () {
    const btn = this;
    btn.disabled = true;
    btn.querySelector('.btn-pagar-text').textContent = 'Conectando con Mercado Pago...';

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    try {
        const res = await fetch('/pago/mercadopago/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });

        const contentType = res.headers.get('content-type');
        if (!contentType?.includes('application/json')) {
            throw new Error(`Respuesta inesperada (${res.status})`);
        }

        const data = await res.json();

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            alert('Error Mercado Pago: ' + (data.error || 'intenta de nuevo'));
            btn.disabled = false;
            btn.querySelector('.btn-pagar-text').textContent = 'Pagar con Mercado Pago';
        }
    } catch (err) {
        alert('Error de red: ' + err.message);
        btn.disabled = false;
        btn.querySelector('.btn-pagar-text').textContent = 'Pagar con Mercado Pago';
    }
});
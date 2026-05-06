/* ═══════════════════════════════════════════
   VetShop — detalle.js
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    window.addEventListener('pageshow', (e) => {
        if (e.persisted) window.location.reload();
    });

    // ── NAVBAR ──────────────────────────────────
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar?.classList.toggle('scrolled', window.scrollY > 20);
    });
    document.getElementById('hamburger')?.addEventListener('click', () => {
        document.querySelector('.nav-links')?.classList.toggle('open');
    });

    // ── CANTIDAD ────────────────────────────────
    let cantidad = 1;
    const qtyValue   = document.getElementById('qtyValue');
    const btnAgregar = document.getElementById('btnAgregar'); // ← definido aquí

    // Leer stock desde el badge del HTML
    const stockTexto = document.querySelector('.stock-badge')?.textContent || '';
    const stockMax   = parseInt(stockTexto.match(/\d+/)?.[0]) || 1;

    document.getElementById('qtyMinus')?.addEventListener('click', () => {
        if (cantidad > 1) {
            cantidad--;
            qtyValue.textContent = cantidad;
        }
    });

    document.getElementById('qtyPlus')?.addEventListener('click', () => {
        if (cantidad < stockMax) {
            cantidad++;
            qtyValue.textContent = cantidad;
        } else {
            window.mostrarToast(`Stock máximo disponible: ${stockMax} unidades 📦`, false);
        }
    });

    // ── AGREGAR AL CARRITO ───────────────────────
    btnAgregar?.addEventListener('click', async () => {
        const productoId = btnAgregar.dataset.productoId;
        const csrf       = btnAgregar.dataset.csrf;

        if (!productoId || !csrf) return;

        btnAgregar.disabled = true;
        btnAgregar.querySelector('.btn-agregar-text').textContent = 'Agregando...';

        await window.agregarAlCarrito(productoId, csrf, cantidad);

        btnAgregar.disabled = false;
        btnAgregar.querySelector('.btn-agregar-text').textContent = 'Agregar al carrito';
        cantidad = 1;
        if (qtyValue) qtyValue.textContent = '1';
    });

});
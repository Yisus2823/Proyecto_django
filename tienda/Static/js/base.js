/* ═══════════════════════════════════════════
   VetShop — base.js
   Compartido en todos los HTMLs vía base.html
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ── NAVBAR scroll ────────────────────────────
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar?.classList.toggle('scrolled', window.scrollY > 20);
    });

    // ── HAMBURGER ────────────────────────────────
    document.getElementById('hamburger')?.addEventListener('click', () => {
        document.querySelector('.nav-links')?.classList.toggle('open');
    });

    // ── CARRITO DRAWER ───────────────────────────
    const toggleBtn  = document.getElementById('carritoToggle');
    const drawer     = document.getElementById('carritoDrawer');
    const overlay    = document.getElementById('carritoOverlay');
    const closeBtn   = document.getElementById('carritoClose');

    function abrirCarrito() {
        drawer?.classList.add('open');
        overlay?.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    function cerrarCarrito() {
        drawer?.classList.remove('open');
        overlay?.classList.remove('open');
        document.body.style.overflow = '';
    }

    toggleBtn?.addEventListener('click', abrirCarrito);
    closeBtn?.addEventListener('click', cerrarCarrito);
    overlay?.addEventListener('click', cerrarCarrito);
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') cerrarCarrito();
    });

    // ── TOAST global ─────────────────────────────
    window.mostrarToast = function(msg, ok = true) {
        const toast    = document.getElementById('toast');
        const toastMsg = document.getElementById('toastMsg');
        const toastIcon = document.getElementById('toastIcon');
        if (!toast) return;
        toastIcon.textContent = ok ? '✅' : '❌';
        toastMsg.textContent  = msg;
        toast.classList.add('show');
        clearTimeout(window._toastTimer);
        window._toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
    };

    // ── ACTUALIZAR BADGE ─────────────────────────
    window.actualizarBadge = function(cantidad) {
        const badge = document.getElementById('carritoBadge');
        if (!badge) return;
        badge.textContent = cantidad;
        if (cantidad > 0) {
            badge.classList.remove('carrito-badge-hidden');
            badge.classList.add('pop');
            setTimeout(() => badge.classList.remove('pop'), 300);
        } else {
            badge.classList.add('carrito-badge-hidden');
        }
    };

    // ── ACTUALIZAR TOTAL ─────────────────────────
    window.actualizarTotal = function(total) {
        const el = document.getElementById('carritoTotal');
        if (el) el.textContent = `$${total}`;
    };

    // ── MOSTRAR/OCULTAR FOOTER CARRITO ───────────
    window.toggleFooterCarrito = function(cantidadItems) {
        const footer = document.getElementById('carritoFooter');
        const empty  = document.getElementById('carritoEmpty');
        if (!footer) return;
        if (cantidadItems > 0) {
            footer.classList.remove('carrito-footer-hidden');
            empty?.remove();
        } else {
            footer.classList.add('carrito-footer-hidden');
            // Mostrar estado vacío
            const body = document.getElementById('carritoBody');
            if (body && !document.getElementById('carritoEmpty')) {
                body.innerHTML = `
                    <div class="carrito-empty" id="carritoEmpty">
                        <div class="empty-paw">🐾</div>
                        <p>Tu carrito está vacío</p>
                        <a href="/catalogo/" class="btn-ver-productos">Ver productos</a>
                    </div>`;
            }
        }
    };

    // ── CAMBIAR CANTIDAD ─────────────────────────
    window.cambiarCantidad = async function(itemId, nuevaCantidad) {
        const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
        const item = document.getElementById(`carritoItem${itemId}`);

        // ── Validar stock antes de enviar ──
        const stockMax = parseInt(item?.dataset.stock || 99);
        if (nuevaCantidad > stockMax) {
            mostrarToast(`Stock máximo disponible: ${stockMax} unidades 📦`, false);
            return;
        }

        try {
            const res  = await fetch(`/carrito/actualizar/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cantidad: nuevaCantidad })
            });
            const data = await res.json();
            if (!data.ok) return;

            if (nuevaCantidad < 1) {
                item?.classList.add('removing');
                setTimeout(() => item?.remove(), 300);
            } else {
                const qtyEl = document.getElementById(`qty${itemId}`);
                const subEl = document.getElementById(`sub${itemId}`);
                if (qtyEl) qtyEl.textContent = nuevaCantidad;
                if (subEl) subEl.textContent = `$${data.subtotal}`;

                // Actualizar onclick de botones
                const btns = item?.querySelectorAll('.qty-btn-sm');
                btns?.[0]?.setAttribute('onclick', `cambiarCantidad(${itemId}, ${nuevaCantidad} - 1)`);
                btns?.[1]?.setAttribute('onclick', `cambiarCantidad(${itemId}, ${nuevaCantidad} + 1)`);
            }

            actualizarTotal(data.total);
            actualizarBadge(data.cantidad_total);
            toggleFooterCarrito(data.cantidad_total);

        } catch(e) {
            mostrarToast('Error al actualizar', false);
        }
    };

    // ── ELIMINAR ITEM ────────────────────────────
    window.eliminarItem = async function(itemId) {
        const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
        try {
            const item = document.getElementById(`carritoItem${itemId}`);
            item?.classList.add('removing');

            const res  = await fetch(`/carrito/eliminar/${itemId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf }
            });
            const data = await res.json();

            setTimeout(() => item?.remove(), 300);
            actualizarTotal(data.total);
            actualizarBadge(data.cantidad_total);
            toggleFooterCarrito(data.cantidad_total);
            mostrarToast('Producto eliminado del carrito');

        } catch(e) {
            mostrarToast('Error al eliminar', false);
        }
    };

    // ── AGREGAR AL CARRITO (global) ──────────────
    // Disponible para detalle.js y cualquier otro script
    window.agregarAlCarrito = async function(productoId, csrf, cantidad = 1) {
        try {
            const res  = await fetch(`/carrito/agregar/${productoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cantidad: cantidad })  // ← envía la cantidad
            });
            const data = await res.json();

            if (!data.ok) {
                // Sin stock disponible
                mostrarToast(data.msg || 'Sin stock disponible', false);
                return false;
            }

            // Avisa si se ajustó la cantidad
            if (data.ajustado) {
                mostrarToast(`Solo había stock para ${data.item_cantidad} unidad(es) 📦`);
            } else {
                mostrarToast(`${cantidad} producto(s) agregado(s) al carrito 🛒`);
            }

            actualizarBadge(data.cantidad_total);
            actualizarTotal(data.total);

            const itemExistente = document.getElementById(`carritoItem${data.item_id}`);
            if (itemExistente) {
                const qtyEl = itemExistente.querySelector(`#qty${data.item_id}`);
                const subEl = itemExistente.querySelector(`#sub${data.item_id}`);
                if (qtyEl) qtyEl.textContent = data.item_cantidad;
                if (subEl) subEl.textContent = `$${data.item_subtotal}`;
                const btns = itemExistente.querySelectorAll('.qty-btn-sm');
                btns[0]?.setAttribute('onclick', `cambiarCantidad(${data.item_id}, ${data.item_cantidad} - 1)`);
                btns[1]?.setAttribute('onclick', `cambiarCantidad(${data.item_id}, ${data.item_cantidad} + 1)`);
            } else {
                insertarItemEnDrawer(data);
            }

            toggleFooterCarrito(data.cantidad_total);
            abrirCarrito();
            return true;

        } catch(e) {
            mostrarToast('Error al agregar', false);
            return false;
        }
    };

    function insertarItemEnDrawer(data) {
        document.getElementById('carritoEmpty')?.remove();
        const body = document.getElementById('carritoBody');
        if (!body) return;

        const div = document.createElement('div');
        div.className = 'carrito-item';
        div.id = `carritoItem${data.item_id}`;
        div.dataset.itemId = data.item_id;
        div.dataset.stock  = data.item_stock;  // ← guardar stock en el DOM
        div.innerHTML = `
            <div class="item-img">
                ${data.item_imagen
                    ? `<img src="${data.item_imagen}" alt="${data.item_nombre}">`
                    : '<span>🐾</span>'
                }
            </div>
            <div class="item-info">
                <span class="item-nombre">${data.item_nombre}</span>
                <span class="item-precio">$${data.item_precio}</span>
                <div class="item-qty">
                    <button class="qty-btn-sm" onclick="cambiarCantidad(${data.item_id}, ${data.item_cantidad} - 1)">−</button>
                    <span class="qty-num" id="qty${data.item_id}">${data.item_cantidad}</span>
                    <button class="qty-btn-sm" onclick="cambiarCantidad(${data.item_id}, ${data.item_cantidad} + 1)">+</button>
                </div>
            </div>
            <div class="item-actions">
                <span class="item-subtotal" id="sub${data.item_id}">$${data.item_subtotal}</span>
                <button class="item-delete" onclick="eliminarItem(${data.item_id})">🗑️</button>
            </div>
        `;
        body.appendChild(div);
    }
});

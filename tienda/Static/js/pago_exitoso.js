/* ════════════════════════════════════
   PAGO EXITOSO — pago_exitoso.js
   Animación del SVG + imprimir boleta
════════════════════════════════════ */
 
document.addEventListener('DOMContentLoaded', () => {
 
    /* ── Animar el círculo y el check/icono SVG al cargar ── */
    const circle = document.querySelector('.check-circle');
    const mark   = document.querySelector('.check-mark');
 
    if (circle) {
        const circleLen = circle.getTotalLength?.() || 150;
        circle.style.strokeDasharray  = circleLen;
        circle.style.strokeDashoffset = circleLen;
        circle.style.transition = 'stroke-dashoffset 0.6s cubic-bezier(0.65,0,0.45,1)';
 
        requestAnimationFrame(() => {
            setTimeout(() => {
                circle.style.strokeDashoffset = '0';
            }, 100);
        });
    }
 
    if (mark) {
        const markLen = mark.getTotalLength?.() || 50;
        mark.style.strokeDasharray  = markLen;
        mark.style.strokeDashoffset = markLen;
        mark.style.transition = 'stroke-dashoffset 0.4s cubic-bezier(0.65,0,0.45,1) 0.55s';
 
        requestAnimationFrame(() => {
            setTimeout(() => {
                mark.style.strokeDashoffset = '0';
            }, 100);
        });
    }
 
    /* ── Entrada animada de la boleta ── */
    const boleta = document.querySelector('.boleta-card');
    if (boleta) {
        boleta.style.opacity   = '0';
        boleta.style.transform = 'translateY(24px)';
        boleta.style.transition = 'opacity 0.5s ease 0.3s, transform 0.5s ease 0.3s';
        requestAnimationFrame(() => {
            setTimeout(() => {
                boleta.style.opacity   = '1';
                boleta.style.transform = 'translateY(0)';
            }, 50);
        });
    }
 
});
 
/* ════════════════════════════════════
   IMPRIMIR BOLETA
   Oculta todo menos la boleta-card
════════════════════════════════════ */
function imprimirBoleta() {
    window.print();
}
document.addEventListener('DOMContentLoaded', () => {

    // ── TOGGLE CONTRASEÑAS ──  //
    document.querySelectorAll('.toggle-pass').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input    = document.getElementById(targetId);
            const isPass   = input.type === 'password';
            input.type     = isPass ? 'text' : 'password';
            btn.textContent = isPass ? '🙈' : '👁️';
        });
    });

    // ── INDICADOR DE FORTALEZA ──── //
    const pass1        = document.getElementById('pass1');
    const strengthWrap = document.getElementById('strengthWrap');
    const strengthFill = document.getElementById('strengthFill');
    const strengthLabel = document.getElementById('strengthLabel');

    const levels = [
        { label: 'Muy débil',  cls: 'weak',   width: '20%',  color: '#ff9a9a' },
        { label: 'Débil',      cls: 'weak',   width: '35%',  color: '#ff9a9a' },
        { label: 'Regular',    cls: 'fair',   width: '55%',  color: '#FFD166' },
        { label: 'Buena',      cls: 'good',   width: '75%',  color: '#63e6be' },
        { label: '¡Fuerte!',   cls: 'strong', width: '100%', color: '#06D6A0' },
    ];

    function checkStrength(pw) {
        let score = 0;
        if (pw.length >= 8)               score++;
        if (pw.length >= 12)              score++;
        if (/[A-Z]/.test(pw))            score++;
        if (/[0-9]/.test(pw))            score++;
        if (/[^A-Za-z0-9]/.test(pw))    score++;
        return Math.min(score, 4);
    }

    pass1?.addEventListener('input', () => {
        const val = pass1.value;
        if (!val) {
            strengthWrap.classList.remove('visible');
            return;
        }
        strengthWrap.classList.add('visible');
        const idx   = checkStrength(val);
        const level = levels[idx];
        strengthFill.style.width = level.width;
        strengthFill.className   = `strength-fill ${level.cls}`;
        strengthLabel.textContent = level.label;
        strengthLabel.style.color = level.color;
    });

    // ── VALIDACIÓN CONTRASEÑAS COINCIDEN ──── //
    const pass2 = document.getElementById('pass2');
    pass2?.addEventListener('input', () => {
        const group = pass2.closest('.field-group');
        if (pass2.value && pass1.value !== pass2.value) {
            group.classList.add('has-error');
            let errSpan = group.querySelector('.field-error');
            if (!errSpan) {
                errSpan = document.createElement('span');
                errSpan.className = 'field-error';
                group.appendChild(errSpan);
            }
            errSpan.textContent = 'Las contraseñas no coinciden';
        } else {
            group.classList.remove('has-error');
            const errSpan = group.querySelector('.field-error');
            if (errSpan) errSpan.remove();
        }
    });

    // ── RIPPLE EN BOTÓN ── //
    const btnRegistro = document.getElementById('btnRegistro');
    btnRegistro?.addEventListener('click', function(e) {
        const ripple = this.querySelector('.btn-ripple');
        const rect   = this.getBoundingClientRect();
        const size   = Math.max(rect.width, rect.height);
        ripple.style.width  = ripple.style.height = size + 'px';
        ripple.style.left   = (e.clientX - rect.left  - size / 2) + 'px';
        ripple.style.top    = (e.clientY - rect.top   - size / 2) + 'px';
        ripple.classList.remove('animate');
        void ripple.offsetWidth;
        ripple.classList.add('animate');
    });

    // ── LOADING AL ENVIAR ───  //
    const form = document.getElementById('registroForm');
    form?.addEventListener('submit', (e) => {
        // Verificar que contraseñas coincidan antes de enviar
        if (pass1.value !== pass2.value) {
            e.preventDefault();
            return;
        }
        btnRegistro.classList.add('loading');
        btnRegistro.disabled = true;
        btnRegistro.querySelector('.btn-text').textContent = 'Creando cuenta';
    });

    // ── FOCUS SCALE en inputs ─── //
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

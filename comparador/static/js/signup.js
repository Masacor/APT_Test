document.addEventListener('DOMContentLoaded', function () {

    const signupForm = document.querySelector('.signup-form');

    const nombreInput = document.getElementById('nombre');
    const emailInput = document.getElementById('email');
    const fechaInput = document.getElementById('fecha_nacimiento');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    const regionInput = document.getElementById('region');
    const comunaInput = document.getElementById('comuna');

    const nombreError = document.getElementById('nombre-error');
    const emailError = document.getElementById('email-error');
    const fechaError = document.getElementById('fecha-error');
    const password1Error = document.getElementById('password1-error');
    const password2Error = document.getElementById('password2-error');
    const regionError = document.getElementById('region-error');
    const comunaError = document.getElementById('comuna-error');

    // -------------------- EVENTOS DE VALIDACIÓN --------------------
    nombreInput.addEventListener('input', validateNombre);
    emailInput.addEventListener('input', validateEmail);
    fechaInput.addEventListener('change', validateFecha);
    password1Input.addEventListener('input', validatePasswords);
    password2Input.addEventListener('input', validatePasswords);
    regionInput.addEventListener('change', loadComunas);

    // -------------------- CARGAR COMUNAS POR REGIÓN --------------------
    function loadComunas() {
        const regionId = regionInput.value;
        comunaError.textContent = "";
        comunaInput.innerHTML = '<option value="">Seleccione comuna</option>';
        comunaInput.disabled = true;

        if (!regionId) {
            comunaError.textContent = "Seleccione primero una región";
            return;
        }

        const filtradas = comunasChile.filter(c => String(c.region) === String(regionId));

        filtradas.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.id;
            opt.textContent = c.nombre;
            comunaInput.appendChild(opt);
        });

        comunaInput.disabled = false;
    }

    // ------------------------- VALIDACIONES -------------------------
    function validateNombre() {
        const nombre = nombreInput.value.trim();
        nombreError.textContent = '';

        if (!nombre) {
            nombreError.textContent = 'El nombre es obligatorio';
            return false;
        }

        if (nombre.length < 2) {
            nombreError.textContent = 'El nombre debe tener al menos 2 caracteres';
            return false;
        }

        return true;
    }

    function validateEmail() {
        const email = emailInput.value.trim();
        emailError.textContent = '';

        if (!email) {
            emailError.textContent = 'El correo es obligatorio';
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            emailError.textContent = 'Ingrese un correo válido';
            return false;
        }

        return true;
    }

    function validateFecha() {
        const fecha = fechaInput.value;
        fechaError.textContent = '';

        if (!fecha) {
            fechaError.textContent = 'La fecha es obligatoria';
            return false;
        }

        const nacimiento = new Date(fecha);
        const hoy = new Date();
        let edad = hoy.getFullYear() - nacimiento.getFullYear();
        const mes = hoy.getMonth() - nacimiento.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
            edad--;
        }

        if (edad < 13) {
            fechaError.textContent = 'Debes tener al menos 13 años';
            return false;
        }

        if (edad > 120) {
            fechaError.textContent = 'Fecha inválida';
            return false;
        }

        return true;
    }

    function validatePasswords() {
        const p1 = password1Input.value;
        const p2 = password2Input.value;

        password1Error.textContent = '';
        password2Error.textContent = '';

        let ok = true;

        if (!p1) {
            password1Error.textContent = 'La contraseña es obligatoria';
            ok = false;
        } else if (p1.length < 6) {
            password1Error.textContent = 'Mínimo 6 caracteres';
            ok = false;
        }

        if (!p2) {
            password2Error.textContent = 'Confirma tu contraseña';
            ok = false;
        } else if (p1 !== p2) {
            password2Error.textContent = 'Las contraseñas no coinciden';
            ok = false;
        }

        return ok;
    }

    // ------------------------- VALIDACIÓN FINAL -------------------------
    signupForm.addEventListener('submit', function (e) {

        let isValid = true;

        if (!validateNombre()) isValid = false;
        if (!validateEmail()) isValid = false;
        if (!validateFecha()) isValid = false;
        if (!validatePasswords()) isValid = false;

        if (!regionInput.value) {
            regionError.textContent = "Seleccione una región";
            isValid = false;
        } else {
            regionError.textContent = "";
        }

        if (!comunaInput.value) {
            comunaError.textContent = "Seleccione una comuna";
            isValid = false;
        } else {
            comunaError.textContent = "";
        }

        if (!isValid) e.preventDefault();
    });

});

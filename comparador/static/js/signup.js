document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.querySelector('.signup-form');
    const nombreInput = document.getElementById('nombre');
    const emailInput = document.getElementById('email');
    const fechaInput = document.getElementById('fecha_nacimiento');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    
    const nombreError = document.getElementById('nombre-error');
    const emailError = document.getElementById('email-error');
    const fechaError = document.getElementById('fecha-error');
    const password1Error = document.getElementById('password1-error');
    const password2Error = document.getElementById('password2-error');

    // Validación en tiempo real
    nombreInput.addEventListener('input', validateNombre);
    emailInput.addEventListener('input', validateEmail);
    fechaInput.addEventListener('change', validateFecha);
    password1Input.addEventListener('input', validatePasswords);
    password2Input.addEventListener('input', validatePasswords);

    // Validación antes de enviar
    signupForm.addEventListener('submit', function(e) {
        let isValid = true;

        if (!validateNombre()) isValid = false;
        if (!validateEmail()) isValid = false;
        if (!validateFecha()) isValid = false;
        if (!validatePasswords()) isValid = false;

        if (!isValid) {
            e.preventDefault();
        }
    });

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
            emailError.textContent = 'El correo electrónico es obligatorio';
            return false;
        }

        if (!isValidEmail(email)) {
            emailError.textContent = 'Ingresa un correo electrónico válido';
            return false;
        }

        return true;
    }

    function validateFecha() {
        const fecha = fechaInput.value;
        fechaError.textContent = '';

        if (!fecha) {
            fechaError.textContent = 'La fecha de nacimiento es obligatoria';
            return false;
        }

        const fechaNac = new Date(fecha);
        const hoy = new Date();
        let edad = hoy.getFullYear() - fechaNac.getFullYear();
        const mes = hoy.getMonth() - fechaNac.getMonth();
        
        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
            edad--;
        }

        if (edad < 13) {
            fechaError.textContent = 'Debes tener al menos 13 años';
            return false;
        }

        if (edad > 120) {
            fechaError.textContent = 'Por favor ingresa una fecha válida';
            return false;
        }

        return true;
    }

    function validatePasswords() {
        const password1 = password1Input.value;
        const password2 = password2Input.value;
        
        password1Error.textContent = '';
        password2Error.textContent = '';

        let isValid = true;

        if (!password1) {
            password1Error.textContent = 'La contraseña es obligatoria';
            isValid = false;
        } else if (password1.length < 6) {
            password1Error.textContent = 'La contraseña debe tener al menos 6 caracteres';
            isValid = false;
        }

        if (!password2) {
            password2Error.textContent = 'Confirma tu contraseña';
            isValid = false;
        } else if (password1 !== password2) {
            password2Error.textContent = 'Las contraseñas no coinciden';
            isValid = false;
        }

        return isValid;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
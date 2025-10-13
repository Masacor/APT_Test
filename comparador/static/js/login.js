document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');

    // Validación en tiempo real
    emailInput.addEventListener('input', validateEmail);
    passwordInput.addEventListener('input', validatePassword);

    // Validación antes de enviar el formulario
    loginForm.addEventListener('submit', function(e) {
        let isValid = true;

        if (!validateEmail()) isValid = false;
        if (!validatePassword()) isValid = false;

        if (!isValid) {
            e.preventDefault();
        }
    });

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

    function validatePassword() {
        const password = passwordInput.value;
        passwordError.textContent = '';

        if (!password) {
            passwordError.textContent = 'La contraseña es obligatoria';
            return false;
        }

        if (password.length < 6) {
            passwordError.textContent = 'La contraseña debe tener al menos 6 caracteres';
            return false;
        }

        return true;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
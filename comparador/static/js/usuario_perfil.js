function habilitarEdicion(campo) {
    const input = document.getElementById(campo + "-input");
    const texto = document.getElementById(campo + "-texto");

    if (input.classList.contains("perfil-input-hidden")) {
        input.classList.remove("perfil-input-hidden");
        texto.style.display = "none";
    } else {
        input.classList.add("perfil-input-hidden");
        texto.style.display = "inline";
    }
}

function mostrarCambioContrasena() {
    const div = document.getElementById("cambio-contrasena");
    div.style.display = div.style.display === "none" ? "block" : "none";
}

// Helper para obtener el CSRF token desde cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleGuardado(presentacionId, btn) {
    const csrftoken = getCookie('csrftoken');
    const formData = new FormData();
    formData.append('presentacion_id', presentacionId);

    fetch('/guardar-presentacion/', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.action === 'removed') {
                // animar y luego eliminar la tarjeta/elemento
                const card = btn.closest('.guardado-card') || btn.closest('li');
                if (card) {
                    card.classList.add('removing');
                    setTimeout(() => {
                        card.remove();
                    }, 220);
                } else {
                    const li = btn.closest('li');
                    if (li) li.remove();
                }
            } else if (data.action === 'saved') {
                // opcional: cambiar texto del botón
                btn.textContent = 'Guardado';
            }
        } else {
            alert(data.message || 'Ocurrió un error');
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error de red al intentar actualizar');
    });
}

// Bind buttons and card clicks after DOM loaded
document.addEventListener('DOMContentLoaded', function() {
    // Attach desmarcar listeners
    document.querySelectorAll('.btn-desmarcar').forEach(function(button) {
        button.addEventListener('click', function(event) {
            // evitar que el click en el botón propague a la tarjeta
            event.stopPropagation();
            const pid = this.getAttribute('data-presentacion');
            toggleGuardado(pid, this);
        });
    });

    // Make whole card clickable
    document.querySelectorAll('.guardado-card').forEach(function(card) {
        card.addEventListener('click', function() {
            const href = this.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        });
    });
});

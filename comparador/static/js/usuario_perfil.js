function habilitarEdicion(campo) {
    const input = document.getElementById(campo + "-input");
    const texto = document.getElementById(campo + "-texto");

    if (input.style.display === "none" || input.style.display === "") {
        input.style.display = "block";
        texto.style.display = "none";
    } else {
        input.style.display = "none";
        texto.style.display = "block";
    }
}

function mostrarCambioContrasena() {
    const div = document.getElementById("cambio-contrasena");
    div.style.display = div.style.display === "none" ? "block" : "none";
}

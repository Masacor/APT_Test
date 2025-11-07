document.addEventListener('DOMContentLoaded', function () {
    // abrir el formulario inline al presionar el botón "Editar" de acciones
    document.querySelectorAll('.edit-inline-trigger').forEach(function(btn){
        btn.addEventListener('click', function(e){
            const row = e.target.closest('tr');
            if(!row) return;
            const span = row.querySelector('.nombre-text');
            const editForm = row.querySelector('.edit-mode');
            if(span) span.style.display = 'none';
            if(editForm) {
                editForm.style.display = 'flex';
                const input = editForm.querySelector('.input-inline');
                if(input) { input.focus(); input.select(); }
            }
        });
    });

    // cancelar edición inline
    document.querySelectorAll('.cancel-inline').forEach(function(btn){
        btn.addEventListener('click', function(e){
            const row = e.target.closest('tr');
            if(!row) return;
            const span = row.querySelector('.nombre-text');
            const editForm = row.querySelector('.edit-mode');
            if(span) span.style.display = '';
            if(editForm) editForm.style.display = 'none';
            const input = row.querySelector('.input-inline');
            if(input && span) input.value = span.textContent.trim();
        });
    });
});

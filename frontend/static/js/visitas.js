// JavaScript para formulario de crear visita

document.addEventListener('DOMContentLoaded', function() {
    // Validación del formulario
    const form = document.getElementById('crear-visita-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    }

    // Convertir CURP a mayúsculas automáticamente
    const curpInput = document.getElementById('curp');
    if (curpInput) {
        curpInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }

    // Actualizar recursos disponibles automáticamente cada 15 segundos
    setInterval(refreshRecursos, 15000);
});

// Refrescar lista de recursos disponibles (doctores y camas)
function refreshRecursos() {
    console.log('Actualizando recursos disponibles...');

    fetch('/api/recursos-disponibles')
        .then(response => response.json())
        .then(data => {
            // Actualizar select de doctores
            const doctorSelect = document.getElementById('id_doctor');
            if (doctorSelect) {
                const currentValue = doctorSelect.value;

                doctorSelect.innerHTML = '<option value="">Seleccione un doctor...</option>';

                data.doctores.forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor.id;
                    option.textContent = `Dr. ${doctor.nombre} - ${doctor.especialidad}`;
                    if (doctor.id == currentValue) {
                        option.selected = true;
                    }
                    doctorSelect.appendChild(option);
                });
            }

            // Actualizar select de camas
            const camaSelect = document.getElementById('id_cama');
            if (camaSelect) {
                const currentValue = camaSelect.value;

                camaSelect.innerHTML = '<option value="">Seleccione una cama...</option>';

                data.camas.forEach(cama => {
                    const option = document.createElement('option');
                    option.value = cama.id;
                    option.textContent = `Cama ${cama.numero} - Sala ${cama.sala}`;
                    if (cama.id == currentValue) {
                        option.selected = true;
                    }
                    camaSelect.appendChild(option);
                });
            }

            // Actualizar alert de recursos
            const recursosInfo = document.getElementById('recursos-info');
            if (recursosInfo) {
                recursosInfo.textContent = `${data.doctores.length} doctores, ${data.camas.length} camas`;
            }

            // Actualizar estado del alert según disponibilidad
            const recursosAlert = document.getElementById('recursos-alert');
            if (recursosAlert) {
                if (data.doctores.length === 0 || data.camas.length === 0) {
                    recursosAlert.className = 'alert alert-warning';
                } else {
                    recursosAlert.className = 'alert alert-info';
                }
            }

            // Habilitar/deshabilitar botón de submit
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                if (data.doctores.length > 0 && data.camas.length > 0) {
                    submitBtn.disabled = false;
                } else {
                    submitBtn.disabled = true;
                }
            }

            console.log('Recursos actualizados:', data);
        })
        .catch(error => {
            console.error('Error al actualizar recursos:', error);

            const recursosAlert = document.getElementById('recursos-alert');
            if (recursosAlert) {
                recursosAlert.className = 'alert alert-danger';
                const recursosInfo = document.getElementById('recursos-info');
                if (recursosInfo) {
                    recursosInfo.textContent = 'Error al cargar recursos';
                }
            }
        });
}

// Validar CURP mexicano
function validarCURP(curp) {
    const regex = /^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9A-Z][0-9]$/;
    return regex.test(curp);
}

console.log('Visitas.js inicializado');

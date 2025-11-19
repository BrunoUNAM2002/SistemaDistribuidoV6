// Cliente SocketIO Global
const socket = io();

// Estado de conexión
socket.on('connect', () => {
    console.log('✅ Conectado al servidor WebSocket');
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    console.log('❌ Desconectado del servidor WebSocket');
    updateConnectionStatus(false);
});

socket.on('connected', (data) => {
    console.log('Mensaje del servidor:', data.message);
});

// Actualizar indicador de conexión en el footer
function updateConnectionStatus(isConnected) {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
        if (isConnected) {
            statusEl.innerHTML = '<i class="bi bi-wifi text-success"></i> Conectado';
        } else {
            statusEl.innerHTML = '<i class="bi bi-wifi-off text-danger"></i> Desconectado';
        }
    }
}

// Evento: Nueva visita creada
socket.on('visita_creada', (data) => {
    console.log('📋 Nueva visita creada:', data);

    // Mostrar notificación toast
    showToast('success', `Nueva visita creada: ${data.folio}`, `Paciente: ${data.paciente}`);

    // Refrescar métricas del dashboard si estamos en esa página
    if (typeof refreshDashboard === 'function') {
        refreshDashboard();
    }
});

// Evento: Visita cerrada
socket.on('visita_cerrada', (data) => {
    console.log('✅ Visita cerrada:', data);

    // Mostrar notificación toast
    showToast('info', `Visita cerrada: ${data.folio}`, `Doctor: ${data.doctor}`);

    // Refrescar métricas del dashboard
    if (typeof refreshDashboard === 'function') {
        refreshDashboard();
    }
});

// Evento: Métricas actualizadas
socket.on('metricas_actualizadas', (data) => {
    console.log('📊 Métricas actualizadas:', data);

    // Actualizar cards del dashboard
    if (typeof updateMetricsCards === 'function') {
        updateMetricsCards(data);
    }
});

// Función para mostrar notificaciones toast
function showToast(type, title, message) {
    // Colores según tipo
    const bgColors = {
        success: 'bg-success',
        info: 'bg-info',
        warning: 'bg-warning',
        danger: 'bg-danger'
    };

    const bgClass = bgColors[type] || 'bg-primary';

    // Crear toast HTML
    const toastHtml = `
        <div class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    // Crear contenedor de toasts si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }

    // Agregar toast
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    toastContainer.appendChild(toastElement.firstElementChild);

    // Mostrar toast
    const toastBootstrap = new bootstrap.Toast(toastContainer.lastElementChild);
    toastBootstrap.show();

    // Eliminar del DOM después de ocultarse
    toastContainer.lastElementChild.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Solicitar métricas actualizadas (puede ser llamado desde cualquier página)
function requestMetrics() {
    socket.emit('solicitar_metricas');
}

console.log('SocketIO client inicializado');

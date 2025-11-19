// Dashboard JavaScript con Chart.js

let visitasHoraChart = null;
let visitasSalaChart = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadUltimasVisitas();

    // Auto-refresh cada 10 segundos
    setInterval(refreshDashboard, 10000);
});

// Inicializar gráficas
function initCharts() {
    // Gráfica de visitas por hora (línea)
    const ctxHora = document.getElementById('visitasHoraChart');
    if (ctxHora) {
        fetch('/api/visitas-por-hora')
            .then(response => response.json())
            .then(data => {
                visitasHoraChart = new Chart(ctxHora, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Visitas',
                            data: data.values,
                            borderColor: 'rgb(13, 110, 253)',
                            backgroundColor: 'rgba(13, 110, 253, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            },
                            title: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error al cargar visitas por hora:', error));
    }

    // Gráfica de visitas por sala (pie)
    const ctxSala = document.getElementById('visitasSalaChart');
    if (ctxSala) {
        fetch('/api/visitas-por-sala')
            .then(response => response.json())
            .then(data => {
                visitasSalaChart = new Chart(ctxSala, {
                    type: 'pie',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.values,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 206, 86, 0.8)',
                                'rgba(75, 192, 192, 0.8)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error al cargar visitas por sala:', error));
    }
}

// Cargar últimas visitas en la tabla
function loadUltimasVisitas() {
    fetch('/api/ultimas-visitas?limit=10')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('ultimas-visitas-body');
            if (!tbody) return;

            if (data.visitas && data.visitas.length > 0) {
                tbody.innerHTML = data.visitas.map(v => {
                    const estadoBadge = getEstadoBadge(v.estado);
                    const timestamp = new Date(v.timestamp).toLocaleTimeString('es-MX', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });

                    return `
                        <tr>
                            <td><strong>${v.folio}</strong></td>
                            <td>${v.paciente}</td>
                            <td>${v.doctor}</td>
                            <td>Sala ${v.sala}</td>
                            <td>${estadoBadge}</td>
                            <td>${timestamp}</td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">No hay visitas registradas</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error al cargar últimas visitas:', error);
            const tbody = document.getElementById('ultimas-visitas-body');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-danger">Error al cargar datos</td>
                    </tr>
                `;
            }
        });
}

// Refrescar todo el dashboard
function refreshDashboard() {
    console.log('Actualizando dashboard...');

    // Actualizar métricas
    fetch('/api/metricas')
        .then(response => response.json())
        .then(data => {
            updateMetricsCards(data);
        })
        .catch(error => console.error('Error al actualizar métricas:', error));

    // Actualizar gráficas
    updateCharts();

    // Actualizar tabla de visitas
    loadUltimasVisitas();
}

// Actualizar las cards de métricas
function updateMetricsCards(data) {
    const metricVisitas = document.getElementById('metric-visitas');
    const metricDoctores = document.getElementById('metric-doctores');
    const metricCamas = document.getElementById('metric-camas');
    const metricHoy = document.getElementById('metric-hoy');

    if (metricVisitas && data.visitas_activas !== undefined) {
        animateValue(metricVisitas, parseInt(metricVisitas.textContent), data.visitas_activas, 500);
    }

    if (metricDoctores && data.doctores_disponibles !== undefined) {
        animateValue(metricDoctores, parseInt(metricDoctores.textContent), data.doctores_disponibles, 500);
    }

    if (metricCamas && data.camas_disponibles !== undefined) {
        animateValue(metricCamas, parseInt(metricCamas.textContent), data.camas_disponibles, 500);
    }

    if (metricHoy && data.visitas_hoy !== undefined) {
        animateValue(metricHoy, parseInt(metricHoy.textContent), data.visitas_hoy, 500);
    }
}

// Actualizar gráficas
function updateCharts() {
    // Actualizar gráfica de visitas por hora
    fetch('/api/visitas-por-hora')
        .then(response => response.json())
        .then(data => {
            if (visitasHoraChart) {
                visitasHoraChart.data.labels = data.labels;
                visitasHoraChart.data.datasets[0].data = data.values;
                visitasHoraChart.update('none'); // Sin animación para actualización
            }
        })
        .catch(error => console.error('Error al actualizar visitas por hora:', error));

    // Actualizar gráfica de visitas por sala
    fetch('/api/visitas-por-sala')
        .then(response => response.json())
        .then(data => {
            if (visitasSalaChart) {
                visitasSalaChart.data.labels = data.labels;
                visitasSalaChart.data.datasets[0].data = data.values;
                visitasSalaChart.update('none');
            }
        })
        .catch(error => console.error('Error al actualizar visitas por sala:', error));
}

// Refrescar últimas visitas (botón)
function refreshUltimasVisitas() {
    const tbody = document.getElementById('ultimas-visitas-body');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </td>
            </tr>
        `;
    }
    loadUltimasVisitas();
}

// Utilidades
function getEstadoBadge(estado) {
    const badges = {
        'activa': '<span class="badge bg-warning text-dark">Activa</span>',
        'completada': '<span class="badge bg-success">Completada</span>',
        'cancelada': '<span class="badge bg-secondary">Cancelada</span>'
    };
    return badges[estado] || `<span class="badge bg-secondary">${estado}</span>`;
}

// Animar cambio de números
function animateValue(element, start, end, duration) {
    if (start === end) return;

    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

console.log('Dashboard inicializado');

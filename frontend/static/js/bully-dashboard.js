/**
 * Bully Dashboard - Frontend Management for Bully Algorithm Status
 *
 * Maneja la visualización y actualización en tiempo real del sistema
 * de consenso distribuido Bully.
 */

class BullyDashboard {
    constructor() {
        this.socket = null;
        this.currentStatus = null;
        this.clusterStatus = null;
        this.refreshInterval = 5000; // 5 segundos
        this.init();
    }

    init() {
        console.log('[BullyDashboard] Inicializando...');
        this.setupWebSocket();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupWebSocket() {
        // El socket global ya está creado por socketio.js
        if (typeof io !== 'undefined') {
            this.socket = io();

            // Manejar cambios de líder
            this.socket.on('lider_cambio', (data) => {
                console.log('[BullyDashboard] Cambio de líder:', data);
                this.handleLeaderChange(data);
            });

            // Manejar estado de Bully
            this.socket.on('bully_status', (data) => {
                console.log('[BullyDashboard] Estado Bully recibido:', data);
                this.updateStatus(data);
            });

            // Solicitar estado inicial al conectar
            this.socket.on('connect', () => {
                console.log('[BullyDashboard] WebSocket conectado');
                this.socket.emit('solicitar_bully_status');
            });
        } else {
            console.error('[BullyDashboard] Socket.IO no disponible');
        }
    }

    async loadInitialData() {
        try {
            // Cargar estado del nodo
            await this.fetchBullyStatus();

            // Cargar estado del cluster
            await this.fetchClusterStatus();
        } catch (error) {
            console.error('[BullyDashboard] Error cargando datos iniciales:', error);
        }
    }

    async fetchBullyStatus() {
        try {
            const response = await fetch('/api/bully/status');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.updateStatus(data);
        } catch (error) {
            console.error('[BullyDashboard] Error en fetchBullyStatus:', error);
            this.showError('No se pudo obtener el estado del nodo');
        }
    }

    async fetchClusterStatus() {
        try {
            const response = await fetch('/api/bully/cluster');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.clusterStatus = data;
            this.renderCluster(data);
        } catch (error) {
            console.error('[BullyDashboard] Error en fetchClusterStatus:', error);
            this.showError('No se pudo obtener el estado del cluster');
        }
    }

    updateStatus(status) {
        if (!status || status.error) {
            console.warn('[BullyDashboard] Estado con error:', status);
            return;
        }

        this.currentStatus = status;
        this.renderStatus();
    }

    renderStatus() {
        const status = this.currentStatus;
        if (!status) return;

        // Actualizar Node ID
        const nodeIdEl = document.getElementById('bully-node-id');
        if (nodeIdEl) nodeIdEl.textContent = status.node_id;

        // Actualizar Estado (Líder o Seguidor)
        const stateEl = document.getElementById('bully-state');
        if (stateEl) {
            const isLeader = status.is_leader;
            const badgeClass = isLeader ? 'badge-warning' : 'badge-info';
            const stateText = isLeader ? '👑 LÍDER' : 'SEGUIDOR';
            stateEl.innerHTML = `<span class="badge ${badgeClass}">${stateText}</span>`;
        }

        // Actualizar Líder Actual
        const leaderEl = document.getElementById('bully-leader');
        if (leaderEl) {
            if (status.current_leader !== null) {
                leaderEl.innerHTML = `Nodo ${status.current_leader} ${status.is_leader ? '(Yo)' : ''}`;
            } else {
                leaderEl.innerHTML = '<span class="text-muted">Sin líder</span>';
            }
        }

        // Actualizar Último Heartbeat
        const heartbeatEl = document.getElementById('bully-heartbeat');
        if (heartbeatEl) {
            const time = Math.round(status.time_since_last_heartbeat || 0);
            heartbeatEl.textContent = `${time}s atrás`;
        }
    }

    renderCluster(data) {
        const container = document.getElementById('cluster-nodes');
        if (!container || !data || !data.nodes) return;

        const nodes = data.nodes;
        const html = nodes.map(node => this.createNodeCard(node)).join('');
        container.innerHTML = html;
    }

    createNodeCard(node) {
        const isLeader = node.is_leader;
        const isCurrent = node.is_current;
        const state = node.state;

        // Clase CSS según estado
        let cardClass = 'node-card';
        if (isLeader) cardClass += ' node-leader';
        if (isCurrent) cardClass += ' node-current';

        // Icon según estado
        const icon = isLeader ? '👑' : (state === 'follower' ? '📡' : '❓');

        return `
            <div class="${cardClass}">
                <div class="node-icon">${icon}</div>
                <div class="node-title">Nodo ${node.id}</div>
                <div class="node-state">${this.getStateLabel(state)}</div>
                ${isCurrent ? '<div class="node-badge">Este nodo</div>' : ''}
            </div>
        `;
    }

    getStateLabel(state) {
        const labels = {
            'leader': 'Líder',
            'follower': 'Seguidor',
            'unknown': 'Desconocido'
        };
        return labels[state] || state;
    }

    handleLeaderChange(data) {
        // Mostrar notificación toast
        if (typeof showToast === 'function') {
            showToast('info', 'Cambio de Líder',
                     `Nodo ${data.nuevo_lider} es el nuevo líder (term ${data.term})`);
        } else {
            console.log(`[BullyDashboard] Nuevo líder: Nodo ${data.nuevo_lider}`);
        }

        // Solicitar actualización de estado
        if (this.socket) {
            this.socket.emit('solicitar_bully_status');
        }

        // Actualizar vista del cluster
        this.fetchClusterStatus();
    }

    showError(message) {
        console.error('[BullyDashboard]', message);
        // Opcional: mostrar en UI
    }

    startAutoRefresh() {
        // Actualizar cada 5 segundos
        setInterval(() => {
            this.fetchBullyStatus();
            this.fetchClusterStatus();
        }, this.refreshInterval);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('[BullyDashboard] DOM listo, inicializando...');
    window.bullyDashboard = new BullyDashboard();
});

// También exportar para uso manual
window.BullyDashboard = BullyDashboard;

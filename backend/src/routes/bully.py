# backend/routes/bully.py

from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from config import Config
import logging
import time

bully_bp = Blueprint('bully_routes', __name__)
logger = logging.getLogger(__name__)

@bully_bp.route('/status')
@login_required
def get_status():
    """
    Obtiene el estado actual del sistema Bully para este nodo.
    
    Returns:
        JSON con el estado del nodo:
        {
            'node_id': int,
            'state': 'follower' | 'leader',
            'current_leader': int | None,
            'is_leader': bool,
            'time_since_last_heartbeat': float
        }
    """
    try:
        if hasattr(current_app, 'bully_manager') and current_app.bully_manager:
            status = current_app.bully_manager.get_status()
            return jsonify(status), 200
        else:
            return jsonify({
                'error': 'Bully system not initialized',
                'node_id': Config.NODE_ID,
                'state': 'unknown',
                'current_leader': None,
                'is_leader': False
            }), 503
    except Exception as e:
        logger.error(f'Error getting Bully status: {e}')
        return jsonify({'error': str(e)}), 500


@bully_bp.route('/cluster')
@login_required
def get_cluster_status():
    """
    Obtiene el estado de todos los nodos del cluster.
    
    Returns:
        JSON con información de todos los nodos:
        {
            'nodes': [
                {
                    'id': int,
                    'url': str,
                    'tcp_port': int,
                    'is_current': bool,
                    'is_leader': bool,
                    'state': 'leader' | 'follower' | 'unknown'
                }
            ],
            'cluster_size': int,
            'current_leader': int | None
        }
    """
    try:
        cluster_status = []
        current_leader = None
        
        # Obtener ID del líder actual
        if hasattr(current_app, 'bully_manager') and current_app.bully_manager:
            current_leader = current_app.bully_manager.get_current_leader()
        
        # Construir información de cada nodo
        for nodo in Config.OTROS_NODOS:
            node_id = nodo['id']
            is_leader = (node_id == current_leader)
            is_current = (node_id == Config.NODE_ID)
            
            # Determinar estado del nodo
            if is_current:
                # Estado de este nodo (sabemos con certeza)
                if hasattr(current_app, 'bully_manager') and current_app.bully_manager:
                    state = current_app.bully_manager.get_status().get('state', 'unknown')
                else:
                    state = 'unknown'
            elif is_leader:
                state = 'leader'
            else:
                state = 'follower'  # Asumimos follower si no es líder
            
            node_info = {
                'id': node_id,
                'url': nodo['url'],
                'tcp_port': nodo['tcp_port'],
                'is_current': is_current,
                'is_leader': is_leader,
                'state': state
            }
            cluster_status.append(node_info)
        
        return jsonify({
            'nodes': cluster_status,
            'cluster_size': len(Config.OTROS_NODOS),
            'current_leader': current_leader,
            'timestamp': time.time()
        }), 200
        
    except Exception as e:
        logger.error(f'Error getting cluster status: {e}')
        return jsonify({'error': str(e)}), 500


@bully_bp.route('/health')
@login_required
def get_health():
    """
    Endpoint de health check para el sistema Bully.
    
    Returns:
        JSON con estado de salud básico
    """
    try:
        healthy = hasattr(current_app, 'bully_manager') and current_app.bully_manager is not None
        
        if healthy:
            status = current_app.bully_manager.get_status()
            return jsonify({
                'healthy': True,
                'node_id': status.get('node_id'),
                'is_leader': status.get('is_leader', False),
                'current_leader': status.get('current_leader')
            }), 200
        else:
            return jsonify({
                'healthy': False,
                'message': 'Bully manager not initialized'
            }), 503
            
    except Exception as e:
        logger.error(f'Error in health check: {e}')
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500

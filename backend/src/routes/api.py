from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import (get_metricas_dashboard, get_doctores_disponibles, get_camas_disponibles,
                   get_visitas_activas, VisitaEmergencia, Sala)
from config import Config
from datetime import datetime, timedelta
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/metricas')
@login_required
def metricas():
    """Retorna métricas actualizadas para el dashboard"""
    try:
        data = get_metricas_dashboard(id_sala=Config.NODE_ID)
        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener métricas: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/recursos-disponibles')
@login_required
def recursos_disponibles():
    """Retorna doctores y camas disponibles para crear visita"""
    try:
        id_sala = request.args.get('sala', Config.NODE_ID, type=int)

        doctores = get_doctores_disponibles(id_sala=id_sala)
        camas = get_camas_disponibles(id_sala=id_sala)

        data = {
            'doctores': [
                {
                    'id': d.id_doctor,
                    'nombre': d.nombre,
                    'especialidad': d.especialidad,
                    'sala': d.id_sala
                }
                for d in doctores
            ],
            'camas': [
                {
                    'id': c.id_cama,
                    'numero': c.numero,
                    'sala': c.id_sala
                }
                for c in camas
            ]
        }

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener recursos: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/visitas-activas')
@login_required
def visitas_activas():
    """Retorna visitas activas (opcionalmente por sala o doctor)"""
    try:
        id_sala = request.args.get('sala', type=int)
        id_doctor = request.args.get('doctor', type=int)

        visitas = get_visitas_activas(id_doctor=id_doctor, id_sala=id_sala)

        data = {
            'visitas': [v.to_dict() for v in visitas],
            'total': len(visitas)
        }

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener visitas activas: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/visitas-por-hora')
@login_required
def visitas_por_hora():
    """Retorna datos para gráfica de visitas por hora (últimas 24 horas)"""
    try:
        ahora = datetime.utcnow()
        hace_24h = ahora - timedelta(hours=24)

        visitas = VisitaEmergencia.query.filter(
            VisitaEmergencia.timestamp >= hace_24h
        ).all()

        # Agrupar por hora
        visitas_por_hora = {}
        for i in range(24):
            hora = (ahora - timedelta(hours=23-i)).replace(minute=0, second=0, microsecond=0)
            visitas_por_hora[hora.strftime('%H:%M')] = 0

        for visita in visitas:
            hora_str = visita.timestamp.strftime('%H:00')
            if hora_str in visitas_por_hora:
                visitas_por_hora[hora_str] += 1

        data = {
            'labels': list(visitas_por_hora.keys()),
            'values': list(visitas_por_hora.values())
        }

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener visitas por hora: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/visitas-por-sala')
@login_required
def visitas_por_sala():
    """Retorna distribución de visitas activas por sala para gráfica pie"""
    try:
        salas = Sala.query.all()
        data = {
            'labels': [f'Sala {s.numero}' for s in salas],
            'values': []
        }

        for sala in salas:
            count = VisitaEmergencia.query.filter_by(
                estado='activa',
                id_sala=sala.id_sala
            ).count()
            data['values'].append(count)

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener visitas por sala: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/estado-nodos')
@login_required
def estado_nodos():
    """Retorna estado de todos los nodos (activos/inactivos)"""
    try:
        salas = Sala.query.all()

        data = {
            'nodos': [
                {
                    'id': s.id_sala,
                    'numero': s.numero,
                    'ip': s.ip_address,
                    'puerto': s.puerto,
                    'activo': s.activa,
                    'es_maestro': s.es_maestro
                }
                for s in salas
            ],
            'total_activos': sum(1 for s in salas if s.activa)
        }

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener estado de nodos: {str(e)}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ultimas-visitas')
@login_required
def ultimas_visitas():
    """Retorna las últimas 10 visitas creadas"""
    try:
        limit = request.args.get('limit', 10, type=int)

        visitas = VisitaEmergencia.query.order_by(
            VisitaEmergencia.timestamp.desc()
        ).limit(limit).all()

        data = {
            'visitas': [v.to_dict() for v in visitas]
        }

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error al obtener últimas visitas: {str(e)}')
        return jsonify({'error': str(e)}), 500

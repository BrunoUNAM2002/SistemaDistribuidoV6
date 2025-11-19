from flask import Blueprint, render_template, request
from flask_login import login_required
from auth import role_required
from models import Doctor, Paciente, Cama, VisitaEmergencia, TrabajadorSocial, Sala
from config import Config
import logging

consultas_bp = Blueprint('consultas', __name__)
logger = logging.getLogger(__name__)


@consultas_bp.route('/global')
@login_required
@role_required('admin')
def global_view():
    """Vista global para administradores - Consulta todos los recursos"""

    # Obtener filtros
    filtro_sala = request.args.get('sala', type=int)
    filtro_disponible = request.args.get('disponible')

    # Doctores
    query_doctores = Doctor.query
    if filtro_sala:
        query_doctores = query_doctores.filter_by(id_sala=filtro_sala)
    if filtro_disponible == '1':
        query_doctores = query_doctores.filter_by(disponible=True)
    elif filtro_disponible == '0':
        query_doctores = query_doctores.filter_by(disponible=False)

    doctores = query_doctores.all()

    # Pacientes
    pacientes = Paciente.query.filter_by(activo=1).all()

    # Camas
    query_camas = Cama.query
    if filtro_sala:
        query_camas = query_camas.filter_by(id_sala=filtro_sala)
    camas = query_camas.all()

    # Trabajadores Sociales
    query_trabajadores = TrabajadorSocial.query
    if filtro_sala:
        query_trabajadores = query_trabajadores.filter_by(id_sala=filtro_sala)
    trabajadores = query_trabajadores.all()

    # Visitas
    query_visitas = VisitaEmergencia.query
    if filtro_sala:
        query_visitas = query_visitas.filter_by(id_sala=filtro_sala)
    visitas = query_visitas.order_by(VisitaEmergencia.timestamp.desc()).limit(50).all()

    # Salas
    salas = Sala.query.all()

    return render_template(
        'consultas.html',
        doctores=doctores,
        pacientes=pacientes,
        camas=camas,
        trabajadores=trabajadores,
        visitas=visitas,
        salas=salas,
        filtro_sala=filtro_sala
    )


@consultas_bp.route('/doctores')
@login_required
def doctores():
    """Lista de todos los doctores"""
    id_sala = request.args.get('sala', type=int)

    query = Doctor.query
    if id_sala:
        query = query.filter_by(id_sala=id_sala)

    doctores_list = query.all()

    return render_template('doctores.html', doctores=doctores_list, sala_filtro=id_sala)


@consultas_bp.route('/pacientes')
@login_required
def pacientes():
    """Lista de todos los pacientes"""
    busqueda = request.args.get('q', '')

    query = Paciente.query.filter_by(activo=1)

    if busqueda:
        query = query.filter(Paciente.nombre.like(f'%{busqueda}%'))

    pacientes_list = query.all()

    return render_template('pacientes.html', pacientes=pacientes_list, busqueda=busqueda)


@consultas_bp.route('/camas')
@login_required
def camas():
    """Lista de todas las camas"""
    id_sala = request.args.get('sala', type=int)
    ocupadas = request.args.get('ocupadas')

    query = Cama.query
    if id_sala:
        query = query.filter_by(id_sala=id_sala)
    if ocupadas == '1':
        query = query.filter_by(ocupada=True)
    elif ocupadas == '0':
        query = query.filter_by(ocupada=False)

    camas_list = query.all()

    return render_template('camas.html', camas=camas_list, sala_filtro=id_sala)

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from auth import role_required, get_user_info
from models import (db, VisitaEmergencia, Paciente, Doctor, Cama, TrabajadorSocial,
                   get_doctores_disponibles, get_camas_disponibles, get_visitas_activas)
from config import Config
from datetime import datetime
import logging

visitas_bp = Blueprint('visitas', __name__)
logger = logging.getLogger(__name__)


@visitas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('trabajador_social')
def crear_visita():
    """Formulario para crear una nueva visita de emergencia"""

    if request.method == 'POST':
        try:
            # 1. Datos del paciente
            nombre = request.form.get('nombre')
            edad = request.form.get('edad')
            sexo = request.form.get('sexo')
            curp = request.form.get('curp')
            telefono = request.form.get('telefono')
            contacto_emergencia = request.form.get('contacto_emergencia')
            sintomas = request.form.get('sintomas')

            # Validar campos requeridos
            if not all([nombre, edad, sexo, sintomas]):
                flash('Faltan campos requeridos', 'danger')
                return redirect(url_for('visitas.crear_visita'))

            # 2. Buscar paciente existente por CURP o crear nuevo
            paciente = None
            if curp:
                paciente = Paciente.query.filter_by(curp=curp).first()

            if not paciente:
                paciente = Paciente(
                    nombre=nombre,
                    edad=int(edad),
                    sexo=sexo,
                    curp=curp if curp else None,
                    telefono=telefono,
                    contacto_emergencia=contacto_emergencia,
                    activo=1
                )
                db.session.add(paciente)
                db.session.flush()  # Para obtener el id_paciente

            # 3. Obtener ID del trabajador social actual
            user_info = get_user_info(current_user)
            id_trabajador = user_info.get('id_relacionado') if user_info else None

            if not id_trabajador:
                flash('Error: No se pudo identificar al trabajador social', 'danger')
                db.session.rollback()
                return redirect(url_for('visitas.crear_visita'))

            # 4. Asignar recursos (doctor y cama) - Prioridad a la sala actual
            id_doctor_form = request.form.get('id_doctor')
            id_cama_form = request.form.get('id_cama')

            doctor = Doctor.query.get(id_doctor_form) if id_doctor_form else None
            cama = Cama.query.get(id_cama_form) if id_cama_form else None

            # Verificar disponibilidad
            if not doctor or not doctor.disponible:
                flash('El doctor seleccionado no está disponible', 'warning')
                db.session.rollback()
                return redirect(url_for('visitas.crear_visita'))

            if not cama or cama.ocupada:
                flash('La cama seleccionada no está disponible', 'warning')
                db.session.rollback()
                return redirect(url_for('visitas.crear_visita'))

            # 5. Crear la visita (el trigger se encargará de generar el folio)
            visita = VisitaEmergencia(
                id_paciente=paciente.id_paciente,
                id_doctor=doctor.id_doctor,
                id_cama=cama.id_cama,
                id_trabajador=id_trabajador,
                id_sala=Config.NODE_ID,
                sintomas=sintomas,
                estado='activa',
                timestamp=datetime.utcnow()
            )

            db.session.add(visita)
            db.session.commit()

            # El trigger ya generó el folio, recargar para obtenerlo
            db.session.refresh(visita)

            # 6. Notificar vía WebSocket
            if hasattr(current_app, 'notificar_visita_creada'):
                current_app.notificar_visita_creada({
                    'folio': visita.folio,
                    'paciente': paciente.nombre,
                    'doctor': doctor.nombre,
                    'sala': Config.NODE_ID
                })

            flash(f'Visita creada exitosamente. Folio: {visita.folio}', 'success')
            logger.info(f'Visita creada: {visita.folio} - Paciente: {paciente.nombre}')

            return redirect(url_for('visitas.crear_visita'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear visita: {str(e)}', 'danger')
            logger.error(f'Error al crear visita: {str(e)}')
            return redirect(url_for('visitas.crear_visita'))

    # GET: Mostrar formulario
    doctores_disponibles = get_doctores_disponibles(id_sala=Config.NODE_ID)
    camas_disponibles = get_camas_disponibles(id_sala=Config.NODE_ID)

    return render_template(
        'crear_visita.html',
        doctores=doctores_disponibles,
        camas=camas_disponibles
    )


@visitas_bp.route('/mis-visitas')
@login_required
@role_required('doctor')
def mis_visitas():
    """Vista de visitas asignadas al doctor actual"""
    user_info = get_user_info(current_user)
    id_doctor = user_info.get('id_relacionado') if user_info else None

    if not id_doctor:
        flash('Error: No se pudo identificar al doctor', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener visitas activas del doctor
    visitas = get_visitas_activas(id_doctor=id_doctor)

    return render_template('mis_visitas.html', visitas=visitas)


@visitas_bp.route('/<folio>/cerrar', methods=['POST'])
@login_required
@role_required('doctor')
def cerrar_visita(folio):
    """Cerrar una visita de emergencia"""
    try:
        visita = VisitaEmergencia.query.filter_by(folio=folio).first()

        if not visita:
            flash('Visita no encontrada', 'danger')
            return redirect(url_for('visitas.mis_visitas'))

        # Verificar que el doctor actual es el asignado
        user_info = get_user_info(current_user)
        id_doctor = user_info.get('id_relacionado') if user_info else None

        if visita.id_doctor != id_doctor and current_user.rol != 'admin':
            flash('No tienes permiso para cerrar esta visita', 'danger')
            return redirect(url_for('visitas.mis_visitas'))

        # Obtener diagnóstico del formulario
        diagnostico = request.form.get('diagnostico', '')

        # Actualizar visita
        visita.estado = 'completada'
        visita.diagnostico = diagnostico
        visita.fecha_cierre = datetime.utcnow()

        # El trigger liberará automáticamente el doctor y la cama
        db.session.commit()

        # Notificar vía WebSocket
        if hasattr(current_app, 'notificar_visita_cerrada'):
            current_app.notificar_visita_cerrada({
                'folio': visita.folio,
                'doctor': visita.doctor.nombre,
                'sala': visita.id_sala
            })

        flash(f'Visita {folio} cerrada exitosamente', 'success')
        logger.info(f'Visita cerrada: {folio} - Doctor: {visita.doctor.nombre}')

        return redirect(url_for('visitas.mis_visitas'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al cerrar visita: {str(e)}', 'danger')
        logger.error(f'Error al cerrar visita {folio}: {str(e)}')
        return redirect(url_for('visitas.mis_visitas'))


@visitas_bp.route('/todas')
@login_required
def todas_visitas():
    """Ver todas las visitas (filtrable por estado)"""
    estado = request.args.get('estado', 'activa')

    query = VisitaEmergencia.query

    if estado and estado != 'todas':
        query = query.filter_by(estado=estado)

    visitas = query.order_by(VisitaEmergencia.timestamp.desc()).limit(100).all()

    return render_template('todas_visitas.html', visitas=visitas, estado=estado)

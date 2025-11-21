from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import LoginManager, current_user
from models import Usuario, db

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'


@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario por ID para Flask-Login"""
    return Usuario.query.get(int(user_id))


def role_required(roles):
    """
    Decorador para requerir roles específicos.

    Uso:
        @role_required('admin')
        @role_required(['doctor', 'admin'])
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))

            if current_user.rol not in roles:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for('dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def init_default_users():
    """
    Inicializa usuarios por defecto si no existen.
    Debe llamarse al iniciar la aplicación.
    """
    # Admin por defecto
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            rol='admin',
            activo=True
        )
        admin.set_password('admin123')  # Cambiar en producción
        db.session.add(admin)

    # Usuarios de prueba para cada rol
    usuarios_prueba = [
        {'username': 'doctor1', 'password': 'doc123', 'rol': 'doctor', 'id_relacionado': 1},
        {'username': 'doctor2', 'password': 'doc123', 'rol': 'doctor', 'id_relacionado': 2},
        {'username': 'trabajador1', 'password': 'trab123', 'rol': 'trabajador_social', 'id_relacionado': 1},
        {'username': 'trabajador2', 'password': 'trab123', 'rol': 'trabajador_social', 'id_relacionado': 2},
    ]

    for user_data in usuarios_prueba:
        existing = Usuario.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = Usuario(
                username=user_data['username'],
                rol=user_data['rol'],
                id_relacionado=user_data.get('id_relacionado'),
                activo=True
            )
            user.set_password(user_data['password'])
            db.session.add(user)

    db.session.commit()
    print("Usuarios por defecto inicializados.")


def get_user_info(user):
    """
    Obtiene información extendida del usuario según su rol.
    Retorna un diccionario con datos adicionales del doctor o trabajador social.
    """
    if not user or not user.is_authenticated:
        return None

    info = {
        'id': user.id,
        'username': user.username,
        'rol': user.rol,
        'rol_display': get_rol_display(user.rol)
    }

    if user.rol == 'doctor' and user.id_relacionado:
        from models import Doctor
        doctor = Doctor.query.get(user.id_relacionado)
        if doctor:
            info['nombre'] = doctor.nombre
            info['especialidad'] = doctor.especialidad
            info['sala_id'] = doctor.id_sala
            info['disponible'] = doctor.disponible

    elif user.rol == 'trabajador_social' and user.id_relacionado:
        from models import TrabajadorSocial
        trabajador = TrabajadorSocial.query.get(user.id_relacionado)
        if trabajador:
            info['nombre'] = trabajador.nombre
            info['sala_id'] = trabajador.id_sala

    return info


def get_rol_display(rol):
    """Retorna el nombre del rol para mostrar en la UI"""
    roles_display = {
        'admin': 'Administrador',
        'doctor': 'Doctor',
        'trabajador_social': 'Trabajador Social'
    }
    return roles_display.get(rol, rol)


def can_access_sala(user, id_sala):
    """
    Verifica si un usuario puede acceder a recursos de una sala específica.
    Los admins tienen acceso a todas las salas.
    Doctores y trabajadores sociales solo a su sala asignada.
    """
    if not user or not user.is_authenticated:
        return False

    if user.rol == 'admin':
        return True

    user_info = get_user_info(user)
    if user_info and 'sala_id' in user_info:
        return user_info['sala_id'] == id_sala

    return False

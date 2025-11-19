from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from config import Config
from models import db, Usuario, get_metricas_dashboard
from auth import login_manager, init_default_users, get_user_info
import logging

# Crear aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
login_manager.init_app(app)
socketio = SocketIO(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'])

# Configurar logging
logging.basicConfig(level=app.config['LOG_LEVEL'])
logger = logging.getLogger(__name__)


# ============================================================================
# CONTEXT PROCESSORS (Variables disponibles en todos los templates)
# ============================================================================

@app.context_processor
def inject_global_vars():
    """Inyecta variables globales en todos los templates"""
    return {
        'node_id': Config.NODE_ID,
        'flask_port': Config.FLASK_PORT,
        'user_info': get_user_info(current_user) if current_user.is_authenticated else None
    }


# ============================================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(username=username, activo=True).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Bienvenido, {username}!', 'success')
            logger.info(f'Usuario {username} ({user.rol}) inició sesión en nodo {Config.NODE_ID}')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            logger.warning(f'Intento de login fallido para usuario: {username}')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    username = current_user.username
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    logger.info(f'Usuario {username} cerró sesión')
    return redirect(url_for('login'))


# ============================================================================
# RUTA PRINCIPAL (DASHBOARD)
# ============================================================================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con métricas (OPTIMIZADO)"""
    metricas = get_metricas_dashboard(id_sala=Config.NODE_ID)

    # Información del nodo actual
    nodo_info = Config.get_info_nodo_actual()

    return render_template(
        'dashboard_lite.html',  # OPTIMIZED: Usar versión lite sin Bootstrap
        metricas=metricas,
        nodo=nodo_info,
        otros_nodos=Config.get_otros_nodos_activos()
    )


# ============================================================================
# IMPORTAR BLUEPRINTS (rutas modulares)
# ============================================================================

# Importamos las rutas después de crear app para evitar imports circulares
from routes.visitas import visitas_bp
from routes.consultas import consultas_bp
from routes.api import api_bp

app.register_blueprint(visitas_bp, url_prefix='/visitas')
app.register_blueprint(consultas_bp, url_prefix='/consultas')
app.register_blueprint(api_bp, url_prefix='/api')


# ============================================================================
# EVENTOS WEBSOCKET
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Cliente conectado a WebSocket"""
    logger.info(f'Cliente WebSocket conectado - SID: {request.sid}')
    emit('connected', {'message': f'Conectado al nodo {Config.NODE_ID}'})


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f'Cliente WebSocket desconectado - SID: {request.sid}')


@socketio.on('solicitar_metricas')
def handle_solicitar_metricas():
    """Cliente solicita métricas actualizadas"""
    metricas = get_metricas_dashboard(id_sala=Config.NODE_ID)
    emit('metricas_actualizadas', metricas)


# Evento global: emitir cuando se crea una visita
def notificar_visita_creada(visita_data):
    """Notifica a todos los clientes conectados que se creó una visita"""
    socketio.emit('visita_creada', visita_data, broadcast=True)
    logger.info(f'Notificación broadcast: Visita creada - {visita_data.get("folio")}')


# Evento global: emitir cuando se cierra una visita
def notificar_visita_cerrada(visita_data):
    """Notifica a todos los clientes conectados que se cerró una visita"""
    socketio.emit('visita_cerrada', visita_data, broadcast=True)
    logger.info(f'Notificación broadcast: Visita cerrada - {visita_data.get("folio")}')


# Exportar funciones de notificación para usarlas en otros módulos
app.notificar_visita_creada = notificar_visita_creada
app.notificar_visita_cerrada = notificar_visita_cerrada


# ============================================================================
# INICIALIZACIÓN DE LA BASE DE DATOS
# ============================================================================

def init_db():
    """Inicializa la base de datos y usuarios por defecto"""
    with app.app_context():
        db.create_all()
        init_default_users()
        logger.info('Base de datos inicializada correctamente')


# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Página no encontrada"""
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(error):
    """Acceso prohibido"""
    return render_template('403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    """Error interno del servidor"""
    db.session.rollback()
    logger.error(f'Error 500: {error}')
    return render_template('500.html'), 500


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    # Inicializar BD si no existe
    init_db()

    # Información de inicio
    logger.info('='*60)
    logger.info(f'🏥 Sistema de Emergencias Médicas - Nodo {Config.NODE_ID}')
    logger.info(f'🌐 Flask corriendo en http://localhost:{Config.FLASK_PORT}')
    logger.info(f'📡 Puerto TCP: {Config.TCP_PORT}')
    logger.info(f'💾 Base de datos: {Config.SQLALCHEMY_DATABASE_URI}')
    logger.info('='*60)

    # Iniciar servidor Flask con SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=True,
        use_reloader=True,
        allow_unsafe_werkzeug=True  # Para desarrollo
    )

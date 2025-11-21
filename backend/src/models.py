from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class Sala(db.Model):
    __tablename__ = 'SALAS'

    id_sala = db.Column('id_sala', db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(50))
    puerto = db.Column(db.Integer)
    es_maestro = db.Column(db.Boolean, default=False)
    activa = db.Column(db.Boolean, default=True)

    # Relaciones
    doctores = db.relationship('Doctor', backref='sala', lazy=True)
    trabajadores = db.relationship('TrabajadorSocial', backref='sala', lazy=True)
    camas = db.relationship('Cama', backref='sala', lazy=True)
    visitas = db.relationship('VisitaEmergencia', backref='sala', lazy=True)

    def __repr__(self):
        return f'<Sala {self.numero}>'


class Paciente(db.Model):
    __tablename__ = 'PACIENTES'

    id_paciente = db.Column('id_paciente', db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    edad = db.Column(db.Integer)
    sexo = db.Column(db.String(1))  # 'M' o 'F'
    curp = db.Column(db.String(18), unique=True)
    telefono = db.Column(db.String(20))
    contacto_emergencia = db.Column(db.String(200))
    activo = db.Column(db.Integer, default=1, nullable=False)

    # Relaciones
    visitas = db.relationship('VisitaEmergencia', backref='paciente', lazy=True)

    def __repr__(self):
        return f'<Paciente {self.nombre}>'


class Doctor(db.Model):
    __tablename__ = 'DOCTORES'

    id_doctor = db.Column('id_doctor', db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    especialidad = db.Column(db.String(100))
    id_sala = db.Column(db.Integer, db.ForeignKey('SALAS.id_sala'), nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    visitas = db.relationship('VisitaEmergencia', backref='doctor', lazy=True)

    def __repr__(self):
        return f'<Doctor {self.nombre} - {self.especialidad}>'


class TrabajadorSocial(db.Model):
    __tablename__ = 'TRABAJADORES_SOCIALES'

    id_trabajador = db.Column('id_trabajador', db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('SALAS.id_sala'), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    visitas = db.relationship('VisitaEmergencia', backref='trabajador_social', lazy=True)

    def __repr__(self):
        return f'<TrabajadorSocial {self.nombre}>'


class Cama(db.Model):
    __tablename__ = 'CAMAS'

    id_cama = db.Column('id_cama', db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('SALAS.id_sala'), nullable=False)
    ocupada = db.Column(db.Boolean, default=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('PACIENTES.id_paciente'))

    # Relaciones
    visitas = db.relationship('VisitaEmergencia', backref='cama', lazy=True)
    paciente_actual = db.relationship('Paciente', foreign_keys=[id_paciente])

    def __repr__(self):
        return f'<Cama {self.numero} - Sala {self.id_sala}>'


class VisitaEmergencia(db.Model):
    __tablename__ = 'VISITAS_EMERGENCIA'

    id_visita = db.Column('id_visita', db.Integer, primary_key=True)
    folio = db.Column(db.String(50), unique=True)  # Generado por trigger
    id_paciente = db.Column(db.Integer, db.ForeignKey('PACIENTES.id_paciente'), nullable=False)
    id_doctor = db.Column(db.Integer, db.ForeignKey('DOCTORES.id_doctor'), nullable=False)
    id_cama = db.Column(db.Integer, db.ForeignKey('CAMAS.id_cama'), nullable=False)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('TRABAJADORES_SOCIALES.id_trabajador'), nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('SALAS.id_sala'), nullable=False)
    sintomas = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    estado = db.Column(db.String(20), default='activa')  # 'activa', 'completada', 'cancelada'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime)

    def __repr__(self):
        return f'<VisitaEmergencia {self.folio} - {self.estado}>'

    def to_dict(self):
        """Convierte la visita a diccionario para JSON"""
        return {
            'id_visita': self.id_visita,
            'folio': self.folio,
            'paciente': self.paciente.nombre,
            'doctor': self.doctor.nombre,
            'cama': self.cama.numero,
            'sala': self.sala.numero,
            'sintomas': self.sintomas,
            'estado': self.estado,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'fecha_cierre': self.fecha_cierre.isoformat() if self.fecha_cierre else None
        }


class Consecutivo(db.Model):
    __tablename__ = 'CONSECUTIVOS'

    id = db.Column(db.Integer, primary_key=True)
    id_sala = db.Column(db.Integer, db.ForeignKey('SALAS.id_sala'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    consecutivo = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Consecutivo Sala {self.id_sala} - {self.fecha}: {self.consecutivo}>'


class Usuario(UserMixin, db.Model):
    """Modelo para autenticación con Flask-Login"""
    __tablename__ = 'USUARIOS'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(30), nullable=False)  # 'doctor', 'trabajador_social', 'admin'
    id_relacionado = db.Column(db.Integer)  # id_doctor o id_trabajador según rol
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Hash de la contraseña con bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def get_id(self):
        """Requerido por Flask-Login"""
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.username} - {self.rol}>'


# Funciones de utilidad para queries comunes

def get_doctores_disponibles(id_sala=None):
    """Obtiene doctores disponibles, opcionalmente filtrados por sala"""
    query = Doctor.query.filter_by(disponible=True, activo=True)
    if id_sala:
        query = query.filter_by(id_sala=id_sala)
    return query.all()


def get_camas_disponibles(id_sala=None):
    """Obtiene camas disponibles, opcionalmente filtradas por sala"""
    query = Cama.query.filter_by(ocupada=False)
    if id_sala:
        query = query.filter_by(id_sala=id_sala)
    return query.all()


def get_visitas_activas(id_doctor=None, id_sala=None):
    """Obtiene visitas activas, opcionalmente filtradas por doctor o sala"""
    query = VisitaEmergencia.query.filter_by(estado='activa')
    if id_doctor:
        query = query.filter_by(id_doctor=id_doctor)
    if id_sala:
        query = query.filter_by(id_sala=id_sala)
    return query.order_by(VisitaEmergencia.timestamp.desc()).all()


def get_metricas_dashboard(id_sala=None):
    """Obtiene métricas para el dashboard (OPTIMIZADO - UNA SOLA QUERY)"""
    from sqlalchemy import func, case, and_

    # Query única optimizada con agregaciones
    hoy = datetime.utcnow().date()

    # Subquery para visitas
    visitas_stats = db.session.query(
        func.count().filter(VisitaEmergencia.estado == 'activa').label('visitas_activas'),
        func.count().filter(func.date(VisitaEmergencia.timestamp) == hoy).label('visitas_hoy'),
        func.count().filter(and_(
            VisitaEmergencia.estado == 'activa',
            VisitaEmergencia.id_sala == id_sala if id_sala else True
        )).label('visitas_activas_sala')
    ).first()

    # Counts optimizados
    doctores_disponibles = Doctor.query.filter_by(disponible=True, activo=True).count()
    camas_disponibles = Cama.query.filter_by(ocupada=False).count()

    metricas = {
        'visitas_activas': visitas_stats.visitas_activas or 0,
        'doctores_disponibles': doctores_disponibles,
        'camas_disponibles': camas_disponibles,
        'visitas_hoy': visitas_stats.visitas_hoy or 0
    }

    if id_sala:
        metricas['visitas_activas_sala'] = visitas_stats.visitas_activas_sala or 0
        metricas['doctores_sala'] = Doctor.query.filter_by(
            id_sala=id_sala, disponible=True, activo=True
        ).count()
        metricas['camas_sala'] = Cama.query.filter_by(
            id_sala=id_sala, ocupada=False
        ).count()

    return metricas

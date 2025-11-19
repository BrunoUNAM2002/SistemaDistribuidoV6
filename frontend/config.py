import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base para la aplicación Flask"""

    # Identificador del nodo (Sala 1, 2, 3, 4)
    NODE_ID = int(os.getenv('NODE_ID', '1'))

    # Secret key para sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Base de datos SQLite local del nodo
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f'sqlite:///../emergency_sala{NODE_ID}.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Puerto Flask (5000, 5001, 5002, 5003) - o usar variable de entorno
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000 + NODE_ID - 1))

    # Puerto TCP del nodo para comunicación distribuida
    TCP_PORT = 5555 + NODE_ID - 1

    # IPs y puertos de otros nodos en el sistema
    OTROS_NODOS = [
        {'id': 1, 'url': 'http://localhost:5000', 'tcp_port': 5555},
        {'id': 2, 'url': 'http://localhost:5001', 'tcp_port': 5556},
        {'id': 3, 'url': 'http://localhost:5002', 'tcp_port': 5557},
        {'id': 4, 'url': 'http://localhost:5003', 'tcp_port': 5558},
    ]

    # Configuración de SocketIO
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*'

    # Configuración de timeouts
    HEARTBEAT_INTERVAL = 5  # segundos
    NODE_TIMEOUT = 15  # segundos para considerar nodo caído

    # Configuración de logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_otros_nodos_activos(cls):
        """Retorna lista de otros nodos (excluyendo el actual)"""
        return [nodo for nodo in cls.OTROS_NODOS if nodo['id'] != cls.NODE_ID]

    @classmethod
    def get_info_nodo_actual(cls):
        """Retorna información del nodo actual"""
        for nodo in cls.OTROS_NODOS:
            if nodo['id'] == cls.NODE_ID:
                return nodo
        return None

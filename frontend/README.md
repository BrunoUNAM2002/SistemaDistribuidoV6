# Frontend Flask - Sistema de Emergencias Médicas

Frontend web profesional para el sistema distribuido de gestión de emergencias médicas.

## Características

- **Interfaz Web Moderna**: Bootstrap 5 + Chart.js
- **Tiempo Real**: WebSockets con Flask-SocketIO
- **Multi-Nodo**: Cada sala ejecuta su propia instancia Flask
- **Autenticación**: Sistema de login con roles (Admin, Doctor, Trabajador Social)
- **Dashboard Interactivo**: Métricas en tiempo real con gráficas
- **API REST**: Endpoints AJAX para consultas rápidas

## Requisitos

- Python 3.10+
- Base de datos SQLite (generada por el backend)

## Instalación

1. Instalar dependencias:
```bash
cd frontend
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional):
```bash
# .env
NODE_ID=1
SECRET_KEY=tu-clave-secreta
DATABASE_URI=sqlite:///../emergency_sala1.db
```

## Uso

### Iniciar un nodo individual

```bash
# Nodo 1 (Sala 1 - Maestro)
NODE_ID=1 python app.py
# Acceder en: http://localhost:5000

# Nodo 2 (Sala 2)
NODE_ID=2 python app.py
# Acceder en: http://localhost:5001

# Nodo 3 (Sala 3)
NODE_ID=3 python app.py
# Acceder en: http://localhost:5002

# Nodo 4 (Sala 4)
NODE_ID=4 python app.py
# Acceder en: http://localhost:5003
```

### Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| doctor1 | doc123 | Doctor |
| doctor2 | doc123 | Doctor |
| trabajador1 | trab123 | Trabajador Social |
| trabajador2 | trab123 | Trabajador Social |

## Estructura del Proyecto

```
frontend/
├── app.py                  # Aplicación Flask principal
├── config.py               # Configuración multi-nodo
├── models.py               # Modelos SQLAlchemy
├── auth.py                 # Autenticación y roles
├── routes/                 # Blueprints
│   ├── visitas.py          # Crear/cerrar visitas
│   ├── consultas.py        # Consultas globales (admin)
│   └── api.py              # Endpoints AJAX
├── templates/              # HTML con Jinja2
│   ├── base.html           # Template base
│   ├── login.html          # Login
│   ├── dashboard.html      # Dashboard principal
│   ├── crear_visita.html   # Formulario crear visita
│   ├── mis_visitas.html    # Vista doctor
│   ├── consultas.html      # Vista admin
│   └── todas_visitas.html  # Todas las visitas
├── static/
│   ├── css/
│   │   └── custom.css      # Estilos personalizados
│   └── js/
│       ├── socketio.js     # Cliente WebSocket
│       ├── dashboard.js    # Lógica dashboard + Chart.js
│       └── visitas.js      # Lógica formularios
└── requirements.txt        # Dependencias
```

## Funcionalidades por Rol

### Trabajador Social
- ✅ Crear visitas de emergencia
- ✅ Registrar nuevos pacientes
- ✅ Ver recursos disponibles (doctores/camas)
- ✅ Dashboard con métricas

### Doctor
- ✅ Ver visitas asignadas
- ✅ Cerrar visitas (agregar diagnóstico)
- ✅ Dashboard con métricas
- ✅ Notificaciones en tiempo real

### Administrador
- ✅ Consultas globales (todos los recursos)
- ✅ Filtros por sala
- ✅ Ver estado de todos los nodos
- ✅ Acceso completo al sistema

## API REST Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/metricas` | GET | Métricas del dashboard |
| `/api/recursos-disponibles` | GET | Doctores y camas disponibles |
| `/api/visitas-activas` | GET | Visitas activas (filtrable) |
| `/api/visitas-por-hora` | GET | Datos para gráfica de visitas |
| `/api/visitas-por-sala` | GET | Distribución por sala |
| `/api/estado-nodos` | GET | Estado de todos los nodos |
| `/api/ultimas-visitas` | GET | Últimas 10 visitas |

## WebSocket Events

### Cliente → Servidor
- `solicitar_metricas`: Solicitar métricas actualizadas

### Servidor → Cliente
- `connected`: Confirmación de conexión
- `visita_creada`: Nueva visita creada (broadcast)
- `visita_cerrada`: Visita cerrada (broadcast)
- `metricas_actualizadas`: Métricas actualizadas

## Integración con Backend

El frontend se conecta automáticamente a la base de datos SQLite generada por el backend:
- `emergency_sala1.db` (Nodo 1)
- `emergency_sala2.db` (Nodo 2)
- `emergency_sala3.db` (Nodo 3)
- `emergency_sala4.db` (Nodo 4)

El esquema de BD debe coincidir exactamente con los modelos definidos en `models.py`.

## Desarrollo

### Hot Reload
Flask está configurado con `debug=True`, los cambios en el código se reflejan automáticamente.

### Logs
Los logs se muestran en consola con el nivel configurado en `config.py` (default: INFO).

### Testing
Abrir múltiples navegadores/pestañas para simular diferentes usuarios:
- Pestaña 1: http://localhost:5000 (Sala 1) - Login como doctor1
- Pestaña 2: http://localhost:5000 (Sala 1) - Login como trabajador1
- Pestaña 3: http://localhost:5001 (Sala 2) - Login como doctor2
- Pestaña 4: http://localhost:5000 (Sala 1) - Login como admin

## Troubleshooting

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Can't connect to database"
Verificar que la BD del backend existe en la ruta correcta:
```bash
ls ../emergency_sala*.db
```

### Puerto ya en uso
Cambiar el puerto en `config.py` o usar otra variable NODE_ID.

## Tecnologías

- **Backend**: Flask 3.0, Flask-Login, Flask-SocketIO, SQLAlchemy
- **Frontend**: Bootstrap 5, Chart.js, Socket.IO client
- **Base de Datos**: SQLite (compatible con esquema del equipo)

## Próximos Pasos

1. Instalar dependencias: `pip install -r requirements.txt`
2. Iniciar nodos: `NODE_ID=1 python app.py`
3. Abrir navegador: http://localhost:5000
4. Login con usuario de prueba
5. Explorar funcionalidades

## Autores

Proyecto de Sistemas Distribuidos - 9º Semestre

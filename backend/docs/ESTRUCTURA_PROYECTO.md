# ESTRUCTURA DEL PROYECTO

**Fecha de Reorganización:** 19 de Noviembre de 2025
**Versión:** 2.0.0

---

## 📁 Estructura de Directorios

```
/Proyectos/
│
├── backend/                          # 🔧 BACKEND (Python/Flask/Bully)
│   ├── app.py                       # Aplicación Flask principal
│   ├── config.py                    # Configuración del sistema
│   ├── models.py                    # Modelos SQLAlchemy (ORM)
│   ├── auth.py                      # Autenticación de usuarios
│   ├── init_test_db.py              # Script de inicialización de BD
│   │
│   ├── routes/                      # 📍 Rutas de la API
│   │   ├── __init__.py
│   │   ├── api.py                  # REST API (/api/*)
│   │   ├── visitas.py              # Gestión de visitas (/visitas/*)
│   │   └── consultas.py            # Consultas administrativas
│   │
│   ├── bully_advanced/              # 👑 Sistema de Consenso Bully
│   │   ├── __init__.py
│   │   ├── priority_scorer.py      # Scoring multi-dimensional
│   │   ├── failure_predictor.py    # Predicción ML de fallos
│   │   ├── byzantine_quorum.py     # Quorum bizantino
│   │   ├── communication.py        # TCP/UDP híbrido
│   │   ├── event_sourcing.py       # Event store + WAL
│   │   ├── fencing_tokens.py       # Tokens anti-split-brain
│   │   └── bully_engine.py         # Motor principal
│   │
│   ├── .env.example                 # Variables de entorno (ejemplo)
│   ├── .gitignore                   # Archivos ignorados por git
│   └── emergency_sala1.db           # Base de datos de prueba
│
├── frontend/                         # 🎨 FRONTEND (HTML/CSS/JS)
│   ├── templates/                   # Plantillas Jinja2
│   │   ├── base.html
│   │   ├── dashboard_lite.html
│   │   ├── login.html
│   │   ├── visitas/
│   │   └── consultas/
│   │
│   └── static/                      # Archivos estáticos
│       ├── css/
│       ├── js/
│       └── img/
│
├── emergencias.db                    # 💾 Base de datos principal
├── schema.sql                        # Schema SQL completo
├── schema2.sql                       # Schema alternativo
├── poblardb.py                       # Script para poblar BD
│
├── requirements.txt                  # 📦 Dependencias Python
├── start_all_nodes.sh               # 🚀 Script de inicio (4 nodos)
│
├── README.md                         # Documentación principal
├── CLAUDE.md                         # Instrucciones para Claude
├── IMPLEMENTATION_SUMMARY.md         # Resumen de implementación
├── BULLY_ADVANCED_DESIGN.md         # Diseño detallado (Parte 1)
├── BULLY_ADVANCED_DESIGN_PART2.md   # Diseño detallado (Parte 2)
├── ESTRUCTURA_PROYECTO.md           # Este archivo
│
├── Primer entregable.py             # Entregable 1 (P2P básico)
├── PROPUESTA.md                     # Propuesta del proyecto
├── PROPUESTA.pdf
└── MEDICAL_WEBSITE_DESIGN_RESEARCH.md
```

---

## 🎯 Separación Backend/Frontend

### Backend (`/backend`)

**Responsabilidades:**
- Lógica de negocio
- API REST
- Gestión de base de datos
- Sistema de consenso distribuido (Bully)
- Autenticación y autorización
- Comunicación entre nodos

**Tecnologías:**
- Python 3.8+
- Flask (web framework)
- SQLAlchemy (ORM)
- Flask-SocketIO (WebSockets)
- scikit-learn (ML)
- psutil (métricas del sistema)

**Puertos:**
- Flask: 5000-5003 (HTTP)
- Bully TCP: 5555-5558 (elecciones)
- Bully UDP: 6000-6003 (heartbeats)

### Frontend (`/frontend`)

**Responsabilidades:**
- Interfaz de usuario
- Presentación de datos
- Interacción con usuario
- Notificaciones en tiempo real

**Tecnologías:**
- HTML5
- CSS3 (sin Bootstrap, optimizado)
- JavaScript vanilla
- Socket.IO client (WebSockets)

---

## 🚀 Cómo Ejecutar

### Opción 1: Script Automático (4 nodos)

```bash
# Desde la raíz del proyecto
./start_all_nodes.sh
```

Este script inicia automáticamente:
- Nodo 1 en http://localhost:5000
- Nodo 2 en http://localhost:5001
- Nodo 3 en http://localhost:5002
- Nodo 4 en http://localhost:5003

### Opción 2: Manual (un nodo a la vez)

```bash
# Terminal 1 - Nodo 1
cd backend
NODE_ID=1 FLASK_PORT=5000 python app.py

# Terminal 2 - Nodo 2
cd backend
NODE_ID=2 FLASK_PORT=5001 python app.py

# Terminal 3 - Nodo 3
cd backend
NODE_ID=3 FLASK_PORT=5002 python app.py

# Terminal 4 - Nodo 4
cd backend
NODE_ID=4 FLASK_PORT=5003 python app.py
```

---

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en `/backend/` basado en `.env.example`:

```bash
# Identificador del nodo (1-4)
NODE_ID=1

# Puerto Flask
FLASK_PORT=5000

# Nivel de logging
LOG_LEVEL=DEBUG

# Secret key para Flask
SECRET_KEY=tu-clave-secreta-aqui
```

### Base de Datos

La base de datos `emergencias.db` debe estar en la **raíz del proyecto**, no en backend.

**Inicializar BD:**
```bash
cd backend
python init_test_db.py
```

---

## 📊 Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                         USUARIO                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Frontend (Browser)  │
          │  - templates/        │
          │  - static/           │
          └──────────┬───────────┘
                     │ HTTP/WebSocket
                     ▼
          ┌──────────────────────┐
          │  Backend (Flask)     │
          │  - routes/           │
          │  - models.py         │
          │  - auth.py           │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────────┐
   │   BD   │  │  Bully  │  │ Otros Nodos  │
   │ SQLite │  │ Engine  │  │ (TCP/UDP)    │
   └────────┘  └─────────┘  └──────────────┘
```

---

## 🔌 API Endpoints

### Autenticación
- `GET  /login` - Formulario de login
- `POST /login` - Autenticar usuario
- `GET  /logout` - Cerrar sesión

### Dashboard
- `GET  /` - Dashboard principal
- `GET  /dashboard` - Dashboard (alias)

### Visitas
- `GET    /visitas` - Listar visitas
- `POST   /visitas/crear` - Crear visita (solo líder)
- `POST   /visitas/<folio>/cerrar` - Cerrar visita (solo líder)
- `GET    /visitas/<folio>` - Ver detalle

### Consultas
- `GET  /consultas/pacientes` - Listar pacientes
- `GET  /consultas/doctores` - Listar doctores
- `GET  /consultas/salas` - Listar salas

### API REST
- `GET  /api/metricas` - Métricas del nodo
- `GET  /api/estado-nodos` - Estado de todos los nodos
- `GET  /api/bully/status` - Estado del sistema Bully

### WebSocket Events
- `connect` - Cliente conectado
- `disconnect` - Cliente desconectado
- `solicitar_metricas` - Solicitar métricas actualizadas
- `solicitar_bully_status` - Solicitar estado Bully
- `visita_creada` - Notificación de visita creada
- `visita_cerrada` - Notificación de visita cerrada
- `lider_cambio` - Notificación de cambio de líder

---

## 🧪 Testing

### Pruebas Manuales

1. **Iniciar cluster:**
   ```bash
   ./start_all_nodes.sh
   ```

2. **Acceder a cualquier nodo:**
   - Usuario: `admin`
   - Contraseña: `admin123`

3. **Observar elección de líder:**
   - Revisar logs
   - Ver qué nodo se convierte en líder
   - Observar heartbeats UDP

4. **Simular fallo del líder:**
   - Matar proceso del líder (Ctrl+C)
   - Observar nueva elección
   - Verificar que otro nodo toma el liderazgo

5. **Crear visitas:**
   - Intentar crear desde nodo no-líder → Redirección
   - Crear desde líder → Éxito

### Comandos Útiles

```bash
# Ver procesos Python corriendo
ps aux | grep python

# Matar todos los nodos
pkill -f "python app.py"

# Ver logs en tiempo real
tail -f backend/app.log

# Verificar puertos en uso
lsof -i :5000
lsof -i :5555

# Test de conectividad TCP
nc -zv localhost 5555

# Test de heartbeat UDP
nc -u localhost 6000
```

---

## 📚 Documentación Adicional

- **IMPLEMENTATION_SUMMARY.md** - Resumen completo de la implementación
- **BULLY_ADVANCED_DESIGN.md** - Diseño técnico detallado (Parte 1)
- **BULLY_ADVANCED_DESIGN_PART2.md** - Diseño técnico (Parte 2)
- **CLAUDE.md** - Instrucciones para Claude Code
- **README.md** - Documentación general del sistema

---

## 🐛 Troubleshooting

### Error: "No such file or directory: templates/"
**Solución:** Asegurarse de estar ejecutando desde `/backend/`

### Error: "Address already in use"
**Solución:**
```bash
# Encontrar proceso usando el puerto
lsof -i :5000
# Matar el proceso
kill -9 <PID>
```

### Error: "Cannot import bully_advanced"
**Solución:** Verificar que estás en el directorio `backend/`

### Error: "Database is locked"
**Solución:**
```bash
# Verificar que no haya múltiples instancias
pkill -f "python app.py"
# Reiniciar
./start_all_nodes.sh
```

---

## 📝 Notas Importantes

1. **Base de Datos:** `emergencias.db` debe estar en la raíz, NO en backend/
2. **Ejecución:** Siempre ejecutar `app.py` desde dentro de `backend/`
3. **Templates:** Flask busca automáticamente en `../frontend/templates/`
4. **Static:** Archivos estáticos en `../frontend/static/`
5. **Logs:** Se generan en la consola, no en archivo (por defecto)

---

**Última actualización:** 19 de Noviembre de 2025
**Versión:** 2.0.0 - Backend/Frontend separados
**Autor:** Claude (Sonnet 4.5)

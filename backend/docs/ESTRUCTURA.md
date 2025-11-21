# Estructura del Proyecto

Este documento describe la organización del proyecto de sistema distribuido de emergencias médicas.

## Árbol de Directorios

```
backend/
├── src/                      # Código fuente de la aplicación
│   ├── app.py               # Punto de entrada principal de Flask
│   ├── config.py            # Configuración de la aplicación
│   ├── models.py            # Modelos de base de datos (SQLAlchemy)
│   ├── auth.py              # Sistema de autenticación
│   ├── bully/               # Implementación del algoritmo Bully
│   │   ├── __init__.py
│   │   ├── bully_node.py    # Lógica del nodo Bully
│   │   └── communication.py # Comunicación TCP/UDP entre nodos
│   └── routes/              # Rutas de la API REST
│       ├── __init__.py
│       ├── api.py           # Endpoints principales
│       ├── bully.py         # Endpoints del algoritmo Bully
│       ├── consultas.py     # Endpoints de consultas médicas
│       └── visitas.py       # Endpoints de visitas de emergencia
├── scripts/                 # Scripts de utilidad
│   ├── start_all_nodes.sh  # Script para iniciar todos los nodos
│   └── init_test_db.py     # Inicialización de BD de prueba
├── tests/                   # Pruebas y tests
│   ├── test_failover.py    # Pruebas de failover del algoritmo Bully
│   └── failover_test.log   # Logs de las pruebas
├── data/                    # Datos persistentes
│   ├── emergency_sala1.db  # Base de datos del nodo 1
│   ├── emergency_sala2.db  # Base de datos del nodo 2
│   ├── emergency_sala3.db  # Base de datos del nodo 3
│   └── emergency_sala4.db  # Base de datos del nodo 4
├── logs/                    # Logs de la aplicación
│   ├── node_1.log          # Logs del nodo 1
│   ├── node_2.log          # Logs del nodo 2
│   ├── node_3.log          # Logs del nodo 3
│   └── node_4.log          # Logs del nodo 4
├── docs/                    # Documentación
│   └── ESTRUCTURA.md       # Este archivo
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Documentación principal del proyecto
```

## Descripción de Componentes

### src/ - Código Fuente

Contiene todo el código fuente de la aplicación organizado en módulos:

- **app.py**: Aplicación Flask principal, configuración de logging, inicialización de extensiones
- **config.py**: Configuración centralizada (puertos, bases de datos, nodos del cluster)
- **models.py**: Modelos de SQLAlchemy para el sistema de emergencias
- **auth.py**: Autenticación y autorización con Flask-Login
- **bully/**: Módulo del algoritmo Bully para elección de líder
- **routes/**: Blueprints de Flask con endpoints REST organizados por funcionalidad

### scripts/ - Scripts de Utilidad

Scripts auxiliares para operaciones del sistema:

- **start_all_nodes.sh**: Inicia los 4 nodos del cluster de forma secuencial con verificación de puertos
- **init_test_db.py**: Crea y puebla las bases de datos con datos de prueba

### tests/ - Pruebas

Contiene las pruebas automatizadas del sistema:

- **test_failover.py**: Pruebas de tolerancia a fallos y failover dinámico del algoritmo Bully

### data/ - Bases de Datos

Almacena las bases de datos SQLite de cada nodo. Cada nodo mantiene su propia copia de los datos.

### logs/ - Logs

Archivos de log con formato rotativo (10MB máximo, 5 backups). Incluyen:
- Timestamps
- ID del nodo
- Nivel de log (INFO, DEBUG, WARNING, ERROR)
- Componente
- Mensaje

## Ejecución del Sistema

### Iniciar todos los nodos

Desde el directorio `backend/`:

```bash
./scripts/start_all_nodes.sh
```

### Iniciar un nodo individual

```bash
NODE_ID=1 FLASK_PORT=5050 python3 src/app.py
```

### Ejecutar pruebas de failover

```bash
python3 tests/test_failover.py
```

### Inicializar base de datos de prueba

```bash
python3 scripts/init_test_db.py
```

## Puertos del Sistema

### Flask (Web Interface)
- Nodo 1: http://localhost:5050
- Nodo 2: http://localhost:5051
- Nodo 3: http://localhost:5052
- Nodo 4: http://localhost:5053

### TCP (Bully - Elecciones)
- Nodo 1: 5555
- Nodo 2: 5556
- Nodo 3: 5557
- Nodo 4: 5558

### UDP (Bully - Heartbeats)
- Nodo 1: 6000
- Nodo 2: 6001
- Nodo 3: 6002
- Nodo 4: 6003

## Notas de Desarrollo

- Los imports en `scripts/` y `tests/` están configurados para encontrar módulos en `src/`
- Las rutas de templates y static apuntan a `../frontend/` desde `src/`
- Las bases de datos se crean en `data/` automáticamente si no existen
- Los logs se crean en `logs/` con rotación automática

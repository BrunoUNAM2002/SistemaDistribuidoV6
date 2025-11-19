#!/bin/bash

# Script para iniciar todos los nodos del sistema de emergencias médicas
# Cada nodo se ejecuta en un puerto diferente

echo "================================================"
echo "Sistema de Emergencias Médicas - Multi-Nodo"
echo "================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "Error: Este script debe ejecutarse desde el directorio frontend/"
    exit 1
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    exit 1
fi

# Verificar dependencias
echo "Verificando dependencias..."
python3 -c "import flask, flask_login, flask_socketio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "${YELLOW}Instalando dependencias...${NC}"
    pip3 install -r requirements.txt
fi

echo ""
echo "${GREEN}Iniciando nodos...${NC}"
echo ""

# Matar procesos anteriores si existen
pkill -f "python3 app.py" 2>/dev/null
sleep 1

# Iniciar Nodo 1 (Maestro)
echo "${BLUE}[Sala 1]${NC} Iniciando en puerto 5000 (Maestro)..."
NODE_ID=1 python3 app.py > logs_sala1.log 2>&1 &
SALA1_PID=$!
sleep 2

# Iniciar Nodo 2
echo "${BLUE}[Sala 2]${NC} Iniciando en puerto 5001..."
NODE_ID=2 python3 app.py > logs_sala2.log 2>&1 &
SALA2_PID=$!
sleep 2

# Iniciar Nodo 3
echo "${BLUE}[Sala 3]${NC} Iniciando en puerto 5002..."
NODE_ID=3 python3 app.py > logs_sala3.log 2>&1 &
SALA3_PID=$!
sleep 2

# Iniciar Nodo 4
echo "${BLUE}[Sala 4]${NC} Iniciando en puerto 5003..."
NODE_ID=4 python3 app.py > logs_sala4.log 2>&1 &
SALA4_PID=$!
sleep 2

echo ""
echo "${GREEN}✓ Todos los nodos iniciados correctamente${NC}"
echo ""
echo "================================================"
echo "URLs de acceso:"
echo "  Sala 1 (Maestro): http://localhost:5000"
echo "  Sala 2:           http://localhost:5001"
echo "  Sala 3:           http://localhost:5002"
echo "  Sala 4:           http://localhost:5003"
echo ""
echo "Usuarios de prueba:"
echo "  Admin:            admin / admin123"
echo "  Doctor 1:         doctor1 / doc123"
echo "  Trabajador 1:     trabajador1 / trab123"
echo ""
echo "Logs:"
echo "  Sala 1: logs_sala1.log"
echo "  Sala 2: logs_sala2.log"
echo "  Sala 3: logs_sala3.log"
echo "  Sala 4: logs_sala4.log"
echo ""
echo "PIDs:"
echo "  Sala 1: $SALA1_PID"
echo "  Sala 2: $SALA2_PID"
echo "  Sala 3: $SALA3_PID"
echo "  Sala 4: $SALA4_PID"
echo "================================================"
echo ""
echo "${YELLOW}Presiona Ctrl+C para detener todos los nodos${NC}"
echo ""

# Función para cleanup al salir
cleanup() {
    echo ""
    echo "${YELLOW}Deteniendo todos los nodos...${NC}"
    kill $SALA1_PID $SALA2_PID $SALA3_PID $SALA4_PID 2>/dev/null
    wait $SALA1_PID $SALA2_PID $SALA3_PID $SALA4_PID 2>/dev/null
    echo "${GREEN}✓ Todos los nodos detenidos${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Mantener el script corriendo
wait

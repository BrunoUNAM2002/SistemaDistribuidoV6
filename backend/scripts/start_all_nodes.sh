#!/bin/bash

# Script para iniciar los 4 nodos de forma controlada
# Asegura que TODOS los nodos estén completamente funcionales

echo "=========================================="
echo "Iniciando TODOS los nodos del cluster"
echo "=========================================="

# Función para verificar si un puerto está escuchando
wait_for_port() {
    local port=$1
    local max_attempts=30
    local attempt=0

    echo "Esperando que el puerto $port esté listo..."
    while [ $attempt -lt $max_attempts ]; do
        if lsof -i:$port -sTCP:LISTEN >/dev/null 2>&1; then
            echo "✅ Puerto $port está listo"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done

    echo "❌ ERROR: Puerto $port no se pudo iniciar"
    return 1
}

# Limpiar procesos anteriores
echo "Limpiando procesos anteriores..."
pkill -f "NODE_ID=" 2>/dev/null
lsof -ti:5050,5051,5052,5053,5555,5556,5557,5558,6000,6001,6002,6003 | xargs kill -9 2>/dev/null
sleep 2

# Iniciar Node 1
echo ""
echo "🚀 Iniciando Node 1..."
NODE_ID=1 FLASK_PORT=5050 python3 src/app.py > /dev/null 2>&1 &
NODE1_PID=$!
wait_for_port 5050 || exit 1
sleep 2

# Iniciar Node 2
echo ""
echo "🚀 Iniciando Node 2..."
NODE_ID=2 FLASK_PORT=5051 python3 src/app.py > /dev/null 2>&1 &
NODE2_PID=$!
wait_for_port 5051 || exit 1
sleep 2

# Iniciar Node 3
echo ""
echo "🚀 Iniciando Node 3..."
NODE_ID=3 FLASK_PORT=5052 python3 src/app.py > /dev/null 2>&1 &
NODE3_PID=$!
wait_for_port 5052 || exit 1
sleep 2

# Iniciar Node 4
echo ""
echo "🚀 Iniciando Node 4..."
NODE_ID=4 FLASK_PORT=5053 python3 src/app.py > /dev/null 2>&1 &
NODE4_PID=$!
wait_for_port 5053 || exit 1

echo ""
echo "=========================================="
echo "✅ TODOS los nodos están funcionando!"
echo "=========================================="
echo ""
echo "📊 URLs de los nodos:"
echo "   Node 1: http://localhost:5050 (PID: $NODE1_PID)"
echo "   Node 2: http://localhost:5051 (PID: $NODE2_PID)"
echo "   Node 3: http://localhost:5052 (PID: $NODE3_PID)"
echo "   Node 4: http://localhost:5053 (PID: $NODE4_PID)"
echo ""
echo "🔍 Verificando estado de los puertos..."
lsof -i:5050-5053 | grep LISTEN

echo ""
echo "👑 El Nodo 4 debería ser el líder inicial"
echo "   Espera 5-10 segundos para que se complete la elección"

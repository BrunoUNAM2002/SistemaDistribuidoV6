#!/usr/bin/env python3
"""
Script de prueba de failover dinámico para el algoritmo Bully.
Prueba que el sistema elija correctamente el líder basado en nodos activos.
"""

import subprocess
import time
import json
import requests
import sys
import signal
import os
from datetime import datetime

class FailoverTester:
    def __init__(self):
        self.processes = {}
        self.base_url = "http://localhost:{}"
        self.flask_ports = {1: 5050, 2: 5051, 3: 5052, 4: 5053}
        self.log_file = os.path.join(os.path.dirname(__file__), "failover_test.log")

    def log(self, message):
        """Registra mensajes en consola y archivo."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        with open(self.log_file, "a") as f:
            f.write(msg + "\n")

    def start_node(self, node_id):
        """Inicia un nodo específico."""
        port = self.flask_ports[node_id]
        cmd = f"NODE_ID={node_id} FLASK_PORT={port} python3 src/app.py"

        self.log(f"🚀 Starting Node {node_id} on port {port}")
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Crear un nuevo grupo de procesos
        )
        self.processes[node_id] = proc
        time.sleep(3)  # Esperar a que el nodo inicie

    def stop_node(self, node_id):
        """Detiene un nodo específico."""
        if node_id in self.processes:
            self.log(f"🛑 Stopping Node {node_id}")
            proc = self.processes[node_id]
            # Terminar todo el grupo de procesos
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait()
            del self.processes[node_id]

    def get_node_status(self, node_id):
        """Obtiene el estado de un nodo."""
        try:
            port = self.flask_ports[node_id]
            response = requests.get(f"{self.base_url.format(port)}/status", timeout=2)
            return response.json()
        except:
            return None

    def get_current_leader(self):
        """Determina quién es el líder actual según los nodos activos."""
        leaders = {}
        for node_id in self.flask_ports:
            status = self.get_node_status(node_id)
            if status:
                leader = status.get("leader")
                if leader:
                    leaders[node_id] = leader
        return leaders

    def verify_consensus(self, expected_leader):
        """Verifica que todos los nodos estén de acuerdo con el líder."""
        leaders = self.get_current_leader()
        consensus = all(l == expected_leader for l in leaders.values() if l)

        if consensus and leaders:
            self.log(f"✅ CONSENSUS: All nodes agree on leader {expected_leader}")
            return True
        else:
            self.log(f"❌ NO CONSENSUS: Leaders by node: {leaders}")
            return False

    def wait_for_stabilization(self, timeout=40):
        """Espera hasta que el sistema se estabilice con un líder."""
        self.log("⏳ Waiting for system stabilization...")
        start = time.time()

        while time.time() - start < timeout:
            leaders = self.get_current_leader()
            if leaders:
                # Verificar si hay consenso
                unique_leaders = set(leaders.values())
                if len(unique_leaders) == 1 and None not in unique_leaders:
                    leader = unique_leaders.pop()
                    self.log(f"📊 System stabilized with leader: {leader}")
                    return leader
            time.sleep(2)

        self.log("⚠️ Timeout waiting for stabilization")
        return None

    def run_test_scenario(self):
        """Ejecuta el escenario completo de pruebas de failover."""
        self.log("="*60)
        self.log("🧪 INICIANDO PRUEBA DE FAILOVER DINÁMICO")
        self.log("="*60)

        try:
            # Limpiar procesos anteriores
            self.log("Limpiando procesos anteriores...")
            subprocess.run("pkill -f 'NODE_ID='", shell=True, check=False)
            time.sleep(2)

            # ESCENARIO 1: Iniciar todos los nodos
            self.log("\n📌 ESCENARIO 1: Iniciando todos los nodos (1, 2, 3, 4)")
            for i in range(1, 5):
                self.start_node(i)

            leader = self.wait_for_stabilization()
            if leader != 4:
                self.log(f"❌ ERROR: Se esperaba líder 4, pero es {leader}")
            else:
                self.log(f"✅ CORRECTO: Node 4 es el líder inicial")
            self.verify_consensus(4)

            # Ver URLs de los nodos
            self.log("\n📊 URLs de los nodos activos:")
            for node_id in range(1, 5):
                port = self.flask_ports[node_id]
                self.log(f"   Node {node_id}: http://localhost:{port}")

            # ESCENARIO 2: Falla Node 4
            self.log("\n📌 ESCENARIO 2: Simulando falla de Node 4")
            self.stop_node(4)
            time.sleep(15)  # Esperar detección de falla y elección

            leader = self.wait_for_stabilization()
            if leader != 3:
                self.log(f"❌ ERROR: Se esperaba líder 3, pero es {leader}")
            else:
                self.log(f"✅ CORRECTO: Node 3 tomó el liderazgo")
            self.verify_consensus(3)

            # ESCENARIO 3: Falla Node 3
            self.log("\n📌 ESCENARIO 3: Simulando falla de Node 3")
            self.stop_node(3)
            time.sleep(15)

            leader = self.wait_for_stabilization()
            if leader != 2:
                self.log(f"❌ ERROR: Se esperaba líder 2, pero es {leader}")
            else:
                self.log(f"✅ CORRECTO: Node 2 tomó el liderazgo")
            self.verify_consensus(2)

            # ESCENARIO 4: Node 4 vuelve a estar en línea
            self.log("\n📌 ESCENARIO 4: Node 4 vuelve a estar en línea")
            self.start_node(4)
            time.sleep(10)

            leader = self.wait_for_stabilization()
            if leader != 4:
                self.log(f"❌ ERROR: Se esperaba que Node 4 recuperara el liderazgo, pero el líder es {leader}")
            else:
                self.log(f"✅ CORRECTO: Node 4 recuperó el liderazgo")
            self.verify_consensus(4)

            # ESCENARIO 5: Node 3 vuelve a estar en línea
            self.log("\n📌 ESCENARIO 5: Node 3 vuelve a estar en línea")
            self.start_node(3)
            time.sleep(10)

            leader = self.wait_for_stabilization()
            if leader != 4:
                self.log(f"⚠️ Node 4 sigue siendo líder (correcto)")
            self.verify_consensus(4)

            self.log("\n"+"="*60)
            self.log("✅ PRUEBA DE FAILOVER COMPLETADA")
            self.log("="*60)

        except Exception as e:
            self.log(f"❌ Error durante la prueba: {e}")

        finally:
            # Limpiar todos los procesos
            self.cleanup()

    def cleanup(self):
        """Limpia todos los procesos activos."""
        self.log("\n🧹 Limpiando procesos...")
        for node_id in list(self.processes.keys()):
            self.stop_node(node_id)
        subprocess.run("pkill -f 'NODE_ID='", shell=True, check=False)


if __name__ == "__main__":
    tester = FailoverTester()
    try:
        tester.run_test_scenario()
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
        tester.cleanup()
        sys.exit(0)
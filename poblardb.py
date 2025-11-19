import sqlite3
import os
from datetime import datetime

# --- Configuración de Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'emergencias.db')

print(f"Conectando a la base de datos en: {DB_PATH}")

def poblar_datos_reales():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- 1. LIMPIEZA TOTAL ---
        print("🧹 Limpiando datos antiguos...")
        cursor.execute("DELETE FROM VISITAS_EMERGENCIA")
        cursor.execute("DELETE FROM CAMAS_ATENCION")
        cursor.execute("DELETE FROM DOCTORES")
        cursor.execute("DELETE FROM TRABAJADORES_SOCIALES")
        cursor.execute("DELETE FROM PACIENTES")
        cursor.execute("DELETE FROM sqlite_sequence") 

        # --- 2. PACIENTES (3 Casos Activos) ---
        print("Registrando Pacientes...")
        pacientes = [
            ('Gerardo Martínez', 34, 'M', '555-0192'), # ID 1
            ('Lucía Fernández', 28, 'F', '555-1283'),  # ID 2
            ('Pedro N.', 8, 'M', 'Sin contacto')       # ID 3
        ]
        cursor.executemany("INSERT INTO PACIENTES (nombre, edad, sexo, contacto) VALUES (?, ?, ?, ?)", pacientes)

        # --- 3. DOCTORES (10 Doctores - SIN ESPECIALIDAD) ---
        print("Registrando Plantilla de 10 Doctores...")
        # Formato: (Nombre, Sala_ID, Disponible)
        doctores = [
            # -- Los originales --
            ('Dr. Ricardo Mendiola', 1, 1),      # ID 1: Disp
            ('Dra. Elena Vázquez', 1, 0),        # ID 2: Ocupada
            ('Dr. Samuel Hernandez', 1, 1),            # ID 3: Disp
            ('Dra. Sofía Ramírez', 1, 0),        # ID 4: Ocupada
            
            # -- Los nuevos ingresos --
            ('Dr. Carlos Ruiz', 1, 1),           # ID 5: Disp
            ('Dra. Ana Torres', 1, 1),           # ID 6: Disp
            ('Dr. Luis Fernández', 1, 0),        # ID 7: Ocupado
            ('Dra. Patricia López', 1, 1),       # ID 8: Disp
            ('Dr. Miguel Ángel Torres', 1, 1),   # ID 9: Disp
            ('Dra. Carmen Diaz', 1, 1)        # ID 10: Disp
        ]
        # Nota: Se eliminó 'especialidad' del INSERT
        cursor.executemany("INSERT INTO DOCTORES (nombre, sala_id, disponible) VALUES (?, ?, ?)", doctores)

        # --- 4. TRABAJO SOCIAL ---
        print("📋 Registrando Trabajo Social...")
        cursor.execute("INSERT INTO TRABAJADORES_SOCIALES (nombre, sala_id, activo) VALUES ('Lic. Roberto Gómez', 1, 1)")

        # --- 5. CAMAS (10 Camas: 3 Ocupadas, 7 Libres) ---
        print("🛏️ Asignando Camas (101-110)...")
        
        # Camas Ocupadas
        cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) VALUES (101, 1, 1, 1)") # Gerardo
        cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) VALUES (102, 1, 1, 2)") # Lucía
        cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) VALUES (103, 1, 1, 3)") # Pedro

        # Camas Libres (104-110)
        for i in range(104, 111):
            cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) VALUES (?, 1, 0, NULL)", (i,))

        # --- 6. VISITAS DE EMERGENCIA ---
        print("Creando Expedientes de Visita...")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        visitas = [
            ('URG-2025-001', 1, 2, 1, None, 1, timestamp, 'En Tratamiento'),    # Gerardo c/ Dra. Elena
            ('URG-2025-002', 2, 3, 2, 1, 1, timestamp, 'En Observación'),       # Lucía c/ Dr. Samuel
            ('URG-2025-003', 3, 4, 3, None, 1, timestamp, 'Estabilización')     # Pedro c/ Dra. Sofía
        ]
        
        cursor.executemany("""
            INSERT INTO VISITAS_EMERGENCIA 
            (folio, paciente_id, doctor_id, cama_id, trabajador_social_id, sala_id, timestamp, estado) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, visitas)

        # --- FINALIZAR ---
        conn.commit()
        print("\n¡Datos actualizados correctamente (Sin Especialidades)!")
        print("Escenario:")
        print("  - 10 Doctores en plantilla.")
        print("  - 3 Pacientes ingresados.")
        print("  - 10 Camas configuradas.")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    poblar_datos_reales()
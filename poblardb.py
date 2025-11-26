import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'emergencias.db')

def poblar_datos_reales():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        print("🧹 Limpiando base de datos...")
        cursor.execute("DELETE FROM VISITAS_EMERGENCIA")
        cursor.execute("DELETE FROM CAMAS_ATENCION")
        cursor.execute("DELETE FROM DOCTORES")
        cursor.execute("DELETE FROM TRABAJADORES_SOCIALES")
        cursor.execute("DELETE FROM PACIENTES")
        cursor.execute("DELETE FROM USUARIOS_SISTEMA")
        cursor.execute("DELETE FROM CONSECUTIVOS_VISITAS")
        cursor.execute("DELETE FROM sqlite_sequence")

        print("📦 Insertando datos de prueba...")

        # --- PACIENTES ---
        pacientes = [
            ('Ana García López', 28, 'F', '555-0101'),
            ('Carlos Rodríguez', 45, 'M', '555-0102'),
            ('María Fernández', 32, 'F', '555-0103')
        ]
        cursor.executemany("INSERT INTO PACIENTES (nombre, edad, sexo, contacto) VALUES (?, ?, ?, ?)", pacientes)

        # --- DOCTORES ---
        doctores = [
            ('Dr. Ricardo Mendiola', 1, 1),
            ('Dra. Elena Vázquez', 1, 1),
            ('Dr. Samuel Kim', 1, 1)
        ]
        cursor.executemany("INSERT INTO DOCTORES (nombre, sala_id, disponible) VALUES (?, ?, ?)", doctores)

        # --- TRABAJADORES SOCIALES ---
        cursor.execute("INSERT INTO TRABAJADORES_SOCIALES (nombre, sala_id, activo) VALUES ('Lic. Roberto Gómez', 1, 1)")

        # --- CAMAS ---
        for i in range(101, 106):
            cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada) VALUES (?, 1, 0)", (i,))

        # --- USUARIOS DEL SISTEMA ---
        usuarios = [
            ('social1', '1234', 'SOCIAL', 1),
            ('doctor1', 'doctor1', 'DOCTOR', 1),
            ('doctor2', 'doctor2', 'DOCTOR', 2),
            ('doctor3', 'doctor3', 'DOCTOR', 3)
        ]
        cursor.executemany("INSERT INTO USUARIOS_SISTEMA (username, password, rol, id_personal) VALUES (?, ?, ?, ?)", usuarios)

        # --- CONSECUTIVOS (NUEVO) ---
        cursor.execute("INSERT INTO CONSECUTIVOS_VISITAS (sala_id, ultimo_consecutivo) VALUES (1, 0)")

        conn.commit()
        print("\n✅ Base de datos poblada exitosamente!")
        print("\n👥 USUARIOS DE PRUEBA:")
        print("   Trabajador Social: social1 / 1234")
        print("   Doctores: doctor1 / doctor1, doctor2 / doctor2, doctor3 / doctor3")
        print(f"\n📊 Estadísticas:")
        print(f"   - {len(pacientes)} pacientes")
        print(f"   - {len(doctores)} doctores") 
        print(f"   - 5 camas")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    poblar_datos_reales()

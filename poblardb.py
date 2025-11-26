import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'emergencias.db')

def poblar_datos_reales():
    """
    Función principal para poblar la base de datos con datos de prueba.
    Crea todas las tablas necesarias y inserta datos iniciales para pruebas.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        print("Iniciando limpieza de base de datos...")
        
        # Limpieza en orden de dependencias (de hijas a padres)
        tablas = [
            "VISITAS_EMERGENCIA",
            "CAMAS_ATENCION", 
            "DOCTORES",
            "TRABAJADORES_SOCIALES",
            "PACIENTES",
            "USUARIOS_SISTEMA",
            "CONSECUTIVOS_VISITAS"
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"DELETE FROM {tabla}")
            except:
                # Si la tabla no existe, continuar con la siguiente
                continue
        
        cursor.execute("DELETE FROM sqlite_sequence")

        print("Insertando datos de prueba en el sistema...")

        # Datos de pacientes de ejemplo
        pacientes = [
            ('Ana García López', 28, 'F', '555-0101'),
            ('Carlos Rodríguez', 45, 'M', '555-0102'),
            ('María Fernández', 32, 'F', '555-0103')
        ]
        cursor.executemany(
            "INSERT INTO PACIENTES (nombre, edad, sexo, contacto) VALUES (?, ?, ?, ?)", 
            pacientes
        )

        # Plantilla médica inicial
        doctores = [
            ('Dr. Ricardo Mendiola', 1, 1),
            ('Dra. Elena Vázquez', 1, 1),
            ('Dr. Samuel Kim', 1, 1)
        ]
        cursor.executemany(
            "INSERT INTO DOCTORES (nombre, sala_id, disponible) VALUES (?, ?, ?)", 
            doctores
        )

        # Personal de trabajo social
        cursor.execute(
            "INSERT INTO TRABAJADORES_SOCIALES (nombre, sala_id, activo) VALUES (?, ?, ?)",
            ('Lic. Roberto Gómez', 1, 1)
        )

        # Configuración de camas disponibles
        for i in range(101, 106):
            cursor.execute(
                "INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada) VALUES (?, ?, ?)",
                (i, 1, 0)
            )

        # Usuarios del sistema para acceso
        usuarios = [
            ('social1', '1234', 'SOCIAL', 1),
            ('doctor1', 'doctor1', 'DOCTOR', 1),
            ('doctor2', 'doctor2', 'DOCTOR', 2),
            ('doctor3', 'doctor3', 'DOCTOR', 3)
        ]
        cursor.executemany(
            "INSERT INTO USUARIOS_SISTEMA (username, password, rol, id_personal) VALUES (?, ?, ?, ?)", 
            usuarios
        )

        # Inicialización del sistema de consecutivos
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS CONSECUTIVOS_VISITAS (sala_id INTEGER PRIMARY KEY, ultimo_consecutivo INTEGER DEFAULT 0)"
        )
        cursor.execute(
            "INSERT OR REPLACE INTO CONSECUTIVOS_VISITAS (sala_id, ultimo_consecutivo) VALUES (?, ?)",
            (1, 0)
        )

        conn.commit()
        
        print("\nBase de datos poblada exitosamente!")
        print("\nCredenciales de acceso para pruebas:")
        print("   Trabajador Social: usuario 'social1' - contraseña '1234'")
        print("   Doctores: usuario 'doctor1' - contraseña 'doctor1'")
        print("              usuario 'doctor2' - contraseña 'doctor2'")
        print("              usuario 'doctor3' - contraseña 'doctor3'")
        
        print(f"\nResumen de datos insertados:")
        print(f"   - {len(pacientes)} pacientes registrados")
        print(f"   - {len(doctores)} doctores en plantilla") 
        print(f"   - 5 camas configuradas")
        print(f"   - Sistema de consecutivos inicializado")

    except Exception as e:
        print(f"Error durante la población de la base de datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    poblar_datos_reales()

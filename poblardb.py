import sqlite3
import os

# --- Configuración de Rutas (Igual que en tu script principal) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'emergencias.db')

print(f"Conectando a la base de datos en: {DB_PATH}")

def poblar_datos():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- 1. LIMPIEZA (Opcional) ---
        # Borramos datos anteriores para no duplicar si corres el script varias veces
        # El orden es importante por las claves foráneas
        print("Limpiando tablas antiguas...")
        cursor.execute("DELETE FROM CAMAS_ATENCION")
        cursor.execute("DELETE FROM DOCTORES")
        cursor.execute("DELETE FROM TRABAJADORES_SOCIALES")
        cursor.execute("DELETE FROM PACIENTES")
        # (Reseteamos los contadores de ID para que empiecen en 1)
        cursor.execute("DELETE FROM sqlite_sequence") 

        # --- 2. INSERTAR PACIENTES ---
        print("Insertando Pacientes...")
        pacientes = [
            ('Juan Pérez', 45, 'M', '555-1010'),
            ('María González', 32, 'F', '555-2020'),
            ('Carlos Ruiz', 78, 'M', '555-3030')
        ]
        cursor.executemany("INSERT INTO PACIENTES (nombre, edad, sexo, contacto) VALUES (?, ?, ?, ?)", pacientes)

        # --- 3. INSERTAR DOCTORES ---
        print("Insertando Doctores...")
        doctores = [
            ('Dr. Gregory House', 'Diagnóstico', 1, 1),      # Disponible
            ('Dra. Meredith Grey', 'Cirugía General', 1, 1)  # Disponible
        ]
        cursor.executemany("INSERT INTO DOCTORES (nombre, especialidad, sala_id, disponible) VALUES (?, ?, ?, ?)", doctores)

        # --- 4. INSERTAR TRABAJADOR SOCIAL ---
        print("Insertando Trabajador Social...")
        cursor.execute("INSERT INTO TRABAJADORES_SOCIALES (nombre, sala_id, activo) VALUES ('Lic. Ana Morales', 1, 1)")

        # --- 5. INSERTAR CAMAS (El nodo tiene 10 camas) ---
        print("Configurando las 10 camas de la Sala 1...")
        
        # Cama 101: OCUPADA por el paciente 1 (Juan Pérez)
        cursor.execute("""
            INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) 
            VALUES (101, 1, 1, 1)
        """)

        # Camas 102 a 110: LIBRES
        # Usamos un bucle para generar las 9 camas restantes
        for i in range(102, 111):
            cursor.execute("INSERT INTO CAMAS_ATENCION (numero, sala_id, ocupada, paciente_id) VALUES (?, 1, 0, NULL)", (i,))

        # --- CONFIRMAR CAMBIOS ---
        conn.commit()
        print("\n¡Éxito! La base de datos ha sido poblada.")
        print("  - 3 Pacientes")
        print("  - 2 Doctores")
        print("  - 1 Trabajador Social")
        print("  - 10 Camas (1 Ocupada, 9 Libres)")

    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    poblar_datos()
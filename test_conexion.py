from config.database import ConexionDB

def probar_conexion():
    print("=== PROBANDO CONEXIÓN A BASE DE DATOS ===\n")
    
    try:
        conexion = ConexionDB.obtener_conexion()
        cursor = conexion.cursor()
        
        print("✅ Conexión establecida correctamente")
        
        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()
        print(f"✅ Consulta de prueba: {resultado[0]}")
        
        print("\n=== VERIFICANDO TABLAS ===")
        tablas = ["Rol", "Persona", "Usuario", "Admin", "Profesion", "Docente", "Estudiante", "Programa"]
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"✅ Tabla {tabla}: {count} registros")
            except:
                print(f"❌ Tabla {tabla}: No existe")
        
        cursor.close()
        conexion.close()
        print("\n✅✅✅ PRUEBA COMPLETADA ✅✅✅")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    probar_conexion()
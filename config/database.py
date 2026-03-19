import pyodbc
 
class ConexionDB:
    SERVIDOR = "DESKTOP-CTIE9N6\PABLOMONGE"  # Cambia si tu instancia es diferente
    BASE_DATOS = 'Universidad'
    @classmethod
    def obtener_conexion(cls):
        try:
            cadena_conexion = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={cls.SERVIDOR};"
                f"DATABASE={cls.BASE_DATOS};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
            conexion = pyodbc.connect(cadena_conexion)
            return conexion
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None
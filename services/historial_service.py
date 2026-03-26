import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc

class HistorialService:
    def crear_movimiento(self, asignacion):
        """Crea una movimiento en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO TipoMovimiento (id_tipo_movimiento, codigo, descripcion,estado)
                OUTPUT INSERTED.id_tipo_movimiento
                VALUES (?, ?, ?, ?, ?, ?)
            """
            ultimo=self.obtener_movimiento()[-1]
            cursor.execute(query, (
                str(int(ultimo['id_tipo_movimiento'])+1),
                asignacion['codigo'],
                asignacion['descripcion'],
                asignacion['estado']
            ))
            id_asignacion = cursor.fetchone()[0]

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"movimiento creado exitosamente (ID: {id_asignacion})"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "Este movimiento ya está asignado a ese programa en el mismo periodo"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear movimiento: {str(e)}"

    def obtener_movimiento(self):
        """Obtiene todas las movimiento con datos completos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    a.id_tipo_movimiento,
                    a.codigo,
                    a.descripcion,
                    a.estado
                FROM TipoMovimiento a
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            asignaciones = []
            for row in resultados:
                asignaciones.append({
                    'id_tipo_movimiento':  row[0],
                    'codigo':           row[1],
                    'descripcion':      row[2],
                    'estado':           row[3]
                })

            cursor.close()
            conexion.close()
            return asignaciones, None

        except Exception as e:
            return None, f"Error al obtener historial: {str(e)}"
        
        
        
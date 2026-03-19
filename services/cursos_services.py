import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc

class CursoService:

    def crear_Curso(self, Curso):
        """Crea un nuevo Curso en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            # Un curso es una sola fila en Materia — solo un INSERT
            query_Curso = """
                INSERT INTO Materia (codigo, descripcion, id_programa, cuatrimestre, precio, estado)
                OUTPUT INSERTED.id_materia
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_Curso, (
                Curso['codigo'],
                Curso['descripcion'],
                Curso['id_programa'],
                Curso['cuatrimestre'],
                Curso['precio'],
                Curso['estado']
            ))
            id_materia = cursor.fetchone()[0]

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Curso creado exitosamente (ID: {id_materia})"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "El código del curso ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear Curso: {str(e)}"

    def obtener_Curso(self):
        """Obtiene todos los Cursos activos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT e.id_materia, e.codigo, e.descripcion, e.id_programa,
                       e.cuatrimestre, e.precio, e.estado
                FROM Materia e
                INNER JOIN Programa p ON e.id_programa = p.id_programa
                WHERE p.estado = 'Activo'
                ORDER BY e.codigo
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            Curso = []
            for row in resultados:
                Curso.append({
                    'id_materia': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'id_programa': row[3],
                    'cuatrimestre': row[4],
                    'precio': row[5],
                    'estado': row[6],
                })

            cursor.close()
            conexion.close()
            return Curso, None

        except Exception as e:
            return None, f"Error al obtener Curso: {str(e)}"

    def obtener_Curso_por_id(self, id_Curso):
        """Obtiene un Curso por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            # CORREGIDO: espacio entre alias y columna, coma extra eliminada,
            # columnas traídas de la tabla correcta (e = Materia), WHERE corregido
            query = """
                SELECT e.id_materia, e.codigo, e.descripcion, e.id_programa,
                       e.cuatrimestre, e.precio, e.estado
                FROM Materia e
                INNER JOIN Programa p ON e.id_programa = p.id_programa
                WHERE e.id_materia = ?
            """
            cursor.execute(query, (id_Curso,))
            row = cursor.fetchone()

            if row:
                Curso = {
                    'id_materia': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'id_programa': row[3],
                    'cuatrimestre': row[4],
                    'precio': row[5],
                    'estado': row[6],
                }
            else:
                Curso = None

            cursor.close()
            conexion.close()
            return Curso, None

        except Exception as e:
            return None, f"Error al obtener Curso: {str(e)}"

    def actualizar_Curso(self, id_Curso, Curso):
        """Actualiza un Curso existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_materia FROM Materia WHERE id_materia = ?", (id_Curso,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Curso no encontrado"

            # CORREGIDO: un solo UPDATE, 7 columnas = 7 valores + 1 WHERE
            query_Curso = """
                UPDATE Materia
                SET codigo = ?, descripcion = ?,
                    id_programa = ?, cuatrimestre = ?,
                    precio = ?, estado = ?
                WHERE id_materia = ?
            """
            cursor.execute(query_Curso, (
                Curso['codigo'],
                Curso['descripcion'],
                Curso['id_programa'],
                Curso['cuatrimestre'],
                Curso['precio'],
                Curso['estado'],
                id_Curso
            ))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Curso actualizado exitosamente"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "El código del curso ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar Curso: {str(e)}"

    def eliminar_Curso(self, id_Curso):
        """Elimina un Curso de la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_materia FROM Materia WHERE id_materia = ?", (id_Curso,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Curso no encontrado"

            # CORREGIDO: un solo DELETE (Materia no tiene tabla dependiente propia)
            cursor.execute("DELETE FROM Materia WHERE id_materia = ?", (id_Curso,))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Curso eliminado permanentemente"

        except Exception as e:
            return False, f"Error al eliminar Curso: {str(e)}"

    def cambiar_estado(self, id_Curso, nuevo_estado):
        """Cambia el estado de un Curso"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_materia FROM Materia WHERE id_materia = ?", (id_Curso,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Curso no encontrado"

            query = "UPDATE Materia SET estado = ? WHERE id_materia = ?"
            cursor.execute(query, (nuevo_estado, id_Curso))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Estado cambiado a {nuevo_estado}"

        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
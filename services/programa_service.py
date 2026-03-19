import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc


class ProgramaService:

    def crear_programa(self, programa):
        """Crea un nuevo programa en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO Programa (codigo, descripcion, horario, precio_matricula, estado)
                OUTPUT INSERTED.id_programa
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                programa['codigo'],
                programa['descripcion'],
                programa.get('horario', ''),
                programa['precio_matricula'],
                programa.get('estado', 'Activo')
            ))
            id_programa = cursor.fetchone()[0]

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Programa creado exitosamente (ID: {id_programa})"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "El código del programa ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear programa: {str(e)}"

    def obtener_programas(self):
        """Obtiene todos los programas"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_programa, codigo, descripcion, horario, precio_matricula, estado
                FROM Programa
                ORDER BY descripcion
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            programas = []
            for row in resultados:
                programas.append({
                    'id_programa':     row[0],
                    'codigo':          row[1],
                    'descripcion':     row[2],
                    'horario':         row[3],
                    'precio_matricula':row[4],
                    'estado':          row[5]
                })

            cursor.close()
            conexion.close()
            return programas, None

        except Exception as e:
            return None, f"Error al obtener programas: {str(e)}"

    def obtener_programa_por_id(self, id_programa):
        """Obtiene un programa por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_programa, codigo, descripcion, horario, precio_matricula, estado
                FROM Programa
                WHERE id_programa = ?
            """
            cursor.execute(query, (id_programa,))
            row = cursor.fetchone()

            if row:
                programa = {
                    'id_programa':     row[0],
                    'codigo':          row[1],
                    'descripcion':     row[2],
                    'horario':         row[3],
                    'precio_matricula':row[4],
                    'estado':          row[5]
                }
            else:
                programa = None

            cursor.close()
            conexion.close()
            return programa, None

        except Exception as e:
            return None, f"Error al obtener programa: {str(e)}"

    def actualizar_programa(self, id_programa, programa):
        """Actualiza un programa existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_programa FROM Programa WHERE id_programa = ?",
                           (id_programa,))
            if not cursor.fetchone():
                return False, "Programa no encontrado"

            query = """
                UPDATE Programa
                SET codigo = ?, descripcion = ?, horario = ?, precio_matricula = ?, estado = ?
                WHERE id_programa = ?
            """
            cursor.execute(query, (
                programa['codigo'],
                programa['descripcion'],
                programa.get('horario', ''),
                programa['precio_matricula'],
                programa.get('estado', 'Activo'),
                id_programa
            ))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Programa actualizado exitosamente"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "El código del programa ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar programa: {str(e)}"

    def eliminar_programa(self, id_programa):
        """Elimina un programa de la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_programa FROM Programa WHERE id_programa = ?",
                           (id_programa,))
            if not cursor.fetchone():
                return False, "Programa no encontrado"

            cursor.execute("DELETE FROM Programa WHERE id_programa = ?", (id_programa,))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Programa eliminado exitosamente"

        except Exception as e:
            return False, f"Error al eliminar programa: {str(e)}"

    def cambiar_estado(self, id_programa, nuevo_estado):
        """Cambia el estado de un programa"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_programa FROM Programa WHERE id_programa = ?",
                           (id_programa,))
            if not cursor.fetchone():
                return False, "Programa no encontrado"

            cursor.execute("UPDATE Programa SET estado = ? WHERE id_programa = ?",
                           (nuevo_estado, id_programa))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Estado cambiado a {nuevo_estado}"

        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
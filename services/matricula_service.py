import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc

class MatriculaService:

    def crear_matricula(self, matricula):
        """Crea una nueva matrícula en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO Matricula (id_estudiante, id_programa, id_docente, fecha_matricula, periodo, estado)
                OUTPUT INSERTED.id_matricula
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                matricula['id_estudiante'],
                matricula['id_programa'],
                matricula['id_docente'],
                matricula['fecha_matricula'],
                matricula.get('periodo', ''),
                matricula.get('estado', 'Activo')
            ))
            id_matricula = cursor.fetchone()[0]

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Matrícula creada exitosamente (ID: {id_matricula})"

        except pyodbc.IntegrityError as e:
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear matrícula: {str(e)}"

    def obtener_matriculas(self):
        """Obtiene todas las matrículas con datos de estudiante, programa y docente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    m.id_matricula,
                    m.id_estudiante,
                    p.nombre_completo AS nombre_estudiante,
                    m.id_programa,
                    pr.descripcion AS nombre_programa,
                    m.id_docente,
                    pd.nombre_completo AS nombre_docente,
                    CONVERT(varchar(10), m.fecha_matricula, 23) AS fecha_matricula,
                    m.periodo,
                    m.estado
                FROM Matricula m
                INNER JOIN Estudiante e ON m.id_estudiante = e.id_estudiante
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                INNER JOIN Programa pr ON m.id_programa = pr.id_programa
                INNER JOIN Docente d ON m.id_docente = d.id_docente
                INNER JOIN Persona pd ON d.id_persona = pd.id_persona
                ORDER BY m.id_matricula DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            matriculas = []
            for row in resultados:
                matriculas.append({
                    'id_matricula': row[0],
                    'id_estudiante': row[1],
                    'nombre_estudiante': row[2],
                    'id_programa': row[3],
                    'nombre_programa': row[4],
                    'id_docente': row[5],
                    'nombre_docente': row[6],
                    'fecha': row[7],
                    'periodo': row[8],
                    'estado': row[9]
                })

            cursor.close()
            conexion.close()
            return matriculas, None

        except Exception as e:
            return None, f"Error al obtener matrículas: {str(e)}"

    def obtener_matricula_por_id(self, id_matricula):
        """Obtiene una matrícula por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    m.id_matricula,
                    m.id_estudiante,
                    p.nombre_completo AS nombre_estudiante,
                    m.id_programa,
                    pr.descripcion AS nombre_programa,
                    m.id_docente,
                    pd.nombre_completo AS nombre_docente,
                    CONVERT(varchar(10), m.fecha_matricula, 23) AS fecha_matricula,
                    m.periodo,
                    m.estado
                FROM Matricula m
                INNER JOIN Estudiante e ON m.id_estudiante = e.id_estudiante
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                INNER JOIN Programa pr ON m.id_programa = pr.id_programa
                INNER JOIN Docente d ON m.id_docente = d.id_docente
                INNER JOIN Persona pd ON d.id_persona = pd.id_persona
                WHERE m.id_matricula = ?
            """
            cursor.execute(query, (id_matricula,))
            row = cursor.fetchone()

            if row:
                matricula = {
                    'id_matricula': row[0],
                    'id_estudiante': row[1],
                    'nombre_estudiante': row[2],
                    'id_programa': row[3],
                    'nombre_programa': row[4],
                    'id_docente': row[5],
                    'nombre_docente': row[6],
                    'fecha': row[7],
                    'periodo': row[8],
                    'estado': row[9]
                }
            else:
                matricula = None

            cursor.close()
            conexion.close()
            return matricula, None

        except Exception as e:
            return None, f"Error al obtener matrícula: {str(e)}"

    def actualizar_matricula(self, id_matricula, matricula):
        """Actualiza una matrícula existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_matricula FROM Matricula WHERE id_matricula = ?", (id_matricula,))
            if not cursor.fetchone():
                return False, "Matrícula no encontrada"

            query = """
                UPDATE Matricula
                SET id_estudiante = ?, id_programa = ?, id_docente = ?,
                    fecha_matricula = ?, periodo = ?, estado = ?
                WHERE id_matricula = ?
            """
            cursor.execute(query, (
                matricula['id_estudiante'],
                matricula['id_programa'],
                matricula['id_docente'],
                matricula['fecha_matricula'],
                matricula.get('periodo', ''),
                matricula.get('estado', 'Activo'),
                id_matricula
            ))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Matrícula actualizada exitosamente"

        except pyodbc.IntegrityError as e:
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar matrícula: {str(e)}"

    def eliminar_matricula(self, id_matricula):
        """Elimina una matrícula de la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_matricula FROM Matricula WHERE id_matricula = ?", (id_matricula,))
            if not cursor.fetchone():
                return False, "Matrícula no encontrada"

            # Primero eliminar MatriculaMateria (FK depende de Matricula)
            cursor.execute("DELETE FROM MatriculaMateria WHERE id_matricula = ?", (id_matricula,))
            cursor.execute("DELETE FROM Matricula WHERE id_matricula = ?", (id_matricula,))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Matrícula eliminada permanentemente"

        except Exception as e:
            return False, f"Error al eliminar matrícula: {str(e)}"

    def cambiar_estado(self, id_matricula, nuevo_estado):
        """Cambia el estado de una matrícula"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_matricula FROM Matricula WHERE id_matricula = ?", (id_matricula,))
            if not cursor.fetchone():
                return False, "Matrícula no encontrada"

            cursor.execute("UPDATE Matricula SET estado = ? WHERE id_matricula = ?", (nuevo_estado, id_matricula))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Estado cambiado a {nuevo_estado}"

        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"

    def obtener_estudiantes_activos(self):
        """Retorna lista de estudiantes activos para el combo de la vista"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT e.id_estudiante, p.nombre_completo, e.carnet
                FROM Estudiante e
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                WHERE p.estado = 'Activo'
                ORDER BY p.nombre_completo
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            estudiantes = [{'id_estudiante': row[0], 'nombre': row[1], 'carnet': row[2]} for row in resultados]

            cursor.close()
            conexion.close()
            return estudiantes, None

        except Exception as e:
            return None, f"Error al obtener estudiantes: {str(e)}"

    def obtener_programas_activos(self):
        """Retorna lista de programas activos para el combo de la vista"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_programa, descripcion, codigo
                FROM Programa
                WHERE estado = 'Activo'
                ORDER BY descripcion
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            programas = [{'id_programa': row[0], 'descripcion': row[1], 'codigo': row[2]} for row in resultados]

            cursor.close()
            conexion.close()
            return programas, None

        except Exception as e:
            return None, f"Error al obtener programas: {str(e)}"

    def obtener_docentes_por_programa(self, id_programa):
        """Retorna docentes activos asignados a un programa — para el combo de docente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT d.id_docente, p.nombre_completo
                FROM Docente d
                INNER JOIN Persona p ON d.id_persona = p.id_persona
                INNER JOIN DocentePrograma dp ON d.id_docente = dp.id_docente
                WHERE dp.id_programa = ?
                AND p.estado = 'Activo'
                ORDER BY p.nombre_completo
            """
            cursor.execute(query, (id_programa,))
            resultados = cursor.fetchall()

            docentes = [{'id_docente': row[0], 'nombre': row[1]} for row in resultados]

            cursor.close()
            conexion.close()
            return docentes, None

        except Exception as e:
            return None, f"Error al obtener docentes: {str(e)}"

    def obtener_matriculas_por_programa(self, id_programa):
        """Retorna todos los estudiantes matriculados en un programa — para Consulta por Curso"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    m.id_matricula,
                    p.nombre_completo AS nombre_estudiante,
                    e.carnet,
                    pr.descripcion AS nombre_programa,
                    CONVERT(varchar(10), m.fecha_matricula, 23) AS fecha_matricula,
                    m.periodo,
                    m.estado
                FROM Matricula m
                INNER JOIN Estudiante e ON m.id_estudiante = e.id_estudiante
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                INNER JOIN Programa pr ON m.id_programa = pr.id_programa
                WHERE m.id_programa = ?
                ORDER BY p.nombre_completo
            """
            cursor.execute(query, (id_programa,))
            resultados = cursor.fetchall()

            matriculas = []
            for row in resultados:
                matriculas.append({
                    'id_matricula': row[0],
                    'nombre_estudiante': row[1],
                    'carnet': row[2],
                    'nombre_programa': row[3],
                    'fecha': row[4],
                    'periodo': row[5],
                    'estado': row[6]
                })

            cursor.close()
            conexion.close()
            return matriculas, None

        except Exception as e:
            return None, f"Error al obtener matrículas por programa: {str(e)}"
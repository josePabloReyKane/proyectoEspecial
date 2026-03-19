import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc


class AsignacionService:

    def crear_asignacion(self, asignacion):
        """Crea una nueva asignación docente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO AsignacionDocente (id_docente, id_programa, id_periodo, fecha_inicio, fecha_fin, id_estado)
                OUTPUT INSERTED.id_asignacion
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                asignacion['id_docente'],
                asignacion['id_programa'],
                asignacion['id_periodo'],
                asignacion['fecha_inicio'],
                asignacion['fecha_fin'],
                asignacion['id_estado']
            ))
            id_asignacion = cursor.fetchone()[0]

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Asignación creada exitosamente (ID: {id_asignacion})"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "Este docente ya está asignado a ese programa en el mismo periodo"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear asignación: {str(e)}"

    def obtener_asignaciones(self):
        """Obtiene todas las asignaciones con datos completos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    a.id_asignacion,
                    a.id_docente,
                    p.nombre_completo   AS nombre_docente,
                    a.id_programa,
                    pr.descripcion      AS nombre_programa,
                    a.id_periodo,
                    pe.codigo           AS codigo_periodo,
                    pe.descripcion      AS nombre_periodo,
                    CONVERT(varchar(10), a.fecha_inicio, 23) AS fecha_inicio,
                    CONVERT(varchar(10), a.fecha_fin,    23) AS fecha_fin,
                    a.id_estado,
                    ea.descripcion      AS nombre_estado
                FROM AsignacionDocente a
                INNER JOIN Docente d       ON a.id_docente  = d.id_docente
                INNER JOIN Persona p       ON d.id_persona  = p.id_persona
                INNER JOIN Programa pr     ON a.id_programa = pr.id_programa
                INNER JOIN Periodo pe      ON a.id_periodo  = pe.id_periodo
                INNER JOIN EstadoAsignacion ea ON a.id_estado = ea.id_estado
                ORDER BY a.id_asignacion DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            asignaciones = []
            for row in resultados:
                asignaciones.append({
                    'id_asignacion':  row[0],
                    'id_docente':     row[1],
                    'nombre_docente': row[2],
                    'id_programa':    row[3],
                    'nombre_programa':row[4],
                    'id_periodo':     row[5],
                    'codigo_periodo': row[6],
                    'nombre_periodo': row[7],
                    'fecha_inicio':   row[8],
                    'fecha_fin':      row[9],
                    'id_estado':      row[10],
                    'nombre_estado':  row[11]
                })

            cursor.close()
            conexion.close()
            return asignaciones, None

        except Exception as e:
            return None, f"Error al obtener asignaciones: {str(e)}"

    def obtener_asignacion_por_id(self, id_asignacion):
        """Obtiene una asignación por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    a.id_asignacion,
                    a.id_docente,
                    p.nombre_completo   AS nombre_docente,
                    a.id_programa,
                    pr.descripcion      AS nombre_programa,
                    a.id_periodo,
                    pe.codigo           AS codigo_periodo,
                    pe.descripcion      AS nombre_periodo,
                    CONVERT(varchar(10), a.fecha_inicio, 23) AS fecha_inicio,
                    CONVERT(varchar(10), a.fecha_fin,    23) AS fecha_fin,
                    a.id_estado,
                    ea.descripcion      AS nombre_estado
                FROM AsignacionDocente a
                INNER JOIN Docente d       ON a.id_docente  = d.id_docente
                INNER JOIN Persona p       ON d.id_persona  = p.id_persona
                INNER JOIN Programa pr     ON a.id_programa = pr.id_programa
                INNER JOIN Periodo pe      ON a.id_periodo  = pe.id_periodo
                INNER JOIN EstadoAsignacion ea ON a.id_estado = ea.id_estado
                WHERE a.id_asignacion = ?
            """
            cursor.execute(query, (id_asignacion,))
            row = cursor.fetchone()

            if row:
                asignacion = {
                    'id_asignacion':  row[0],
                    'id_docente':     row[1],
                    'nombre_docente': row[2],
                    'id_programa':    row[3],
                    'nombre_programa':row[4],
                    'id_periodo':     row[5],
                    'codigo_periodo': row[6],
                    'nombre_periodo': row[7],
                    'fecha_inicio':   row[8],
                    'fecha_fin':      row[9],
                    'id_estado':      row[10],
                    'nombre_estado':  row[11]
                }
            else:
                asignacion = None

            cursor.close()
            conexion.close()
            return asignacion, None

        except Exception as e:
            return None, f"Error al obtener asignación: {str(e)}"

    def actualizar_asignacion(self, id_asignacion, asignacion):
        """Actualiza una asignación existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_asignacion FROM AsignacionDocente WHERE id_asignacion = ?",
                           (id_asignacion,))
            if not cursor.fetchone():
                return False, "Asignación no encontrada"

            query = """
                UPDATE AsignacionDocente
                SET id_docente  = ?, id_programa = ?, id_periodo = ?,
                    fecha_inicio = ?, fecha_fin  = ?, id_estado  = ?
                WHERE id_asignacion = ?
            """
            cursor.execute(query, (
                asignacion['id_docente'],
                asignacion['id_programa'],
                asignacion['id_periodo'],
                asignacion['fecha_inicio'],
                asignacion['fecha_fin'],
                asignacion['id_estado'],
                id_asignacion
            ))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Asignación actualizada exitosamente"

        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e).upper():
                return False, "Este docente ya está asignado a ese programa en el mismo periodo"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar asignación: {str(e)}"

    def eliminar_asignacion(self, id_asignacion):
        """Elimina una asignación"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_asignacion FROM AsignacionDocente WHERE id_asignacion = ?",
                           (id_asignacion,))
            if not cursor.fetchone():
                return False, "Asignación no encontrada"

            cursor.execute("DELETE FROM AsignacionDocente WHERE id_asignacion = ?",
                           (id_asignacion,))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Asignación eliminada permanentemente"

        except Exception as e:
            return False, f"Error al eliminar asignación: {str(e)}"

    def cambiar_estado(self, id_asignacion, id_estado):
        """Cambia el estado de una asignación"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_asignacion FROM AsignacionDocente WHERE id_asignacion = ?",
                           (id_asignacion,))
            if not cursor.fetchone():
                return False, "Asignación no encontrada"

            cursor.execute("UPDATE AsignacionDocente SET id_estado = ? WHERE id_asignacion = ?",
                           (id_estado, id_asignacion))

            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Estado actualizado exitosamente"

        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"

    def obtener_periodos(self):
        """Retorna los periodos activos para el combo"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_periodo, codigo, descripcion, fecha_inicio, fecha_fin
                FROM Periodo
                WHERE estado = 'Activo'
                ORDER BY fecha_inicio
            """)
            resultados = cursor.fetchall()

            periodos = []
            for row in resultados:
                periodos.append({
                    'id_periodo':   row[0],
                    'codigo':       row[1],
                    'descripcion':  row[2],
                    'fecha_inicio': str(row[3]),
                    'fecha_fin':    str(row[4])
                })

            cursor.close()
            conexion.close()
            return periodos, None

        except Exception as e:
            return None, f"Error al obtener periodos: {str(e)}"

    def obtener_estados(self):
        """Retorna los estados desde tabla maestra para el combo"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_estado, codigo, descripcion
                FROM EstadoAsignacion
                WHERE estado = 'Activo'
                ORDER BY descripcion
            """)
            resultados = cursor.fetchall()

            estados = []
            for row in resultados:
                estados.append({
                    'id_estado':   row[0],
                    'codigo':      row[1],
                    'descripcion': row[2]
                })

            cursor.close()
            conexion.close()
            return estados, None

        except Exception as e:
            return None, f"Error al obtener estados: {str(e)}"

    def obtener_docentes_activos(self):
        """Retorna docentes activos para el combo"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT d.id_docente, p.nombre_completo
                FROM Docente d
                INNER JOIN Persona p ON d.id_persona = p.id_persona
                WHERE p.estado = 'Activo'
                ORDER BY p.nombre_completo
            """)
            resultados = cursor.fetchall()

            docentes = [{'id_docente': row[0], 'nombre': row[1]} for row in resultados]

            cursor.close()
            conexion.close()
            return docentes, None

        except Exception as e:
            return None, f"Error al obtener docentes: {str(e)}"

    def obtener_programas_activos(self):
        """Retorna programas activos para el combo"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_programa, codigo, descripcion
                FROM Programa
                WHERE estado = 'Activo'
                ORDER BY descripcion
            """)
            resultados = cursor.fetchall()

            programas = [{'id_programa': row[0], 'codigo': row[1], 'descripcion': row[2]}
                         for row in resultados]

            cursor.close()
            conexion.close()
            return programas, None

        except Exception as e:
            return None, f"Error al obtener programas: {str(e)}"
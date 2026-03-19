import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from config.database import ConexionDB
import pyodbc
 
class DocenteService:
 
    def crear_docente(self, docente):
        """Crea un nuevo docente en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            # Insertar en Persona
            query_persona = """
            INSERT INTO Persona (identificacion, nombre_completo, email, telefono, direccion, estado)
            OUTPUT INSERTED.id_persona
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_persona, (
                docente['identificacion'],
                docente['nombre_completo'],
                docente.get('email', ''),
                docente.get('telefono', ''),
                docente.get('direccion', ''),
                docente.get('estado', 'Activo')
            ))
            id_persona = cursor.fetchone()[0]
 
            # Insertar en Docente
            query_docente = """
            INSERT INTO Docente (id_persona, id_profesion, especialidad)
            OUTPUT INSERTED.id_docente
            VALUES (?, ?, ?)
            """
            cursor.execute(query_docente, (
                id_persona,
                docente['id_profesion'],
                docente.get('especialidad', '')
            ))
            id_docente = cursor.fetchone()[0]

            # Asignar automáticamente a todos los programas activos
            cursor.execute("SELECT id_programa FROM Programa WHERE estado = 'Activo'")
            programas = cursor.fetchall()
            for prog in programas:
                cursor.execute(
                    "INSERT INTO DocentePrograma (id_docente, id_programa) VALUES (?, ?)",
                    (id_docente, prog[0])
                )
 
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Docente creado exitosamente"
 
        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e):
                return False, "La identificación ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear docente: {str(e)}"
 
    def obtener_docentes(self):
        """Obtiene todos los docentes"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            query = """
            SELECT d.id_docente, p.identificacion, p.nombre_completo,
                   p.email, p.telefono, p.direccion,
                   pr.descripcion as profesion, d.especialidad, p.estado,
                   p.id_persona, d.id_profesion
            FROM Docente d
            INNER JOIN Persona p ON d.id_persona = p.id_persona
            INNER JOIN Profesion pr ON d.id_profesion = pr.id_profesion
            ORDER BY p.nombre_completo
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
 
            docentes = []
            for row in resultados:
                docentes.append({
                    'id_docente': row[0],
                    'identificacion': row[1],
                    'nombre_completo': row[2],
                    'email': row[3],
                    'telefono': row[4],
                    'direccion': row[5],
                    'profesion': row[6],
                    'especialidad': row[7],
                    'estado': row[8],
                    'id_persona': row[9],
                    'id_profesion': row[10]
                })
 
            cursor.close()
            conexion.close()
            return docentes, None
 
        except Exception as e:
            return None, f"Error al obtener docentes: {str(e)}"
 
    def obtener_profesiones(self):
        """Obtiene todas las profesiones activas"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            query = "SELECT id_profesion, codigo, descripcion FROM Profesion WHERE estado = 'Activo' ORDER BY descripcion"
            cursor.execute(query)
            resultados = cursor.fetchall()
 
            profesiones = []
            for row in resultados:
                profesiones.append({
                    'id_profesion': row[0],
                    'codigo': row[1],
                    'descripcion': row[2]
                })
 
            cursor.close()
            conexion.close()
            return profesiones, None
 
        except Exception as e:
            return None, f"Error al obtener profesiones: {str(e)}"
 
    def obtener_docente_por_id(self, id_docente):
        """Obtiene un docente por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            query = """
            SELECT d.id_docente, p.identificacion, p.nombre_completo,
                   p.direccion, p.telefono, p.email,
                   d.id_profesion, d.especialidad, p.estado,
                   p.id_persona
            FROM Docente d
            INNER JOIN Persona p ON d.id_persona = p.id_persona
            WHERE d.id_docente = ?
            """
            cursor.execute(query, (id_docente,))
            row = cursor.fetchone()
 
            if row:
                docente = {
                    'id_docente': row[0],
                    'identificacion': row[1],
                    'nombre_completo': row[2],
                    'direccion': row[3],
                    'telefono': row[4],
                    'email': row[5],
                    'id_profesion': row[6],
                    'especialidad': row[7],
                    'estado': row[8],
                    'id_persona': row[9]
                }
            else:
                docente = None
 
            cursor.close()
            conexion.close()
            return docente, None
 
        except Exception as e:
            return None, f"Error al obtener docente: {str(e)}"
 
    def actualizar_docente(self, id_docente, docente):
        """Actualiza un docente existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            cursor.execute("SELECT id_persona FROM Docente WHERE id_docente = ?", (id_docente,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Docente no encontrado"
            id_persona = resultado[0]
 
            query_persona = """
            UPDATE Persona
            SET identificacion = ?, nombre_completo = ?, email = ?,
                telefono = ?, direccion = ?, estado = ?
            WHERE id_persona = ?
            """
            cursor.execute(query_persona, (
                docente['identificacion'],
                docente['nombre_completo'],
                docente.get('email', ''),
                docente.get('telefono', ''),
                docente.get('direccion', ''),
                docente.get('estado', 'Activo'),
                id_persona
            ))
 
            query_docente = """
            UPDATE Docente
            SET id_profesion = ?, especialidad = ?
            WHERE id_docente = ?
            """
            cursor.execute(query_docente, (
                docente['id_profesion'],
                docente.get('especialidad', ''),
                id_docente
            ))
 
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Docente actualizado exitosamente"
 
        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e):
                return False, "La identificación ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar docente: {str(e)}"
 
    def eliminar_docente(self, id_docente):
        """Elimina físicamente un docente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            cursor.execute("BEGIN TRANSACTION")
 
            cursor.execute("SELECT id_persona FROM Docente WHERE id_docente = ?", (id_docente,))
            resultado = cursor.fetchone()
            if not resultado:
                cursor.execute("ROLLBACK TRANSACTION")
                return False, "Docente no encontrado"
            id_persona = resultado[0]

            # Eliminar asignaciones de programas primero (FK)
            cursor.execute("DELETE FROM DocentePrograma WHERE id_docente = ?", (id_docente,))

            # Eliminar de Docente
            cursor.execute("DELETE FROM Docente WHERE id_docente = ?", (id_docente,))
 
            # Eliminar de Persona
            cursor.execute("DELETE FROM Persona WHERE id_persona = ?", (id_persona,))
 
            cursor.execute("COMMIT TRANSACTION")
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Docente eliminado permanentemente"
 
        except Exception as e:
            try:
                cursor.execute("ROLLBACK TRANSACTION")
            except:
                pass
            return False, f"Error al eliminar docente: {str(e)}"
 
    def cambiar_estado(self, id_docente, nuevo_estado):
        """Cambia el estado de un docente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
 
            cursor.execute("SELECT id_persona FROM Docente WHERE id_docente = ?", (id_docente,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Docente no encontrado"
            id_persona = resultado[0]
 
            query = "UPDATE Persona SET estado = ? WHERE id_persona = ?"
            cursor.execute(query, (nuevo_estado, id_persona))
 
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Estado cambiado a {nuevo_estado}"
 
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
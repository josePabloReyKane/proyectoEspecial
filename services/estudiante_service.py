import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
import pyodbc
from services.historial_service import HistorialService
class EstudianteService:
    
    def crear_estudiante(self, estudiante):
        """Crea un nuevo estudiante en la base de datos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            # Primero insertar en Persona
            query_persona = """
                INSERT INTO Persona (identificacion, nombre_completo, email, telefono, direccion, estado)
                OUTPUT INSERTED.id_persona
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_persona, (
                estudiante['identificacion'],
                estudiante['nombre_completo'],
                estudiante['email'],
                estudiante['telefono'],
                estudiante['direccion'],
                estudiante['estado']
            ))
            id_persona = cursor.fetchone()[0]
            
            # Luego insertar en Estudiante
            query_estudiante = """
                INSERT INTO Estudiante (id_persona, carnet, fecha_nacimiento)
                VALUES (?, ?, ?)
            """
            cursor.execute(query_estudiante, (
                id_persona,
                estudiante['carnet'],
                estudiante.get('fecha_nacimiento', None)
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Estudiante creado exitosamente"
            
        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e):
                return False, "El carnet o identificación ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al crear estudiante: {str(e)}"
    
    def obtener_estudiantes(self):
        """Obtiene todos los estudiantes activos"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            query = """
                SELECT e.id_estudiante, e.carnet, p.identificacion, p.nombre_completo, 
                       p.direccion, p.telefono, p.email, e.fecha_nacimiento, p.estado,
                       p.id_persona
                FROM Estudiante e
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                ORDER BY p.nombre_completo
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            estudiantes = []
            for row in resultados:
                estudiantes.append({
                    'id_estudiante': row[0],
                    'carnet': row[1],
                    'identificacion': row[2],
                    'nombre_completo': row[3],
                    'direccion': row[4],
                    'telefono': row[5],
                    'email': row[6],
                    'fecha_nacimiento': row[7],
                    'estado': row[8],
                    'id_persona': row[9]
                })
            
            cursor.close()
            conexion.close()
            return estudiantes, None
            
        except Exception as e:
            return None, f"Error al obtener estudiantes: {str(e)}"
    
    def obtener_estudiante_por_id(self, id_estudiante):
        """Obtiene un estudiante por su ID"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            query = """
                SELECT e.id_estudiante, e.carnet, p.identificacion, p.nombre_completo, 
                       p.direccion, p.telefono, p.email, e.fecha_nacimiento, p.estado,
                       p.id_persona
                FROM Estudiante e
                INNER JOIN Persona p ON e.id_persona = p.id_persona
                WHERE e.id_estudiante = ?
            """
            cursor.execute(query, (id_estudiante,))
            row = cursor.fetchone()
            
            if row:
                estudiante = {
                    'id_estudiante': row[0],
                    'carnet': row[1],
                    'identificacion': row[2],
                    'nombre_completo': row[3],
                    'direccion': row[4],
                    'telefono': row[5],
                    'email': row[6],
                    'fecha_nacimiento': row[7],
                    'estado': row[8],
                    'id_persona': row[9]
                }
            else:
                estudiante = None
            
            cursor.close()
            conexion.close()
            return estudiante, None
            
        except Exception as e:
            return None, f"Error al obtener estudiante: {str(e)}"
    
    def actualizar_estudiante(self, id_estudiante, estudiante):
        """Actualiza un estudiante existente"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            # Obtener id_persona del estudiante
            cursor.execute("SELECT id_persona FROM Estudiante WHERE id_estudiante = ?", (id_estudiante,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Estudiante no encontrado"
            id_persona = resultado[0]
            
            # Actualizar Persona
            query_persona = """
                UPDATE Persona 
                SET identificacion = ?, nombre_completo = ?, email = ?, 
                    telefono = ?, direccion = ?, estado = ?
                WHERE id_persona = ?
            """
            cursor.execute(query_persona, (
                estudiante['identificacion'],
                estudiante['nombre_completo'],
                estudiante['email'],
                estudiante['telefono'],
                estudiante['direccion'],
                estudiante['estado'],
                id_persona
            ))
            
            # Actualizar Estudiante
            query_estudiante = """
                UPDATE Estudiante 
                SET carnet = ?, fecha_nacimiento = ?
                WHERE id_estudiante = ?
            """
            cursor.execute(query_estudiante, (
                estudiante['carnet'],
                estudiante.get('fecha_nacimiento', None),
                id_estudiante
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Estudiante actualizado exitosamente"
            
        except pyodbc.IntegrityError as e:
            if 'UNIQUE' in str(e):
                return False, "El carnet o identificación ya existe"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            return False, f"Error al actualizar estudiante: {str(e)}"
    
    def eliminar_estudiante(self, id_estudiante):
        """Elimina físicamente un estudiante de ambas tablas"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            # Iniciar transacción
            cursor.execute("BEGIN TRANSACTION")
            
            # Obtener id_persona del estudiante
            cursor.execute("SELECT id_persona FROM Estudiante WHERE id_estudiante = ?", (id_estudiante,))
            resultado = cursor.fetchone()
            if not resultado:
                cursor.execute("ROLLBACK TRANSACTION")
                return False, "Estudiante no encontrado"
            id_persona = resultado[0]
            
            # Eliminar de Estudiante primero (por la FK)
            cursor.execute("DELETE FROM Estudiante WHERE id_estudiante = ?", (id_estudiante,))
            
            # Eliminar de Persona
            cursor.execute("DELETE FROM Persona WHERE id_persona = ?", (id_persona,))
            
            # Confirmar transacción
            cursor.execute("COMMIT TRANSACTION")
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, "Estudiante eliminado permanentemente"
            
        except Exception as e:
            # Revertir en caso de error
            try:
                cursor.execute("ROLLBACK TRANSACTION")
            except:
                pass
            return False, f"Error al eliminar estudiante: {str(e)}"
    
    def cambiar_estado(self, id_estudiante, nuevo_estado):
        """Cambia el estado de un estudiante"""
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            # Obtener id_persona del estudiante
            cursor.execute("SELECT id_persona FROM Estudiante WHERE id_estudiante = ?", (id_estudiante,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Estudiante no encontrado"
            id_persona = resultado[0]
            
            query = "UPDATE Persona SET estado = ? WHERE id_persona = ?"
            cursor.execute(query, (nuevo_estado, id_persona))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Estado cambiado a {nuevo_estado}"
            
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
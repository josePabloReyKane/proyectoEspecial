import sys
import os

# Agregar la ruta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from services.historial_service import HistorialService
class UsuarioService:
    def autenticar(self, usuario, password):
        try:
            conexion = ConexionDB.obtener_conexion()
            cursor = conexion.cursor()
            
            query = """
                SELECT u.id_usuario, u.id_persona, p.nombre_completo, u.id_rol
                FROM Usuario u
                INNER JOIN Persona p ON u.id_persona = p.id_persona
                WHERE u.usuario = ? AND u.contrasena = ? AND u.estado = 'Activo'
            """
            
            cursor.execute(query, (usuario, password))
            resultado = cursor.fetchone()
            
            cursor.close()
            conexion.close()
            
            if resultado:
                return {
                    "success": True,
                    "mensaje": "Autenticación exitosa",
                    "nombre_persona": resultado[2],
                    "id_usuario": resultado[0],
                    "id_persona": resultado[1],
                    "id_rol": resultado[3]
                }
            else:
                return {
                    "success": False,
                    "mensaje": "Usuario o contraseña incorrectos"
                }
                
        except Exception as e:
            return {
                "success": False,
                "mensaje": f"Error: {str(e)}"
            }
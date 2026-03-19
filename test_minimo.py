import sys
import os

print("=== DIAGNÓSTICO ===")
print(f"Directorio actual: {os.getcwd()}")
print(f"Archivo services/usuario_service.py existe: {os.path.exists('services/usuario_service.py')}")

print("\n--- Leyendo archivo ---")
try:
    with open('services/usuario_service.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
        print("Primeras 200 caracteres:")
        print(contenido[:200])
        print("\n¿La clase 'UsuarioService' está en el archivo?")
        print(f"'class UsuarioService' encontrado: {'class UsuarioService' in contenido}")
        print(f"'UsuarioService' (como texto) encontrado: {'UsuarioService' in contenido}")
except Exception as e:
    print(f"Error leyendo archivo: {e}")

print("\n--- Intentando importar ---")
try:
    # Importar el módulo completo
    import services.usuario_service as mod
    print("✅ Módulo importado")
    print(f"Contenido del módulo: {dir(mod)}")
    
    # Intentar obtener la clase
    if hasattr(mod, 'UsuarioService'):
        print("✅ Clase UsuarioService encontrada en el módulo")
        cls = getattr(mod, 'UsuarioService')
        print(f"Tipo de clase: {type(cls)}")
    else:
        print("❌ Clase UsuarioService NO encontrada en el módulo")
        
except Exception as e:
    print(f"❌ Error importando: {e}")
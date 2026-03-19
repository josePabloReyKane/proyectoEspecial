import pyodbc
import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox, filedialog
#import MENU
#from PIL import Image, ImageTk, ImageDraw # Para soportar JPG y redimensionar

# Configuración de conexión
SERVER = "KENNETH\PROYECTO"   # Cambia según tu instancia
DATABASE = "Universidad"
DRIVER = "ODBC Driver 17 for SQL Server"

# Función para conectarse a SQL Server usando credenciales ingresadas
def conectar_sql(usuario, contrasena):
    try:
        conexion = pyodbc.connect(
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={usuario};"
            f"PWD={contrasena};"
            "TrustServerCertificate=yes;"
        )
        return conexion
    except pyodbc.OperationalError as e:
        messagebox.showerror("Error de conexión",
                            f"No se pudo conectar al servidor SQL.\n\nDetalle técnico:\n{str(e)}")
        return None
    except Exception as e:
        messagebox.showerror("ERROR", f"Ocurrió un error al intentar conectar:\n{str(e)}")
        return None

# Función de login
def login():
    usuario_ingresado = entry_usuario.get()
    contrasena_ingresada = entry_contrasena.get()

    if not usuario_ingresado or not contrasena_ingresada:
        messagebox.showerror("Error", "Por favor ingresa un nombre de usuario y una contraseña.")
        return

    conn = conectar_sql(usuario_ingresado, contrasena_ingresada)

    if conn:
        cursor = conn.cursor()
        try:
            # Ejecuta el procedimiento almacenado que valida el usuario
            cursor.execute("EXEC ValidarUsuario ?, ?", (usuario_ingresado, contrasena_ingresada))
            resultado = cursor.fetchone()

            if resultado:
                mensaje = resultado[0]
                if mensaje == 'Acceso permitido':
                    messagebox.showinfo("Acceso", mensaje)
                else:
                    messagebox.showerror("Error", mensaje)
            else:
                messagebox.showerror("Error", "No se recibió respuesta del procedimiento almacenado.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al validar el usuario: {e}")
        finally:
            cursor.close()
            conn.close()


# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("SIS_UNIVERSITARIO")
ventana.geometry("450x225")   # un poco más ancho para la foto
ventana.resizable(False,False)
ventana.configure(bg="#3582C5")

# Función para cargar la foto de perfil
def cargar_foto():
    ruta_imagen = filedialog.askopenfilename(
        title="Escoger foto de perfil",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if ruta_imagen:
        try:
            # Abrir y redimensionar con Pillow
            img = Image.open(ruta_imagen).resize((100, 100))

            # Crear máscara circular
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)

            # Aplicar máscara para recortar en círculo
            img = Image.composite(img, Image.new("RGB", img.size, (0, 0, 0)), mask)

            foto = ImageTk.PhotoImage(img)
            label_foto.config(image=foto)
            label_foto.image = foto  # Mantener referencia
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo cargar la imagen:\n{e}")

# Campo Usuario
label_usuario = tk.Label(
    ventana, text="Usuario:",
    font=("Arial", 12, "bold"),
    bg="#3582C5", fg="#FFFFFF"
)
label_usuario.grid(row=0, column=0, padx=10, pady=10, sticky="e")

entry_usuario = tk.Entry(
    ventana, font=("Arial", 12),
    bg="white", fg="black"
)
entry_usuario.grid(row=0, column=1, padx=10, pady=10)

# Campo Contraseña
label_contrasena = tk.Label(
    ventana, text="Contraseña:",
    font=("Arial", 12, "bold"),
    bg="#3582C5", fg="#FFFFFF"
)
label_contrasena.grid(row=1, column=0, padx=10, pady=10, sticky="e")

entry_contrasena = tk.Entry(
    ventana, show="*",
    font=("Arial", 12),
    bg="white", fg="black"
)
entry_contrasena.grid(row=1, column=1, padx=10, pady=10)

# Foto de perfil a la derecha
label_foto = tk.Label(ventana, bg="#3582C5")
label_foto.grid(row=0, column=2, rowspan=2, padx=20, pady=10)

# Frame para centrar los botones (debajo de los campos)
frame_botones = tk.Frame(ventana, bg="#3582C5")
frame_botones.grid(row=3, column=0, columnspan=3, pady=20)

# Botón Login
boton_login = tk.Button(
    frame_botones, text="ACEPTAR",
    font=("Arial", 12, "bold"),
    bg="#1FAC82", fg="white",
    activebackground="#1E5A7B",
    relief=tk.RAISED, bd=3,
    command=lambda: messagebox.showinfo("Login", "Acceso Autorizado")
)
boton_login.pack(side="left", padx=10)

# Botón Cancelar
boton_cancelar = tk.Button(
    frame_botones, text="CANCELAR",
    font=("Arial", 12, "bold"),
    bg="#A93030", fg="white",
    activebackground="#7B1E1E",
    relief=tk.RAISED, bd=3,
    command=ventana.destroy
)
boton_cancelar.pack(side="left", padx=10)

# Botón Subir Foto (junto a Cancelar)
boton_foto = tk.Button(
    frame_botones, text="Subir foto de perfil",
    font=("Arial", 10, "bold"),
    bg="#B0BC00", fg="white",
    command=cargar_foto
)
boton_foto.pack(side="left", padx=10)
ventana.mainloop()
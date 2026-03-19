import sys
import os

# Agregar la ruta raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from services.usuario_service import UsuarioService

class LoginView:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Universidad")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        # Centrar la ventana
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(root, text="SISTEMA UNIVERSITARIO", font=("Arial", 12, "bold")).pack(pady=10)

        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Usuario:").grid(row=0, column=0, pady=5, sticky="e")
        self.usuario_entry = tk.Entry(frame)
        self.usuario_entry.grid(row=0, column=1, pady=5, padx=5)
        self.usuario_entry.focus()

        tk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        self.password_entry.bind('<Return>', lambda event: self.login())

        tk.Button(root, text="Ingresar", command=self.login, width=15).pack(pady=10)

    def login(self):
        usuario = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not usuario or not password:
            messagebox.showwarning("Advertencia", "Debe ingresar usuario y contraseña")
            return
            
        service = UsuarioService()
        resultado = service.autenticar(usuario, password)
        
        if resultado["success"]:
            messagebox.showinfo("Bienvenido", f"¡Bienvenido al sistema {resultado['nombre_persona']}!")
            self.root.destroy()
            
            # Importar MenuView desde views
            from views.menu_view import MenuView
            root_menu = tk.Tk()
            app_menu = MenuView(root_menu)
            root_menu.mainloop()
        else:
            messagebox.showerror("Error", resultado["mensaje"])
            self.usuario_entry.focus()
            self.usuario_entry.select_range(0, tk.END)
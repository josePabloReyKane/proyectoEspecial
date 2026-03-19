import sys
import os

# Agregar la ruta raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox

class MenuView:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal - Universidad")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        # Centrar la ventana
        self.root.eval('tk::PlaceWindow . center')

        # Configurar color de fondo
        self.root.configure(bg='#f0f0f0')

        # Encabezado con logo simulado
        header_frame = tk.Frame(root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="UNIVERSIDAD",
                font=("Arial", 20, "bold"),
                bg='#2c3e50',
                fg='white').pack(expand=True)

        tk.Label(header_frame, text="Sistema de Gestión Académica",
                font=("Arial", 10),
                bg='#2c3e50',
                fg='#ecf0f1').pack()

        # Frame para el contenido principal
        content_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para los botones de menú
        menu_frame = tk.LabelFrame(content_frame,
                                  text="MÓDULOS DEL SISTEMA",
                                  font=("Arial", 12, "bold"),
                                  bg='#f0f0f0',
                                  padx=20,
                                  pady=15)
        menu_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid para los botones
        for i in range(3):
            menu_frame.grid_columnconfigure(i, weight=1, uniform="col")

        # Botones de menú — se agregó Asignación Docente
        botones = [
            ("📚 Cursos",              self.open_cursos,      "#3498db"),
            ("🎓 Programas",          self.open_programas,   "#2239e6"),
            ("👨‍🏫 Docentes",            self.open_docentes,    "#e67e22"),
            ("👨‍🎓 Estudiantes",          self.open_estudiantes, "#27ae60"),
            ("📝 Matrículas",           self.open_matriculas,  "#9b59b6"),
            ("📊 Reportes",             self.open_reportes,    "#e74c3c"),
            ("📊 Historial",             self.open_historial,    "#e74c3c"),
            ("🗂️ Asignación Docente",   self.open_asignacion,  "#16a085"),
            ("⚙️ Configuración",        self.open_config,      "#95a5a6"),
        ]

        # Posicionar botones en grid de 3 columnas
        for i, (texto, comando, color) in enumerate(botones):
            row = i // 3
            col = i % 3

            btn = tk.Button(menu_frame,
                          text=texto,
                          command=comando,
                          bg=color,
                          fg='white',
                          font=("Arial", 11, "bold"),
                          width=15,
                          height=2,
                          relief=tk.RAISED,
                          bd=3,
                          cursor="hand2")
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_enter(e, b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_leave(e, b, c))

        # Frame para información del usuario
        info_frame = tk.Frame(content_frame, bg='#f0f0f0', pady=10)
        info_frame.pack(fill=tk.X)

        tk.Label(info_frame,
                text="Usuario: Administrador",
                font=("Arial", 9),
                bg='#f0f0f0',
                fg='#7f8c8d').pack(side=tk.LEFT, padx=10)

        # Botón salir
        btn_salir = tk.Button(content_frame,
                            text="❌ Salir del Sistema",
                            command=self.salir,
                            bg="#c0392b",
                            fg='white',
                            font=("Arial", 11, "bold"),
                            width=20,
                            height=1,
                            relief=tk.RAISED,
                            bd=3,
                            cursor="hand2")
        btn_salir.pack(pady=10)

        # Efecto hover para botón salir
        btn_salir.bind("<Enter>", lambda e: btn_salir.configure(bg="#e74c3c"))
        btn_salir.bind("<Leave>", lambda e: btn_salir.configure(bg="#c0392b"))

        # Barra de estado
        status_bar = tk.Label(root,
                            text="© 2026 Universidad - Sistema de Gestión Académica v1.0",
                            bd=1,
                            relief=tk.SUNKEN,
                            anchor=tk.W,
                            bg='#bdc3c7',
                            fg='#2c3e50',
                            font=("Arial", 8))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_enter(self, event, button, color):
        button.configure(bg=self.lighten_color(color))

    def on_leave(self, event, button, color):
        button.configure(bg=color)

    def lighten_color(self, color):
        colors = {
            "#3498db": "#5dade2",
            "#e67e22": "#f39c12",
            "#27ae60": "#2ecc71",
            "#9b59b6": "#af7ac5",
            "#e74c3c": "#ec7063",
            "#16a085": "#1abc9c",
            "#95a5a6": "#bdc3c7",
        }
        return colors.get(color, color)

    def open_cursos(self):
        try:
            from views.curso_view import CursosView
            CursosView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de cursos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir cursos: {str(e)}")

    def open_programas(self):
        try:
            from views.programa_view import ProgramaView
            ProgramaView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de programas: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir programas: {str(e)}")
    def open_historial(self):
        try:
            from views.historial_view import HistorialView
            HistorialView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de historial: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial: {str(e)}")
            
    def open_docentes(self):
        try:
            from views.docente_view import DocenteView
            DocenteView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de docentes: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir docentes: {str(e)}")

    def open_estudiantes(self):
        try:
            from views.estudiante_view import EstudianteView
            EstudianteView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de estudiantes: {str(e)}")
            self.crear_modulo_basico("Estudiantes")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir estudiantes: {str(e)}")

    def open_matriculas(self):
        try:
            from views.matricula_view import MatriculaView
            MatriculaView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de matrículas: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir matrículas: {str(e)}")

    def open_reportes(self):
        try:
            from views.reporte_view import ReporteView
            ReporteView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de reportes: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir reportes: {str(e)}")

    def open_asignacion(self):
        """Abrir módulo de asignación de docentes"""
        try:
            from views.asignacion_view import AsignacionView
            AsignacionView(tk.Toplevel(self.root))
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de asignación: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir asignación: {str(e)}")

    def open_config(self):
        messagebox.showinfo("Configuración", "Módulo de Configuración - En desarrollo")

    def crear_modulo_basico(self, modulo):
        respuesta = messagebox.askyesno(
            "Módulo no encontrado",
            f"El módulo de {modulo} no está implementado.\n¿Desea crear una versión básica?"
        )
        if respuesta:
            if modulo == "Estudiantes":
                self.crear_vista_estudiante_basica()

    def crear_vista_estudiante_basica(self):
        try:
            ventana = tk.Toplevel(self.root)
            ventana.title("Gestión de Estudiantes - Versión Básica")
            ventana.geometry("400x300")

            tk.Label(ventana, text="MÓDULO DE ESTUDIANTES",
                    font=("Arial", 14, "bold")).pack(pady=20)

            tk.Label(ventana,
                    text="Versión básica temporal\n\nLos módulos completos estarán disponibles\nen la próxima actualización.",
                    font=("Arial", 10),
                    justify=tk.CENTER).pack(pady=20)

            tk.Button(ventana,
                     text="Cerrar",
                     command=ventana.destroy,
                     bg="#3498db",
                     fg="white").pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la vista básica: {str(e)}")

    def salir(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea salir del sistema?"):
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MenuView(root)
    root.mainloop()
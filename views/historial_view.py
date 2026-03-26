import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from services.historial_service import HistorialService


class HistorialView:
    def __init__(self, root):
        self.root = root
        self.root.title("Historial de movimient")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.service = HistorialService()
        self._programas = []

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_historial()

    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="REPORTE DE HISTORIAL",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        # ── FILTRO ────────────────────────────────────────────
        filter_frame = ttk.LabelFrame(main_frame, text="📌 Filtro", padding="12")
        filter_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(filter_frame, text="Mostrar todos",
                   command=self.mostrar_todos).pack(side=tk.LEFT, padx=4)

        # GRID DE RESULTADOS
        tree_frame = ttk.LabelFrame(main_frame, text="📊 Historial", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id_tipo_movimiento', 'codigo', 'descripcion', 'estado')
        headers = ['id_tipo_movimiento', 'Codigo', 'Descripcion', 'Estado']
        widths   = [200, 90, 200, 110, 80, 90]

        container = ttk.Frame(tree_frame)
        container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(container, columns=columns, show='headings', height=16)
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, minwidth=60)

        vsb = ttk.Scrollbar(container, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure('oddrow',  background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='white')

        # BARRA INFERIOR
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(nav_frame, text="⬅️ Volver al Menú", command=self.volver_menu,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  width=16, relief=tk.RAISED, bd=2, cursor="hand2").pack(side=tk.LEFT, padx=6)

        self.contador_label = tk.Label(nav_frame, text="Total: 0 registros",
                                       font=("Arial", 9), fg="#7f8c8d")
        self.contador_label.pack(side=tk.RIGHT, padx=8)

        self.status_bar = tk.Label(main_frame, text="✅ Listo", bd=1,
                                   relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#ecf0f1', fg='#2c3e50', font=("Arial", 8))
        self.status_bar.pack(fill=tk.X, pady=(8, 0))

    # CARGA DE DATOS

    def cargar_historial(self):
        try:
            programas, error = self.service.obtener_movimiento()
            
            if error:
                messagebox.showerror("Error", f"No se pudieron cargar el historial:\n{error}")
                self.mostrar_estado(f"Error al cargar historial", "error")
                self._programas = []
                return
                
            self._programas = programas or []
            
            # Poblar el Treeview automáticamente al cargar
            self._poblar_tree(self._programas, modo='todos')
            
            # Actualizar contador
            self.contador_label.config(text=f"Total: {len(self._programas)} registros")
            
            # Mensaje de estado
            if self._programas:
                self.mostrar_estado(f"✅ {len(self._programas)} movimientos cargados correctamente", "success")
            else:
                self.mostrar_estado("ℹ️ No hay movimientos registrados aún", "info")
                
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error al cargar el historial:\n{str(e)}")
            self.mostrar_estado("Error al cargar historial", "error")
            self._programas = []



    def mostrar_todos(self):
        matriculas, error = self.service.obtener_movimiento()
        if error:
            messagebox.showerror("Error", error)
            self.mostrar_estado(f"Error: {error}", "error")
            return
        self._poblar_tree(matriculas, modo='todos')
        self.mostrar_estado(f"📋 {len(matriculas)} matrículas en total", "success")

    def _poblar_tree(self, datos, modo='todos'):
        self.tree.delete(*self.tree.get_children())
        for i, m in enumerate(datos):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            if modo == 'por_curso':
                # obtener_matriculas_por_programa devuelve nombre_estudiante y carnet
                self.tree.insert('', 'end', tags=(tag,), values=(
                    m.get('id_tipo_movimiento', ''),
                    m.get('codigo', ''),
                    m.get('descripcion', ''),
                    m.get('estado', '')
                ))
            else:
                # obtener_matriculas devuelve nombre_estudiante y nombre_programa
                self.tree.insert('', 'end', tags=(tag,), values=(
                    m.get('id_tipo_movimiento', ''),
                    '',
                    m.get('codigo', ''),
                    m.get('descripcion', ''),
                    m.get('estado', '')
                ))
        self.contador_label.config(text=f"Total: {len(datos)} registros")


    # HELPERS (Son métodos auxiliares que hacen tareas repetitivas de soporte para no duplicar código en la clase)

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#c0392b"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()
            
            
    def guardar_Movimiento(self):
        if not self.validar_campos_requeridos():
            return

        try:
            datos = self.obtener_datos_formulario()
            success, mensaje = self.service.crear_movimiento(datos)

            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")


if __name__ == "__main__":
    root = tk.Tk()
    app = HistorialView(root)
    root.mainloop()
    
    
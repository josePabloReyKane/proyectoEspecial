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
        self.root.geometry("900x580")
        self.root.resizable(True, True)

        self.service = HistorialService()
        self._programas = []

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_programas()

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

        tk.Label(main_frame, text="REPORTE DE ESTUDIANTES POR CURSO",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        # ── FILTRO ────────────────────────────────────────────
        filter_frame = ttk.LabelFrame(main_frame, text="📌 Filtro", padding="12")
        filter_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(filter_frame, text="Curso/Programa:",
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 8))

        self.programa_combo = ttk.Combobox(filter_frame, width=45,
                                           font=("Arial", 10), state="readonly")
        self.programa_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(filter_frame, text="Consultar por curso",
                   command=self.consultar_por_curso).pack(side=tk.LEFT, padx=4)
        ttk.Button(filter_frame, text="Mostrar todos",
                   command=self.mostrar_todos).pack(side=tk.LEFT, padx=4)

        # GRID DE RESULTADOS
        tree_frame = ttk.LabelFrame(main_frame, text="📊 Estudiantes Matriculados", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('estudiante', 'carnet', 'programa', 'fecha', 'periodo', 'estado')
        headers = ['Estudiante', 'Carnet', 'Programa', 'Fecha Matrícula', 'Periodo', 'Estado']
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

    def cargar_programas(self):
        programas, error = self.service.obtener_programas_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar programas:\n{error}")
            return
        self._programas = programas or []
        self.programa_combo['values'] = [
            f"{p['codigo']} - {p['descripcion']}" for p in self._programas
        ]

    def consultar_por_curso(self):
        idx = self.programa_combo.current()
        if idx < 0:
            messagebox.showwarning("Advertencia", "Seleccione un Curso/Programa")
            return
        id_programa = self._programas[idx]['id_programa']
        nombre_programa = self._programas[idx]['descripcion']

        matriculas, error = self.service.obtener_matriculas_por_programa(id_programa)
        if error:
            messagebox.showerror("Error", error)
            self.mostrar_estado(f"Error: {error}", "error")
            return

        self._poblar_tree(matriculas, modo='por_curso')
        self.mostrar_estado(
            f"📋 {len(matriculas)} estudiantes en: {nombre_programa}", "success")

    def mostrar_todos(self):
        matriculas, error = self.service.obtener_matriculas()
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
                    m.get('nombre_estudiante', ''),
                    m.get('carnet', ''),
                    m.get('nombre_programa', ''),
                    m.get('fecha', ''),
                    m.get('periodo', ''),
                    m.get('estado', '')
                ))
            else:
                # obtener_matriculas devuelve nombre_estudiante y nombre_programa
                self.tree.insert('', 'end', tags=(tag,), values=(
                    m.get('nombre_estudiante', ''),
                    '',
                    m.get('nombre_programa', ''),
                    m.get('fecha', ''),
                    m.get('periodo', ''),
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


if __name__ == "__main__":
    root = tk.Tk()
    app = ReporteView(root)
    root.mainloop()
    
    
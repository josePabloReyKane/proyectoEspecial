import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services.matricula_service import MatriculaService


class MatriculaView:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Matrículas")
        self.root.geometry("1200x720")
        self.root.resizable(True, True)

        self.service = MatriculaService()
        self.matricula_seleccionada = None

        # Listas internas para mapear combo → ID real
        self._estudiantes = []
        self._programas = []
        self._docentes = []

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_combos()
        self.cargar_matriculas()

    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    # ──────────────────────────────────────────────────────────
    # WIDGETS
    # ──────────────────────────────────────────────────────────
    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="GESTIÓN DE MATRÍCULAS",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ── FORMULARIO ────────────────────────────────────────
        form_frame = ttk.LabelFrame(content_frame, text="📋 Datos de la Matrícula", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        form_frame.grid_columnconfigure(1, weight=1)

        # Estudiante — combo cargado desde BD
        tk.Label(form_frame, text="Estudiante:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=6)
        self.estudiante_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                             state="readonly")
        self.estudiante_combo.grid(row=0, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Curso/Programa — combo cargado desde BD
        tk.Label(form_frame, text="Curso/Programa:*", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=6)
        self.programa_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                           state="readonly")
        self.programa_combo.grid(row=1, column=1, pady=6, padx=10, sticky=tk.W + tk.E)
        self.programa_combo.bind("<<ComboboxSelected>>", self.on_programa_seleccionado)

        # Docente — combo filtrado por programa seleccionado
        tk.Label(form_frame, text="Docente:*", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=6)
        self.docente_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                          state="readonly")
        self.docente_combo.grid(row=2, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Fecha — Entry + botón calendario
        tk.Label(form_frame, text="Fecha:*", font=("Arial", 10)).grid(
        row=3, column=0, sticky=tk.W, pady=6)

        fecha_frame = ttk.Frame(form_frame)
        fecha_frame.grid(row=3, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        self.fecha_entry = ttk.Entry(fecha_frame, width=20, font=("Arial", 10))
        self.fecha_entry.pack(side=tk.LEFT)

        # Fecha de hoy
        self.fecha_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        # ←─ Importante: hacerlo de solo lectura
        self.fecha_entry.config(state='readonly')

        # Periodo
        tk.Label(form_frame, text="Periodo:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=6)
        self.periodo_entry = ttk.Entry(form_frame, width=38, font=("Arial", 10))
        self.periodo_entry.grid(row=4, column=1, pady=6, padx=10, sticky=tk.W + tk.E)
        tk.Label(form_frame, text="Ej: 2025-I", font=("Arial", 8, "italic"),
                 fg="gray").grid(row=4, column=2, sticky=tk.W, padx=(4, 0))

        # Estado
        tk.Label(form_frame, text="Estado:*", font=("Arial", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=6)
        self.estado_combo = ttk.Combobox(
            form_frame,
            values=["Activo", "Inactivo", "Vacaciones", "Suspendido"],
            width=35, font=("Arial", 10), state="readonly")
        self.estado_combo.grid(row=5, column=1, pady=6, padx=10, sticky=tk.W)
        self.estado_combo.set("Activo")

        tk.Label(form_frame, text="* Campos requeridos",
                 font=("Arial", 8, "italic"), fg="red").grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky=tk.W)

        btns = [
            ("➕ Nuevo",          self.nueva_matricula),
            ("💾 Matricular",     self.guardar_matricula),
            ("🔄 Actualizar",     self.actualizar_matricula),
            ("🔀 Cambiar estado", self.cambiar_estado_popup),
            ("🗑️ Eliminar",       self.eliminar_matricula),
            ("🔍 Consulta Curso", self.consulta_por_curso),
            ("🧹 Limpiar",        self.limpiar_formulario),
        ]
        for txt, cmd in btns:
            ttk.Button(button_frame, text=txt, command=cmd, width=15).pack(
                side=tk.LEFT, padx=3, pady=2)

        # ── GRID / LISTA ──────────────────────────────────────
        list_frame = ttk.LabelFrame(content_frame, text="📊 Lista de Matrículas", padding="15")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 12))
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=32, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar_matriculas())
        ttk.Button(search_frame, text="⟲ Refrescar",
                   command=self.cargar_matriculas).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'estudiante', 'programa', 'docente', 'fecha', 'periodo', 'estado')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=18)

        headers = ['ID', 'Estudiante', 'Programa', 'Docente', 'Fecha', 'Periodo', 'Estado']
        widths   = [50, 150, 150, 130, 100, 80, 90]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, minwidth=50,
                             anchor='center' if col == 'id' else 'w')

        vsb = ttk.Scrollbar(tree_container, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.tag_configure('oddrow',  background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='white')

        # Barra inferior
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(15, 0))
        tk.Button(nav_frame, text="⬅️ Volver al Menú", command=self.volver_menu,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  width=16, relief=tk.RAISED, bd=2, cursor="hand2").pack(side=tk.LEFT, padx=6)
        self.contador_label = tk.Label(nav_frame, text="Total: 0 registros",
                                       font=("Arial", 9), fg="#7f8c8d")
        self.contador_label.pack(side=tk.RIGHT, padx=8)

        self.status_bar = tk.Label(main_frame, text="✅ Listo", bd=1,
                                   relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#ecf0f1', fg='#2c3e50', font=("Arial", 8))
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    # ──────────────────────────────────────────────────────────
    # CARGA DE COMBOS
    # ──────────────────────────────────────────────────────────
    def cargar_combos(self):
        """Carga estudiantes y programas activos en sus respectivos combos."""
        # Estudiantes
        estudiantes, error = self.service.obtener_estudiantes_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar estudiantes:\n{error}")
        else:
            self._estudiantes = estudiantes or []
            self.estudiante_combo['values'] = [
                f"{e['carnet']} - {e['nombre']}" for e in self._estudiantes
            ]

        # Programas
        programas, error = self.service.obtener_programas_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar programas:\n{error}")
        else:
            self._programas = programas or []
            self.programa_combo['values'] = [
                f"{p['codigo']} - {p['descripcion']}" for p in self._programas
            ]

    def on_programa_seleccionado(self, event=None):
        """Cuando cambia el programa, recarga el combo de docentes filtrado."""
        idx = self.programa_combo.current()
        if idx < 0:
            return
        id_programa = self._programas[idx]['id_programa']
        docentes, error = self.service.obtener_docentes_por_programa(id_programa)
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar docentes:\n{error}")
            return
        self._docentes = docentes or []
        self.docente_combo['values'] = [d['nombre'] for d in self._docentes]
        self.docente_combo.set('')

    # ──────────────────────────────────────────────────────────
    # CALENDARIO
    # ──────────────────────────────────────────────────────────
    def abrir_calendario(self):
        self.root = root
        # ... otros widgets ...

        self.fecha_entry = ttk.Entry(...)   # o tk.Entry
        self.fecha_entry.pack(...)           # o grid, place, etc.

        # ── Aquí cargamos la fecha de hoy automáticamente ──
        hoy = date.today().strftime('%Y-%m-%d')
        self.fecha_entry.insert(0, hoy)

        # Opcional: si también quieres que sea de solo lectura
        # self.fecha_entry.config(state='readonly')
        

        

        

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────
    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()

    def actualizar_contador(self, cantidad):
        self.contador_label.config(text=f"Total: {cantidad} registros")

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#c0392b"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

    def obtener_datos_formulario(self):
        idx_est = self.estudiante_combo.current()
        idx_prog = self.programa_combo.current()
        idx_doc = self.docente_combo.current()
        return {
            'id_estudiante':  self._estudiantes[idx_est]['id_estudiante'] if idx_est >= 0 else None,
            'id_programa':    self._programas[idx_prog]['id_programa']    if idx_prog >= 0 else None,
            'id_docente':     self._docentes[idx_doc]['id_docente']       if idx_doc >= 0 else None,
            'fecha_matricula': self.fecha_entry.get().strip(),
            'periodo':        self.periodo_entry.get().strip(),
            'estado':         self.estado_combo.get()
        }

    def validar_campos_requeridos(self):
        datos = self.obtener_datos_formulario()
        if not datos['id_estudiante']:
            messagebox.showwarning("Validación", "Seleccione un Estudiante")
            return False
        if not datos['id_programa']:
            messagebox.showwarning("Validación", "Seleccione un Curso/Programa")
            return False
        if not datos['id_docente']:
            messagebox.showwarning("Validación", "Seleccione un Docente")
            return False
        if not datos['fecha_matricula']:
            messagebox.showwarning("Validación", "La fecha es requerida")
            return False
        if not datos['periodo']:
            messagebox.showwarning("Validación", "El periodo es requerido (Ej: 2025-I)")
            return False
        return True

    def mostrar_matricula_en_formulario(self, matricula):
        # Estudiante
        for i, e in enumerate(self._estudiantes):
            if e['id_estudiante'] == matricula.get('id_estudiante'):
                self.estudiante_combo.current(i)
                break

        # Programa
        for i, p in enumerate(self._programas):
            if p['id_programa'] == matricula.get('id_programa'):
                self.programa_combo.current(i)
                self.on_programa_seleccionado()
                break

        # Docente (cargar después de on_programa_seleccionado)
        for i, d in enumerate(self._docentes):
            if d['id_docente'] == matricula.get('id_docente'):
                self.docente_combo.current(i)
                break

        self.fecha_entry.delete(0, tk.END)
        fecha = matricula.get('fecha', '')
        if hasattr(fecha, 'strftime'):
            fecha = fecha.strftime('%Y-%m-%d')
        self.fecha_entry.insert(0, str(fecha))

        self.periodo_entry.delete(0, tk.END)
        self.periodo_entry.insert(0, matricula.get('periodo', ''))

        self.estado_combo.set(matricula.get('estado', 'Activo'))

    # ──────────────────────────────────────────────────────────
    # CARGA DEL GRID
    # ──────────────────────────────────────────────────────────
    def cargar_matriculas(self):
        try:
            matriculas, error = self.service.obtener_matriculas()
            if error:
                messagebox.showerror("Error", error)
                self.mostrar_estado(f"Error: {error}", "error")
                return
            self._poblar_tree(matriculas)
            self.mostrar_estado(f"✅ {len(matriculas)} matrículas cargadas", "success")
        except Exception as e:
            self.mostrar_estado(f"Error al cargar: {str(e)}", "error")
            messagebox.showerror("Error", str(e))

    def _poblar_tree(self, matriculas):
        self.tree.delete(*self.tree.get_children())
        for i, m in enumerate(matriculas):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end',
                             values=(
                                 m['id_matricula'],
                                 m.get('nombre_estudiante', m.get('id_estudiante', '')),
                                 m.get('nombre_programa',  m.get('id_programa', '')),
                                 m.get('nombre_docente',   m.get('id_docente', '')),
                                 m.get('fecha', ''),
                                 m.get('periodo', ''),
                                 m.get('estado', '')
                             ),
                             tags=(tag,),
                             iid=str(m['id_matricula']))
        self.actualizar_contador(len(matriculas))

    def buscar_matriculas(self):
        busqueda = self.search_entry.get().strip().lower()
        if not busqueda:
            self.cargar_matriculas()
            return
        try:
            matriculas, _ = self.service.obtener_matriculas()
            keys = ['id_matricula', 'nombre_estudiante', 'nombre_programa',
                    'nombre_docente', 'fecha', 'periodo', 'estado']
            filtradas = [m for m in matriculas
                         if any(busqueda in str(m.get(k, '')).lower() for k in keys)]
            self._poblar_tree(filtradas)
            self.mostrar_estado(f"🔍 {len(filtradas)} resultados para '{busqueda}'")
        except Exception as e:
            self.mostrar_estado(f"Error en búsqueda: {str(e)}", "error")

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        try:
            id_mat = int(seleccion[0])
            matricula, error = self.service.obtener_matricula_por_id(id_mat)
            if error or not matricula:
                self.mostrar_estado(f"Error: {error or 'No encontrado'}", "error")
                return
            self.matricula_seleccionada = id_mat
            self.mostrar_matricula_en_formulario(matricula)
            self.mostrar_estado(f"📋 Matrícula seleccionada: {id_mat}")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")

    # ──────────────────────────────────────────────────────────
    # ACCIONES DE BOTONES
    # ──────────────────────────────────────────────────────────
    def nueva_matricula(self):
        self.limpiar_formulario()
        self.matricula_seleccionada = None
        self.mostrar_estado("📝 Nueva matrícula — complete los campos")

    def guardar_matricula(self):
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.crear_matricula(datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_matriculas()
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def actualizar_matricula(self):
        if not self.matricula_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una matrícula de la lista")
            return
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.actualizar_matricula(self.matricula_seleccionada, datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_matriculas()
            self.matricula_seleccionada = None
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def cambiar_estado_popup(self):
        """Abre popup para cambiar el estado de una matrícula seleccionada."""
        if not self.matricula_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una matrícula de la lista")
            return

        top = tk.Toplevel(self.root)
        top.title("Cambiar estado")
        top.geometry("280x160")
        top.grab_set()
        top.resizable(False, False)

        tk.Label(top, text="Seleccione el nuevo estado:",
                 font=("Arial", 10)).pack(pady=(20, 8))

        estado_var = tk.StringVar(value="Activo")
        combo = ttk.Combobox(top, textvariable=estado_var,
                             values=["Activo", "Inactivo", "Vacaciones", "Suspendido"],
                             state="readonly", width=25)
        combo.pack(pady=4)

        def confirmar():
            success, mensaje = self.service.cambiar_estado(
                self.matricula_seleccionada, estado_var.get())
            top.destroy()
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.cargar_matriculas()
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")

        ttk.Button(top, text="Aceptar", command=confirmar).pack(pady=12)

    def eliminar_matricula(self):
        if not self.matricula_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una matrícula")
            return
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Eliminar esta matrícula permanentemente?\n\n⚠️ Acción irreversible"):
            success, mensaje = self.service.eliminar_matricula(self.matricula_seleccionada)
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_matriculas()
                self.matricula_seleccionada = None
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")

    def consulta_por_curso(self):
        """Abre popup para consultar estudiantes matriculados en un programa."""
        top = tk.Toplevel(self.root)
        top.title("Consulta por Curso")
        top.geometry("700x420")
        top.grab_set()

        tk.Label(top, text="Seleccione el Curso/Programa:",
                 font=("Arial", 10)).pack(pady=(16, 4))

        combo_prog = ttk.Combobox(
            top,
            values=[f"{p['codigo']} - {p['descripcion']}" for p in self._programas],
            state="readonly", width=50)
        combo_prog.pack(pady=4)

        columns = ('estudiante', 'carnet', 'fecha', 'periodo', 'estado')
        headers = ['Estudiante', 'Carnet', 'Fecha', 'Periodo', 'Estado']
        widths   = [200, 100, 100, 80, 90]

        tree_frame = ttk.Frame(top)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        for col, head, w in zip(columns, headers, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        contador = tk.Label(top, text="", font=("Arial", 9), fg="#7f8c8d")
        contador.pack()

        def consultar():
            idx = combo_prog.current()
            if idx < 0:
                messagebox.showwarning("Advertencia", "Seleccione un programa", parent=top)
                return
            id_programa = self._programas[idx]['id_programa']
            matriculas, error = self.service.obtener_matriculas_por_programa(id_programa)
            if error:
                messagebox.showerror("Error", error, parent=top)
                return
            tree.delete(*tree.get_children())
            for m in matriculas:
                tree.insert('', 'end', values=(
                    m['nombre_estudiante'], m['carnet'],
                    m['fecha'], m['periodo'], m['estado']
                ))
            contador.config(text=f"{len(matriculas)} estudiantes matriculados")

        def mostrar_todos():
            tree.delete(*tree.get_children())
            matriculas, _ = self.service.obtener_matriculas()
            for m in (matriculas or []):
                tree.insert('', 'end', values=(
                    m.get('nombre_estudiante', ''), '',
                    m.get('fecha', ''), m.get('periodo', ''), m.get('estado', '')
                ))
            contador.config(text=f"{len(matriculas or [])} matrículas en total")

        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=(0, 12))
        ttk.Button(btn_frame, text="Consultar", command=consultar).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Mostrar todos", command=mostrar_todos).pack(side=tk.LEFT, padx=6)

    def limpiar_formulario(self):
        self.estudiante_combo.set('')
        self.programa_combo.set('')
        self.docente_combo.set('')
        self.docente_combo['values'] = []
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.periodo_entry.delete(0, tk.END)
        self.estado_combo.set("Activo")
        self.matricula_seleccionada = None


if __name__ == "__main__":
    root = tk.Tk()
    app = MatriculaView(root)
    root.mainloop()
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from services.asignacion_service import AsignacionService


class AsignacionView:
    def __init__(self, root):
        self.root = root
        self.root.title("Asignación de Docentes")
        self.root.geometry("1200x720")
        self.root.resizable(True, True)

        self.service = AsignacionService()
        self.asignacion_seleccionada = None

        # Listas internas para mapear combo → ID real
        self._docentes  = []
        self._programas = []
        self._periodos  = []
        self._estados   = []

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_combos()
        self.cargar_asignaciones()

    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto  = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto  // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    # WIDGETS
    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="ASIGNACIÓN DE DOCENTES",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ── FORMULARIO ────────────────────────────────────────
        form_frame = ttk.LabelFrame(content_frame, text="📋 Datos de la Asignación", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        form_frame.grid_columnconfigure(1, weight=1)

        # Docente
        tk.Label(form_frame, text="Docente:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=6)
        self.docente_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                          state="readonly")
        self.docente_combo.grid(row=0, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Curso/Programa
        tk.Label(form_frame, text="Curso/Programa:*", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=6)
        self.programa_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                           state="readonly")
        self.programa_combo.grid(row=1, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Periodo — desplegado automático según fecha actual
        tk.Label(form_frame, text="Periodo:*", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=6)
        self.periodo_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                          state="readonly")
        self.periodo_combo.grid(row=2, column=1, pady=6, padx=10, sticky=tk.W + tk.E)
        self.periodo_combo.bind("<<ComboboxSelected>>", self.on_periodo_seleccionado)

        # Fecha Inicio — automática según periodo
        tk.Label(form_frame, text="Fecha Inicio:*", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=6)
        self.fecha_inicio_entry = ttk.Entry(form_frame, width=38, font=("Arial", 10),
                                            state="readonly")
        self.fecha_inicio_entry.grid(row=3, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Fecha Fin — automática según periodo
        tk.Label(form_frame, text="Fecha Fin:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=6)
        self.fecha_fin_entry = ttk.Entry(form_frame, width=38, font=("Arial", 10),
                                         state="readonly")
        self.fecha_fin_entry.grid(row=4, column=1, pady=6, padx=10, sticky=tk.W + tk.E)

        # Estado — desde tabla maestra
        tk.Label(form_frame, text="Estado:*", font=("Arial", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=6)
        self.estado_combo = ttk.Combobox(form_frame, width=36, font=("Arial", 10),
                                         state="readonly")
        self.estado_combo.grid(row=5, column=1, pady=6, padx=10, sticky=tk.W)

        tk.Label(form_frame, text="* Campos requeridos",
                 font=("Arial", 8, "italic"), fg="red").grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky=tk.W)

        btns = [
            ("➕ Nuevo",          self.nueva_asignacion),
            ("💾 Guardar",        self.guardar_asignacion),
            ("🔄 Actualizar",     self.actualizar_asignacion),
            ("🔀 Cambiar estado", self.cambiar_estado_popup),
            ("🗑️ Eliminar",       self.eliminar_asignacion),
            ("🧹 Limpiar",        self.limpiar_formulario),
        ]
        for txt, cmd in btns:
            ttk.Button(button_frame, text=txt, command=cmd, width=15).pack(
                side=tk.LEFT, padx=3, pady=2)

        # GRID
        list_frame = ttk.LabelFrame(content_frame, text="📊 Lista de Asignaciones", padding="15")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 12))
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=32, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar_asignaciones())
        ttk.Button(search_frame, text="⟲ Refrescar",
                   command=self.cargar_asignaciones).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'docente', 'programa', 'periodo', 'fecha_inicio', 'fecha_fin', 'estado')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=18)

        headers = ['ID', 'Docente', 'Programa', 'Periodo', 'Fecha Inicio', 'Fecha Fin', 'Estado']
        widths   = [50, 170, 160, 90, 100, 100, 90]
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

    # CARGA DE COMBOS
    
    def cargar_combos(self):
        # Docentes
        docentes, error = self.service.obtener_docentes_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar docentes:\n{error}")
        else:
            self._docentes = docentes or []
            self.docente_combo['values'] = [d['nombre'] for d in self._docentes]

        # Programas
        programas, error = self.service.obtener_programas_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar programas:\n{error}")
        else:
            self._programas = programas or []
            self.programa_combo['values'] = [
                f"{p['codigo']} - {p['descripcion']}" for p in self._programas
            ]

        # Periodos
        periodos, error = self.service.obtener_periodos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar periodos:\n{error}")
        else:
            self._periodos = periodos or []
            self.periodo_combo['values'] = [
                f"{p['codigo']} - {p['descripcion']}" for p in self._periodos
            ]
            # Seleccionar automáticamente el periodo activo según la fecha actual
            self._seleccionar_periodo_actual()

        # Estados desde tabla maestra
        estados, error = self.service.obtener_estados()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar estados:\n{error}")
        else:
            self._estados = estados or []
            self.estado_combo['values'] = [e['descripcion'] for e in self._estados]
            if self._estados:
                self.estado_combo.current(0)

    def _seleccionar_periodo_actual(self):
        """Selecciona automáticamente el periodo que corresponde a la fecha de hoy."""
        from datetime import date
        hoy = date.today()
        for i, p in enumerate(self._periodos):
            inicio = date.fromisoformat(p['fecha_inicio'])
            fin    = date.fromisoformat(p['fecha_fin'])
            if inicio <= hoy <= fin:
                self.periodo_combo.current(i)
                self._poblar_fechas(p)
                break

    def on_periodo_seleccionado(self, event=None):
        """Al cambiar el periodo, actualiza las fechas automáticamente."""
        idx = self.periodo_combo.current()
        if idx < 0:
            return
        self._poblar_fechas(self._periodos[idx])

    def _poblar_fechas(self, periodo):
        """Pone las fechas de inicio y fin según el periodo seleccionado."""
        for entry in (self.fecha_inicio_entry, self.fecha_fin_entry):
            entry.config(state='normal')
            entry.delete(0, tk.END)
        self.fecha_inicio_entry.insert(0, periodo['fecha_inicio'])
        self.fecha_fin_entry.insert(0,    periodo['fecha_fin'])
        for entry in (self.fecha_inicio_entry, self.fecha_fin_entry):
            entry.config(state='readonly')


    # HELPERS

    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#c0392b"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

    def actualizar_contador(self, cantidad):
        self.contador_label.config(text=f"Total: {cantidad} registros")

    def obtener_datos_formulario(self):
        idx_doc  = self.docente_combo.current()
        idx_prog = self.programa_combo.current()
        idx_per  = self.periodo_combo.current()
        idx_est  = self.estado_combo.current()
        return {
            'id_docente':   self._docentes[idx_doc]['id_docente']    if idx_doc  >= 0 else None,
            'id_programa':  self._programas[idx_prog]['id_programa'] if idx_prog >= 0 else None,
            'id_periodo':   self._periodos[idx_per]['id_periodo']    if idx_per  >= 0 else None,
            'fecha_inicio': self.fecha_inicio_entry.get().strip(),
            'fecha_fin':    self.fecha_fin_entry.get().strip(),
            'id_estado':    self._estados[idx_est]['id_estado']      if idx_est  >= 0 else None,
        }

    def validar_campos_requeridos(self):
        datos = self.obtener_datos_formulario()
        if not datos['id_docente']:
            messagebox.showwarning("Validación", "Seleccione un Docente")
            return False
        if not datos['id_programa']:
            messagebox.showwarning("Validación", "Seleccione un Curso/Programa")
            return False
        if not datos['id_periodo']:
            messagebox.showwarning("Validación", "Seleccione un Periodo")
            return False
        if not datos['id_estado']:
            messagebox.showwarning("Validación", "Seleccione un Estado")
            return False
        return True

    def mostrar_asignacion_en_formulario(self, asignacion):
        for i, d in enumerate(self._docentes):
            if d['id_docente'] == asignacion.get('id_docente'):
                self.docente_combo.current(i)
                break
        for i, p in enumerate(self._programas):
            if p['id_programa'] == asignacion.get('id_programa'):
                self.programa_combo.current(i)
                break
        for i, p in enumerate(self._periodos):
            if p['id_periodo'] == asignacion.get('id_periodo'):
                self.periodo_combo.current(i)
                self._poblar_fechas(p)
                break
        for i, e in enumerate(self._estados):
            if e['descripcion'] == asignacion.get('nombre_estado'):
                self.estado_combo.current(i)
                break


    # CARGA DEL GRID

    def cargar_asignaciones(self):
        try:
            asignaciones, error = self.service.obtener_asignaciones()
            if error:
                messagebox.showerror("Error", error)
                self.mostrar_estado(f"Error: {error}", "error")
                return
            self._poblar_tree(asignaciones)
            self.mostrar_estado(f"✅ {len(asignaciones)} asignaciones cargadas", "success")
        except Exception as e:
            self.mostrar_estado(f"Error al cargar: {str(e)}", "error")
            messagebox.showerror("Error", str(e))

    def _poblar_tree(self, asignaciones):
        self.tree.delete(*self.tree.get_children())
        for i, a in enumerate(asignaciones):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end',
                             values=(
                                 a['id_asignacion'],
                                 a['nombre_docente'],
                                 a['nombre_programa'],
                                 a['codigo_periodo'],
                                 a['fecha_inicio'],
                                 a['fecha_fin'],
                                 a['nombre_estado']
                             ),
                             tags=(tag,),
                             iid=str(a['id_asignacion']))
        self.actualizar_contador(len(asignaciones))

    def buscar_asignaciones(self):
        busqueda = self.search_entry.get().strip().lower()
        if not busqueda:
            self.cargar_asignaciones()
            return
        try:
            asignaciones, _ = self.service.obtener_asignaciones()
            keys = ['nombre_docente', 'nombre_programa', 'codigo_periodo', 'nombre_estado']
            filtradas = [a for a in asignaciones
                         if any(busqueda in str(a.get(k, '')).lower() for k in keys)]
            self._poblar_tree(filtradas)
            self.mostrar_estado(f"🔍 {len(filtradas)} resultados para '{busqueda}'")
        except Exception as e:
            self.mostrar_estado(f"Error en búsqueda: {str(e)}", "error")

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        try:
            id_asig = int(seleccion[0])
            asignacion, error = self.service.obtener_asignacion_por_id(id_asig)
            if error or not asignacion:
                self.mostrar_estado(f"Error: {error or 'No encontrado'}", "error")
                return
            self.asignacion_seleccionada = id_asig
            self.mostrar_asignacion_en_formulario(asignacion)
            self.mostrar_estado(f"📋 Asignación seleccionada: {id_asig}")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")


    # ACCIONES DE BOTONES
  
    def nueva_asignacion(self):
        self.limpiar_formulario()
        self.asignacion_seleccionada = None
        self.mostrar_estado("📝 Nueva asignación — complete los campos")

    def guardar_asignacion(self):
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.crear_asignacion(datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_asignaciones()
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def actualizar_asignacion(self):
        if not self.asignacion_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una asignación de la lista")
            return
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.actualizar_asignacion(self.asignacion_seleccionada, datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_asignaciones()
            self.asignacion_seleccionada = None
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def cambiar_estado_popup(self):
        """Abre popup para cambiar el estado de una asignación."""
        if not self.asignacion_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una asignación de la lista")
            return

        top = tk.Toplevel(self.root)
        top.title("Cambiar estado")
        top.geometry("300x170")
        top.grab_set()
        top.resizable(False, False)

        tk.Label(top, text="Seleccione el nuevo estado:",
                 font=("Arial", 10)).pack(pady=(20, 8))

        estado_var = tk.StringVar()
        combo = ttk.Combobox(top, textvariable=estado_var,
                             values=[e['descripcion'] for e in self._estados],
                             state="readonly", width=28)
        combo.pack(pady=4)
        if self._estados:
            combo.current(0)

        def confirmar():
            idx = combo.current()
            if idx < 0:
                messagebox.showwarning("Advertencia", "Seleccione un estado", parent=top)
                return
            id_estado = self._estados[idx]['id_estado']
            success, mensaje = self.service.cambiar_estado(
                self.asignacion_seleccionada, id_estado)
            top.destroy()
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.cargar_asignaciones()
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")

        ttk.Button(top, text="Aceptar", command=confirmar).pack(pady=12)

    def eliminar_asignacion(self):
        if not self.asignacion_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Eliminar esta asignación permanentemente?\n\n⚠️ Acción irreversible"):
            success, mensaje = self.service.eliminar_asignacion(self.asignacion_seleccionada)
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_asignaciones()
                self.asignacion_seleccionada = None
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")

    def limpiar_formulario(self):
        self.docente_combo.set('')
        self.programa_combo.set('')
        self.periodo_combo.set('')
        for entry in (self.fecha_inicio_entry, self.fecha_fin_entry):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.config(state='readonly')
        if self._estados:
            self.estado_combo.current(0)
        self.asignacion_seleccionada = None
        # Restaurar periodo actual
        self._seleccionar_periodo_actual()


if __name__ == "__main__":
    root = tk.Tk()
    app = AsignacionView(root)
    root.mainloop()
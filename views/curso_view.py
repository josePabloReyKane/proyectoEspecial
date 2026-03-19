import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from services.cursos_services import CursoService
from services.matricula_service import MatriculaService


class CursosView:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de curso")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        self.service = CursoService()
        self.matricula_service = MatriculaService()
        self.curso_seleccionado = None
        self._programas = []

        self.centrar_ventana_Curso()
        self.crear_widgets_Curso()
        self.cargar_programas()
        self.cargar_Curso()

    def centrar_ventana_Curso(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    def crear_widgets_Curso(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="GESTIÓN DE Curso",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Formulario
        form_frame = ttk.LabelFrame(content_frame, text="📋 Datos del Curso", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        for i in range(9):
            form_frame.grid_rowconfigure(i, pad=5)
        form_frame.grid_columnconfigure(1, weight=1)

        # Código
        tk.Label(form_frame, text="codigo:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.codigo_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.codigo_entry.grid(row=0, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Descripción
        tk.Label(form_frame, text="descripcion:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.descripcion_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.descripcion_entry.grid(row=1, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Programa — Combo cargado desde BD
        tk.Label(form_frame, text="id_programa:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.programa_combo = ttk.Combobox(form_frame, width=33, font=("Arial", 10),
                                           state="readonly")
        self.programa_combo.grid(row=2, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Cuatrimestre — solo números 1-4
        tk.Label(form_frame, text="cuatrimestre:", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.cuatrimestre_combo = ttk.Combobox(form_frame, values=["1", "2", "3", "4"],
                                               width=33, font=("Arial", 10), state="readonly")
        self.cuatrimestre_combo.grid(row=3, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Precio
        tk.Label(form_frame, text="precio:", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.precio_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.precio_entry.grid(row=4, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Estado
        tk.Label(form_frame, text="Estado:*", font=("Arial", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=5)
        self.estado_combo = ttk.Combobox(form_frame, values=["Activo", "Inactivo", "Suspendido"],
                                         width=32, font=("Arial", 10), state="readonly")
        self.estado_combo.grid(row=5, column=1, pady=5, padx=10, sticky=tk.W)
        self.estado_combo.set("Activo")

        tk.Label(form_frame, text="* Campos requeridos", font=("Arial", 8, "italic"),
                 fg="red").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=15)

        ttk.Button(button_frame, text="➕ Nuevo",     command=self.nuevo_Curso,    width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="💾 Guardar",   command=self.guardar_curso,  width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🔄 Actualizar",command=self.actualizar_curso,width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🗑️ Eliminar",  command=self.eliminar_Curso, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🧹 Limpiar",   command=self.limpiar_formulario, width=12).pack(side=tk.LEFT, padx=3)

        # Lista
        list_frame = ttk.LabelFrame(content_frame, text="📊 Lista de Cursos", padding="15")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=25, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar_Curso())
        ttk.Button(search_frame, text="⟲ Refrescar", command=self.cargar_Curso).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('id_materia', 'codigo', 'descripcion', 'id_programa', 'cuatrimestre', 'precio', 'estado')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        headers = ['ID', 'Código', 'Descripción', 'Programa', 'Cuatrimestre', 'Precio', 'Estado']
        widths   = [60, 100, 200, 80, 100, 100, 80]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, minwidth=50)

        vsb = ttk.Scrollbar(tree_container, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.tag_configure('oddrow',  background='#f2f2f2')
        self.tree.tag_configure('evenrow', background='white')

        # Barra inferior
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(15, 0))
        tk.Button(nav_frame, text="⬅️ Volver al Menú", command=self.volver_menu,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  width=15, relief=tk.RAISED, bd=3, cursor="hand2").pack(side=tk.LEFT, padx=5)
        self.contador_label = tk.Label(nav_frame, text="Total: 0 registros",
                                       font=("Arial", 9), fg="#7f8c8d")
        self.contador_label.pack(side=tk.RIGHT, padx=5)

        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        self.status_bar = tk.Label(main_frame, text="✅ Listo", bd=1,
                                   relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#ecf0f1', fg='#2c3e50', font=("Arial", 8))
        self.status_bar.pack(fill=tk.X)

    
    # Carga de combos
    def cargar_programas(self):
        programas, error = self.matricula_service.obtener_programas_activos()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar programas:\n{error}")
            return
        self._programas = programas or []
        self.programa_combo['values'] = [
            f"{p['codigo']} - {p['descripcion']}" for p in self._programas
        ]


    # HELPERS (Son métodos auxiliares que hacen tareas repetitivas de soporte para no duplicar código en la clase)
    
    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()

    def actualizar_contador(self, cantidad):
        self.contador_label.config(text=f"Total: {cantidad} registros")

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#e74c3c"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

    def obtener_datos_formulario(self):
        idx_prog = self.programa_combo.current()
        return {
            'codigo':       self.codigo_entry.get().strip(),
            'descripcion':  self.descripcion_entry.get().strip(),
            'id_programa':  self._programas[idx_prog]['id_programa'] if idx_prog >= 0 else None,
            'cuatrimestre': self.cuatrimestre_combo.get() or None,
            'precio':       self.precio_entry.get().strip() or None,
            'estado':       self.estado_combo.get()
        }

    def validar_campos_requeridos(self):
        if not self.codigo_entry.get().strip():
            messagebox.showwarning("Validación", "El código es requerido")
            self.codigo_entry.focus()
            return False
        if self.programa_combo.current() < 0:
            messagebox.showwarning("Validación", "Seleccione un programa")
            return False
        return True

    def mostrar_Curso_en_formulario(self, curso):
        self.codigo_entry.delete(0, tk.END)
        self.codigo_entry.insert(0, curso.get('codigo', ''))

        self.descripcion_entry.delete(0, tk.END)
        self.descripcion_entry.insert(0, curso.get('descripcion', ''))

        # Seleccionar programa en combo
        for i, p in enumerate(self._programas):
            if p['id_programa'] == curso.get('id_programa'):
                self.programa_combo.current(i)
                break

        # Cuatrimestre es INT
        cuatrimestre = curso.get('cuatrimestre')
        self.cuatrimestre_combo.set(str(cuatrimestre) if cuatrimestre else '')

        self.precio_entry.delete(0, tk.END)
        self.precio_entry.insert(0, curso.get('precio', ''))

        self.estado_combo.set(curso.get('estado', 'Activo'))

    # Carga del GRID
    
    def cargar_Curso(self):
        try:
            curso, error = self.service.obtener_Curso()
            if error:
                self.mostrar_estado(f"Error: {error}", "error")
                messagebox.showerror("Error", error)
                return
            for row in self.tree.get_children():
                self.tree.delete(row)
            for i, est in enumerate(curso):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end',
                                 values=(
                                     est['id_materia'],
                                     est['codigo'],
                                     est['descripcion'],
                                     est['id_programa'] or '',
                                     est['cuatrimestre'] or '',
                                     est['precio'],
                                     est['estado']
                                 ),
                                 tags=(tag,),
                                 iid=str(est['id_materia']))
            self.actualizar_contador(len(curso))
            self.mostrar_estado(f"✅ {len(curso)} cursos cargados", "success")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")
            messagebox.showerror("Error", f"Error al cargar cursos: {str(e)}")

    def buscar_Curso(self):
        busqueda = self.search_entry.get().strip().lower()
        if not busqueda:
            self.cargar_Curso()
            return
        try:
            curso, error = self.service.obtener_Curso()
            if error:
                return
            for row in self.tree.get_children():
                self.tree.delete(row)
            count = 0
            for i, est in enumerate(curso):
                if any(busqueda in str(est.get(k, '')).lower()
                       for k in ['codigo', 'descripcion', 'estado']):
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert('', 'end',
                                     values=(
                                         est['id_materia'],
                                         est['codigo'],
                                         est['descripcion'],
                                         est['id_programa'] or '',
                                         est['cuatrimestre'] or '',
                                         est['precio'],
                                         est['estado']
                                     ),
                                     tags=(tag,),
                                     iid=str(est['id_materia']))
                    count += 1
            self.actualizar_contador(count)
            self.mostrar_estado(f"🔍 {count} resultados para '{busqueda}'")
        except Exception as e:
            self.mostrar_estado(f"Error en búsqueda: {str(e)}", "error")

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        id_materia = int(seleccion[0])
        try:
            curso, error = self.service.obtener_Curso_por_id(id_materia)
            if error:
                self.mostrar_estado(f"Error: {error}", "error")
                return
            if curso:
                self.curso_seleccionado = id_materia
                self.mostrar_Curso_en_formulario(curso)
                self.mostrar_estado(f"📋 Curso seleccionado: {curso['descripcion']}")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")

    # Acciones de los botones
    def nuevo_Curso(self):
        self.limpiar_formulario()
        self.curso_seleccionado = None
        self.mostrar_estado("📝 Nuevo curso — complete los campos")

    def guardar_curso(self):
        if not self.validar_campos_requeridos():
            return
        try:
            datos = self.obtener_datos_formulario()
            success, mensaje = self.service.crear_Curso(datos)
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_Curso()
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def actualizar_curso(self):
        if not self.curso_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar un curso de la lista")
            return
        if not self.validar_campos_requeridos():
            return
        try:
            datos = self.obtener_datos_formulario()
            # CORREGIDO: llamaba a actualizar_estudiante — ahora llama a actualizar_Curso
            success, mensaje = self.service.actualizar_Curso(self.curso_seleccionado, datos)
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_Curso()
                self.curso_seleccionado = None
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def eliminar_Curso(self):
        if not self.curso_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar un curso de la lista")
            return
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Está seguro de eliminar este curso?\n\n"
                               "⚠️ Esta acción es permanente."):
            try:
                success, mensaje = self.service.eliminar_Curso(self.curso_seleccionado)
                if success:
                    messagebox.showinfo("Éxito", mensaje)
                    self.mostrar_estado(mensaje, "success")
                    self.limpiar_formulario()
                    self.cargar_Curso()
                    self.curso_seleccionado = None
                else:
                    messagebox.showerror("Error", mensaje)
                    self.mostrar_estado(mensaje, "error")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.mostrar_estado(f"Error: {str(e)}", "error")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, tk.END)
        self.descripcion_entry.delete(0, tk.END)
        self.programa_combo.set('')
        self.cuatrimestre_combo.set('')
        self.precio_entry.delete(0, tk.END)
        self.estado_combo.set("Activo")
        self.curso_seleccionado = None


if __name__ == "__main__":
    root = tk.Tk()
    app = CursosView(root)
    root.mainloop()
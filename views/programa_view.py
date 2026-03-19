import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from services.programa_service import ProgramaService


class ProgramaView:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Programas")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        self.service = ProgramaService()
        self.programa_seleccionado = None

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_programas()

    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto  = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto  // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="GESTIÓN DE PROGRAMAS",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ── FORMULARIO ────────────────────────────────────────
        form_frame = ttk.LabelFrame(content_frame, text="📋 Datos del Programa", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)

        # Código
        tk.Label(form_frame, text="Código:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.codigo_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.codigo_entry.grid(row=0, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Descripción
        tk.Label(form_frame, text="Descripción:*", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.descripcion_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.descripcion_entry.grid(row=1, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Horario
        tk.Label(form_frame, text="Horario:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.horario_combo = ttk.Combobox(form_frame,
                                          values=["Diurno", "Nocturno", "Sabatino", "Virtual"],
                                          width=33, font=("Arial", 10), state="readonly")
        self.horario_combo.grid(row=2, column=1, pady=5, padx=10, sticky=tk.W)
        self.horario_combo.set("Nocturno")

        # Precio matrícula
        tk.Label(form_frame, text="Precio Matrícula:*", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.precio_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.precio_entry.grid(row=3, column=1, pady=5, padx=10, sticky=tk.W + tk.E)

        # Estado
        tk.Label(form_frame, text="Estado:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.estado_combo = ttk.Combobox(form_frame,
                                         values=["Activo", "Inactivo", "Suspendido"],
                                         width=33, font=("Arial", 10), state="readonly")
        self.estado_combo.grid(row=4, column=1, pady=5, padx=10, sticky=tk.W)
        self.estado_combo.set("Activo")

        tk.Label(form_frame, text="* Campos requeridos",
                 font=("Arial", 8, "italic"), fg="red").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=15)

        btns = [
            ("➕ Nuevo",     self.nuevo_programa),
            ("💾 Guardar",   self.guardar_programa),
            ("🔄 Actualizar",self.actualizar_programa),
            ("🗑️ Eliminar",  self.eliminar_programa),
            ("🧹 Limpiar",   self.limpiar_formulario),
        ]
        for txt, cmd in btns:
            ttk.Button(button_frame, text=txt, command=cmd, width=12).pack(
                side=tk.LEFT, padx=3)

        # ── LISTA ─────────────────────────────────────────────
        list_frame = ttk.LabelFrame(content_frame, text="📊 Lista de Programas", padding="15")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=25, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar_programas())
        ttk.Button(search_frame, text="⟲ Refrescar",
                   command=self.cargar_programas).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'codigo', 'descripcion', 'horario', 'precio', 'estado')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        headers = ['ID', 'Código', 'Descripción', 'Horario', 'Precio', 'Estado']
        widths   = [50, 100, 200, 100, 100, 80]
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

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────
    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#e74c3c"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

    def actualizar_contador(self, cantidad):
        self.contador_label.config(text=f"Total: {cantidad} registros")

    def obtener_datos_formulario(self):
        return {
            'codigo':          self.codigo_entry.get().strip(),
            'descripcion':     self.descripcion_entry.get().strip(),
            'horario':         self.horario_combo.get(),
            'precio_matricula':self.precio_entry.get().strip(),
            'estado':          self.estado_combo.get()
        }

    def validar_campos_requeridos(self):
        if not self.codigo_entry.get().strip():
            messagebox.showwarning("Validación", "El código es requerido")
            self.codigo_entry.focus()
            return False
        if not self.descripcion_entry.get().strip():
            messagebox.showwarning("Validación", "La descripción es requerida")
            self.descripcion_entry.focus()
            return False
        if not self.precio_entry.get().strip():
            messagebox.showwarning("Validación", "El precio de matrícula es requerido")
            self.precio_entry.focus()
            return False
        return True

    def mostrar_programa_en_formulario(self, programa):
        self.codigo_entry.delete(0, tk.END)
        self.codigo_entry.insert(0, programa.get('codigo', ''))

        self.descripcion_entry.delete(0, tk.END)
        self.descripcion_entry.insert(0, programa.get('descripcion', ''))

        self.horario_combo.set(programa.get('horario', 'Nocturno'))

        self.precio_entry.delete(0, tk.END)
        self.precio_entry.insert(0, programa.get('precio_matricula', ''))

        self.estado_combo.set(programa.get('estado', 'Activo'))

    # ──────────────────────────────────────────────────────────
    # CARGA DEL GRID
    # ──────────────────────────────────────────────────────────
    def cargar_programas(self):
        try:
            programas, error = self.service.obtener_programas()
            if error:
                messagebox.showerror("Error", error)
                self.mostrar_estado(f"Error: {error}", "error")
                return
            self.tree.delete(*self.tree.get_children())
            for i, p in enumerate(programas):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end',
                                 values=(
                                     p['id_programa'],
                                     p['codigo'],
                                     p['descripcion'],
                                     p['horario'] or '',
                                     p['precio_matricula'],
                                     p['estado']
                                 ),
                                 tags=(tag,),
                                 iid=str(p['id_programa']))
            self.actualizar_contador(len(programas))
            self.mostrar_estado(f"✅ {len(programas)} programas cargados", "success")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def buscar_programas(self):
        busqueda = self.search_entry.get().strip().lower()
        if not busqueda:
            self.cargar_programas()
            return
        try:
            programas, _ = self.service.obtener_programas()
            self.tree.delete(*self.tree.get_children())
            count = 0
            for p in (programas or []):
                if any(busqueda in str(p.get(k, '')).lower()
                       for k in ['codigo', 'descripcion', 'estado']):
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert('', 'end',
                                     values=(p['id_programa'], p['codigo'], p['descripcion'],
                                             p['horario'] or '', p['precio_matricula'], p['estado']),
                                     tags=(tag,), iid=str(p['id_programa']))
                    count += 1
            self.actualizar_contador(count)
            self.mostrar_estado(f"🔍 {count} resultados para '{busqueda}'")
        except Exception as e:
            self.mostrar_estado(f"Error en búsqueda: {str(e)}", "error")

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        id_programa = int(seleccion[0])
        try:
            programa, error = self.service.obtener_programa_por_id(id_programa)
            if error or not programa:
                self.mostrar_estado(f"Error: {error or 'No encontrado'}", "error")
                return
            self.programa_seleccionado = id_programa
            self.mostrar_programa_en_formulario(programa)
            self.mostrar_estado(f"📋 Programa seleccionado: {programa['descripcion']}")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")

    # ──────────────────────────────────────────────────────────
    # ACCIONES DE BOTONES
    # ──────────────────────────────────────────────────────────
    def nuevo_programa(self):
        self.limpiar_formulario()
        self.programa_seleccionado = None
        self.mostrar_estado("📝 Nuevo programa — complete los campos")

    def guardar_programa(self):
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.crear_programa(datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_programas()
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def actualizar_programa(self):
        if not self.programa_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un programa de la lista")
            return
        if not self.validar_campos_requeridos():
            return
        datos = self.obtener_datos_formulario()
        success, mensaje = self.service.actualizar_programa(self.programa_seleccionado, datos)
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.mostrar_estado(mensaje, "success")
            self.limpiar_formulario()
            self.cargar_programas()
            self.programa_seleccionado = None
        else:
            messagebox.showerror("Error", mensaje)
            self.mostrar_estado(mensaje, "error")

    def eliminar_programa(self):
        if not self.programa_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un programa de la lista")
            return
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Eliminar este programa permanentemente?\n\n⚠️ Acción irreversible"):
            success, mensaje = self.service.eliminar_programa(self.programa_seleccionado)
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_programas()
                self.programa_seleccionado = None
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, tk.END)
        self.descripcion_entry.delete(0, tk.END)
        self.horario_combo.set("Nocturno")
        self.precio_entry.delete(0, tk.END)
        self.estado_combo.set("Activo")
        self.programa_seleccionado = None



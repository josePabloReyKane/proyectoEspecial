import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from services.docente_service import DocenteService

class DocenteView:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Docentes")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        self.service = DocenteService()
        self.docente_seleccionado = None
        self.lista_profesiones = []

        self.centrar_ventana()
        self.crear_widgets()
        self.cargar_profesiones()
        self.cargar_docentes()

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

        title_label = tk.Label(main_frame, text="GESTIÓN DE DOCENTES",
                               font=("Arial", 16, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # --- FORMULARIO ---
        form_frame = ttk.LabelFrame(content_frame, text="📋 Datos del Docente", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        for i in range(8):
            form_frame.grid_rowconfigure(i, pad=5)
        form_frame.grid_columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Identificación:*", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.identificacion_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.identificacion_entry.grid(row=0, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Nombre Completo:*", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nombre_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.nombre_entry.grid(row=1, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Email:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.email_entry.grid(row=2, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Teléfono:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.telefono_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.telefono_entry.grid(row=3, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Dirección:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.direccion_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.direccion_entry.grid(row=4, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Profesión:*", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.profesion_combo = ttk.Combobox(form_frame, width=32, font=("Arial", 10), state="readonly")
        self.profesion_combo.grid(row=5, column=1, pady=5, padx=10, sticky=tk.W)

        tk.Label(form_frame, text="Especialidad:", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.especialidad_entry = ttk.Entry(form_frame, width=35, font=("Arial", 10))
        self.especialidad_entry.grid(row=6, column=1, pady=5, padx=10, sticky=tk.W+tk.E)

        tk.Label(form_frame, text="Estado:*", font=("Arial", 10)).grid(row=7, column=0, sticky=tk.W, pady=5)
        self.estado_combo = ttk.Combobox(form_frame, values=["Activo", "Inactivo"],
                                         width=32, font=("Arial", 10), state="readonly")
        self.estado_combo.grid(row=7, column=1, pady=5, padx=10, sticky=tk.W)
        self.estado_combo.set("Activo")

        tk.Label(form_frame, text="* Campos requeridos", font=("Arial", 8, "italic"),
                 fg="red").grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=10)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="➕ Nuevo", command=self.nuevo_docente, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="💾 Guardar", command=self.guardar_docente, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🔄 Actualizar", command=self.actualizar_docente, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_docente, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🧹 Limpiar", command=self.limpiar_formulario, width=12).pack(side=tk.LEFT, padx=3)

        # --- LISTA DE DOCENTES ---
        list_frame = ttk.LabelFrame(content_frame, text="📊 Lista de Docentes", padding="15")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=25, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar_docentes())

        ttk.Button(search_frame, text="⟲ Refrescar", command=self.cargar_docentes).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'identificacion', 'nombre', 'email', 'telefono', 'profesion', 'estado')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        self.tree.heading('id', text='ID')
        self.tree.heading('identificacion', text='Identificación')
        self.tree.heading('nombre', text='Nombre Completo')
        self.tree.heading('email', text='Email')
        self.tree.heading('telefono', text='Teléfono')
        self.tree.heading('profesion', text='Profesión')
        self.tree.heading('estado', text='Estado')

        self.tree.column('id', width=50, minwidth=50)
        self.tree.column('identificacion', width=100, minwidth=100)
        self.tree.column('nombre', width=200, minwidth=150)
        self.tree.column('email', width=150, minwidth=120)
        self.tree.column('telefono', width=80, minwidth=80)
        self.tree.column('profesion', width=120, minwidth=100)
        self.tree.column('estado', width=70, minwidth=70)

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.tag_configure('oddrow', background='#f2f2f2')
        self.tree.tag_configure('evenrow', background='white')

        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(15, 0))

        btn_atras = tk.Button(nav_frame, text="⬅️ Volver al Menú",
                              command=self.volver_menu,
                              bg="#3498db", fg="white",
                              font=("Arial", 10, "bold"),
                              width=15,
                              relief=tk.RAISED, bd=3,
                              cursor="hand2")
        btn_atras.pack(side=tk.LEFT, padx=5)

        self.contador_label = tk.Label(nav_frame, text="Total: 0 registros",
                                       font=("Arial", 9), fg="#7f8c8d")
        self.contador_label.pack(side=tk.RIGHT, padx=5)

        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self.status_bar = tk.Label(main_frame, text="✅ Listo", bd=1,
                                    relief=tk.SUNKEN, anchor=tk.W,
                                    bg='#ecf0f1', fg='#2c3e50',
                                    font=("Arial", 8))
        self.status_bar.pack(fill=tk.X)

    def cargar_profesiones(self):
        try:
            profesiones, error = self.service.obtener_profesiones()
            if error:
                messagebox.showerror("Error", error)
                return
            
            self.lista_profesiones = profesiones
            profesiones_display = [p['descripcion'] for p in profesiones]
            self.profesion_combo['values'] = profesiones_display
            
            if profesiones:
                self.profesion_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar profesiones: {str(e)}")

    def cargar_docentes(self):
        try:
            docentes, error = self.service.obtener_docentes()
            if error:
                self.mostrar_estado(f"Error: {error}", "error")
                messagebox.showerror("Error", error)
                return

            for row in self.tree.get_children():
                self.tree.delete(row)

            for i, doc in enumerate(docentes):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end',
                               values=(
                                   doc['id_docente'],
                                   doc['identificacion'],
                                   doc['nombre_completo'],
                                   doc['email'],
                                   doc['telefono'],
                                   doc['profesion'],
                                   doc['estado']
                               ),
                               tags=(tag,),
                               iid=str(doc['id_docente']))

            self.actualizar_contador(len(docentes))
            self.mostrar_estado(f"✅ {len(docentes)} docentes cargados", "success")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")
            messagebox.showerror("Error", f"Error al cargar docentes: {str(e)}")

    def buscar_docentes(self):
        busqueda = self.search_entry.get().strip().lower()
        if not busqueda:
            self.cargar_docentes()
            return

        try:
            docentes, error = self.service.obtener_docentes()
            if error:
                return

            for row in self.tree.get_children():
                self.tree.delete(row)

            count = 0
            for i, doc in enumerate(docentes):
                if (busqueda in doc['nombre_completo'].lower() or
                    busqueda in doc['identificacion'].lower()):
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert('', 'end',
                                   values=(
                                       doc['id_docente'],
                                       doc['identificacion'],
                                       doc['nombre_completo'],
                                       doc['email'],
                                       doc['telefono'],
                                       doc['profesion'],
                                       doc['estado']
                                   ),
                                   tags=(tag,),
                                   iid=str(doc['id_docente']))
                    count += 1

            self.actualizar_contador(count)
            self.mostrar_estado(f"🔍 {count} resultados para '{busqueda}'")
        except Exception as e:
            self.mostrar_estado(f"Error en búsqueda: {str(e)}", "error")

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        id_docente = int(seleccion[0])
        try:
            docente, error = self.service.obtener_docente_por_id(id_docente)
            if error:
                self.mostrar_estado(f"Error: {error}", "error")
                return

            if docente:
                self.docente_seleccionado = id_docente
                self.mostrar_docente_en_formulario(docente)
                self.mostrar_estado(f"📋 Docente seleccionado: {docente['nombre_completo']}")
        except Exception as e:
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def mostrar_docente_en_formulario(self, docente):
        self.identificacion_entry.delete(0, tk.END)
        self.identificacion_entry.insert(0, docente['identificacion'] or '')

        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, docente['nombre_completo'] or '')

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, docente['email'] or '')

        self.telefono_entry.delete(0, tk.END)
        self.telefono_entry.insert(0, docente['telefono'] or '')

        self.direccion_entry.delete(0, tk.END)
        self.direccion_entry.insert(0, docente['direccion'] or '')

        profesion_id = docente['id_profesion']
        for p in self.lista_profesiones:
            if p['id_profesion'] == profesion_id:
                self.profesion_combo.set(p['descripcion'])
                break

        self.especialidad_entry.delete(0, tk.END)
        self.especialidad_entry.insert(0, docente['especialidad'] or '')

        self.estado_combo.set(docente['estado'])

    def obtener_datos_formulario(self):
        profesion_desc = self.profesion_combo.get()
        id_profesion = None
        for p in self.lista_profesiones:
            if p['descripcion'] == profesion_desc:
                id_profesion = p['id_profesion']
                break

        return {
            'identificacion': self.identificacion_entry.get().strip(),
            'nombre_completo': self.nombre_entry.get().strip(),
            'email': self.email_entry.get().strip() or '',
            'telefono': self.telefono_entry.get().strip() or '',
            'direccion': self.direccion_entry.get().strip() or '',
            'id_profesion': id_profesion,
            'especialidad': self.especialidad_entry.get().strip() or '',
            'estado': self.estado_combo.get()
        }

    def guardar_docente(self):
        if not self.validar_campos_requeridos():
            return

        try:
            datos = self.obtener_datos_formulario()
            success, mensaje = self.service.crear_docente(datos)

            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_docentes()
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def actualizar_docente(self):
        if not self.docente_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar un docente de la lista")
            return

        if not self.validar_campos_requeridos():
            return

        try:
            datos = self.obtener_datos_formulario()
            success, mensaje = self.service.actualizar_docente(self.docente_seleccionado, datos)

            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.mostrar_estado(mensaje, "success")
                self.limpiar_formulario()
                self.cargar_docentes()
                self.docente_seleccionado = None
            else:
                messagebox.showerror("Error", mensaje)
                self.mostrar_estado(mensaje, "error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.mostrar_estado(f"Error: {str(e)}", "error")

    def eliminar_docente(self):
        if not self.docente_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar un docente de la lista")
            return

        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Está seguro de eliminar ESTE DOCENTE?\n\n"
                               "⚠️ Esta acción eliminará TODOS los datos del docente\n"
                               "de la base de datos permanentemente."):
            try:
                success, mensaje = self.service.eliminar_docente(self.docente_seleccionado)

                if success:
                    messagebox.showinfo("Éxito", mensaje)
                    self.mostrar_estado(mensaje, "success")
                    self.limpiar_formulario()
                    self.cargar_docentes()
                    self.docente_seleccionado = None
                else:
                    messagebox.showerror("Error", mensaje)
                    self.mostrar_estado(mensaje, "error")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.mostrar_estado(f"Error: {str(e)}", "error")

    def nuevo_docente(self):
        self.limpiar_formulario()
        self.docente_seleccionado = None
        self.mostrar_estado("📝 Nuevo docente - Complete los campos")

    def limpiar_formulario(self):
        self.identificacion_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)
        self.especialidad_entry.delete(0, tk.END)
        if self.lista_profesiones:
            self.profesion_combo.current(0)
        self.estado_combo.set("Activo")

    def validar_campos_requeridos(self):
        if not self.identificacion_entry.get().strip():
            messagebox.showwarning("Validación", "La identificación es requerida")
            self.identificacion_entry.focus()
            return False

        if not self.nombre_entry.get().strip():
            messagebox.showwarning("Validación", "El nombre completo es requerido")
            self.nombre_entry.focus()
            return False

        if not self.profesion_combo.get():
            messagebox.showwarning("Validación", "Debe seleccionar una profesión")
            self.profesion_combo.focus()
            return False

        return True

    def volver_menu(self):
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.root.destroy()

    def actualizar_contador(self, cantidad):
        self.contador_label.config(text=f"Total: {cantidad} registros")

    def mostrar_estado(self, mensaje, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "error": "#e74c3c"}
        self.status_bar.config(text=mensaje, fg=colores.get(tipo, "#2c3e50"))

if __name__ == "__main__":
    root = tk.Tk()
    app = DocenteView(root)
    root.mainloop()
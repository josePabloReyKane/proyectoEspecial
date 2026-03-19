from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from app.db.connection import connect_sql_auth
from app.services.auth_service import usuario_existe

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIS-Universitario - Login")
        self.resizable(False, False)

        self.usuario_var = tk.StringVar()
        self.contra_var = tk.StringVar()

        frm = ttk.Frame(self, padding=16)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Usuario (SQL Auth):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.usuario_var, width=34).grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(frm, text="Contraseña (SQL Auth):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.contra_var, show="*", width=34).grid(row=3, column=0, sticky="ew", pady=(4, 14))

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, sticky="ew")
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)

        ttk.Button(btns, text="Cancelar", command=self._cancel).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Aceptar", command=self._login).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Return>", lambda _e: self._login())
        self.bind("<Escape>", lambda _e: self._cancel())

        # Resultado
        self.cred: dict[str, str] | None = None

    def _cancel(self):
        self.cred = None
        self.destroy()

    def _login(self):
        usuario = (self.usuario_var.get() or "").strip()
        contra = (self.contra_var.get() or "").strip()

        if not usuario or not contra:
            messagebox.showwarning("Validación", "Debe ingresar usuario y contraseña.")
            return

        try:
            conn = connect_sql_auth(usuario, contra)
        except Exception as e:
            messagebox.showerror("Login", f"No se pudo conectar a SQL Server.\nDetalle: {e}")
            return

        try:
            if not usuario_existe(conn, usuario):
                messagebox.showwarning("Login", "Credenciales válidas, pero el usuario no existe en dbo.Usuarios.")
                return
        except Exception as e:
            messagebox.showerror("Login", f"Error consultando dbo.Usuarios.\nDetalle: {e}")
            return
        finally:
            try:
                conn.close()
            except Exception:
                pass

        self.cred = {"usuario": usuario, "contra": contra}
        self.destroy()

def run_login_window() -> dict[str, str] | None:
    win = LoginWindow()
    win.mainloop()
    return win.cred

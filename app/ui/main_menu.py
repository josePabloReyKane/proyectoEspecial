from __future__ import annotations

import tkinter as tk
from tkinter import ttk

class MainMenuWindow(tk.Tk):
    def __init__(self, usuario: str):
        super().__init__()
        self.title("SIS-Universitario - Menú Principal")
        self.state("zoomed")  # pantalla completa en Windows

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text=f"Bienvenido: {usuario}").pack(side="left")
        ttk.Button(top, text="Salir", command=self.destroy).pack(side="right")

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        # Placeholder mínimo (para que el proyecto no esté vacío)
        card = ttk.LabelFrame(body, text="Entregable #2", padding=12)
        card.pack(fill="x", anchor="n")

        ttk.Label(
            card,
            text=(
                "Este menú es un placeholder básico.\n"
                "Ya valida conexión SQL Auth y existencia de usuario en dbo.Usuarios."
            ),
            justify="left",
        ).pack(anchor="w")

def run_main_menu(usuario: str):
    win = MainMenuWindow(usuario=usuario)
    win.mainloop()

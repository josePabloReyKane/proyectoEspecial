import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from views.login_view import LoginView

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginView(root)
    root.mainloop()
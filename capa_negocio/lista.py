import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from capa_datos.database import listar_password
import pyperclip
from tkinter import Frame, Canvas

class ListaContraseñas(ttk.Frame):
    def __init__(self, master, usuario_id):
        super().__init__(master)
        self.usuario_id = usuario_id
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Limpiar contenido existente antes de agregar nuevos elementos
        for widget in self.winfo_children():
            widget.destroy()

        # Contenedor principal para Canvas y Scrollbar
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Crear canvas y scrollbar
        self.canvas = Canvas(container, borderwidth=0, background="#2b2b2b")
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Scroll
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel) 
        self.canvas.bind_all("<Button-5>", self.on_mousewheel) 

        # Título de la sección, centrado
        title_label = ttk.Label(self.scrollable_frame, text="Lista de Contraseñas", font=("Helvetica", 12, "bold"))
        title_label.pack(pady=5)
        title_label.pack_configure(anchor="center")

        # Verificar si el usuario está autenticado
        if not self.usuario_id:
            ttk.Label(self.scrollable_frame, text="No se ha encontrado una ID de usuario válida.").pack(pady=10)
            return

        # Obtener la lista de contraseñas desde la base de datos
        self.contraseñas_almacenadas = listar_password(self.usuario_id)

        if not self.contraseñas_almacenadas:
            ttk.Label(self.scrollable_frame, text="No se encontraron contraseñas para este usuario.").pack(pady=10)
            return

        # Mostrar lista de contraseñas
        for idx, item in enumerate(self.contraseñas_almacenadas, start=1):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill="x", pady=5)

            ttk.Label(frame, text=f"{idx}. Título: {item['titulo']}").pack(anchor="w")
            ttk.Label(frame, text=f"   Descripción: {item['descripcion']}").pack(anchor="w")

            password_label = ttk.Label(frame, text="   Contraseña: ********")
            password_label.pack(anchor="w")

            # Mensaje de copia al portapapeles
            copy_message = ttk.Label(frame, text="", foreground="green")
            copy_message.pack(anchor="w")

            # Botones de Ver y Copiar
            ver_button = ttk.Button(
                frame, text="Ver Contraseña", bootstyle="info",
                command=lambda i=idx-1, lbl=password_label: self.ver_contraseña(i, lbl)
            )
            ver_button.pack(side="left", padx=5)

            copiar_button = ttk.Button(
                frame, text="Copiar Contraseña", bootstyle="success",
                command=lambda i=idx-1, lbl=copy_message: self.copiar_contraseña(i, lbl)
            )
            copiar_button.pack(side="left", padx=5)

    def ver_contraseña(self, indice, label):
        # Obtener la contraseña desencriptada directamente
        contraseña_desencriptada = self.contraseñas_almacenadas[indice]['password_desencriptada']
        label.config(text=f"   Contraseña: {contraseña_desencriptada}")

    def copiar_contraseña(self, indice, label):
        # Copiar la contraseña al portapapeles
        contraseña_desencriptada = self.contraseñas_almacenadas[indice]['password_desencriptada']
        pyperclip.copy(contraseña_desencriptada)
        label.config(text="La contraseña fue copiada al portapapeles")

        self.after(2000, lambda: label.config(text=""))

    def on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

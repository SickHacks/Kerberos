import string
import random
import base64
import ttkbootstrap as ttk
from tkinter import IntVar, BooleanVar, StringVar
from capa_datos.database import almacenar_password, obtener_datos_usuario

class GeneradorContraseña(ttk.Frame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id  
        self.pack(pady=20)

        # Variables
        self.longitud = IntVar(value=8)
        self.usar_letras = BooleanVar(value=True)
        self.usar_numeros = BooleanVar(value=True)
        self.usar_simbolos = BooleanVar(value=True)
        self.contraseña_generada = StringVar()
        self.titulo = ""
        self.descripcion = ""

        # Interfaz gráfica
        self.create_widgets()

    def create_widgets(self):
        # Título de la sección
        ttk.Label(self, text="Contraseña generada", font=("Helvetica", 12), foreground="lightblue").pack(pady=5)
        # Mostrar contraseña generada
        self.generada_label = ttk.Label(self, textvariable=self.contraseña_generada, font=("Helvetica", 10))
        self.generada_label.pack(pady=(0, 10))

        # Control de longitud de contraseña
        ttk.Label(self, text="Longitud de la contraseña:").pack(pady=5)
        self.longitud_label = ttk.Label(self, text=f"{self.longitud.get()} caracteres")
        self.longitud_label.pack()
        longitud_scale = ttk.Scale(self, from_=8, to=32, variable=self.longitud, orient="horizontal",
                                   command=self.actualizar_longitud)
        longitud_scale.pack(fill="x", padx=20)

        # Opciones de caracteres
        ttk.Checkbutton(self, text="Incluir letras", variable=self.usar_letras).pack(anchor="w", padx=20)
        ttk.Checkbutton(self, text="Incluir números", variable=self.usar_numeros).pack(anchor="w", padx=20)
        ttk.Checkbutton(self, text="Incluir símbolos", variable=self.usar_simbolos).pack(anchor="w", padx=20)

        # Botón para generar la contraseña
        ttk.Button(self, text="Generar contraseña", bootstyle="info", command=self.generar_contraseña).pack(pady=10)

        # Campos de entrada para título y descripción
        ttk.Label(self, text="Título:").pack(pady=5)
        self.entry_titulo = ttk.Entry(self)
        self.entry_titulo.pack(fill="x", padx=20)

        ttk.Label(self, text="Descripción:").pack(pady=5)
        self.entry_descripcion = ttk.Entry(self)
        self.entry_descripcion.pack(fill="x", padx=20)

        # Botón para guardar la contraseña
        ttk.Button(self, text="Guardar contraseña", bootstyle="success", command=self.guardar_contraseña).pack(pady=20)

        # Mensaje de estado
        self.status_label = ttk.Label(self, text="", font=("Helvetica", 10), foreground="green")
        self.status_label.pack(pady=(10, 0))

    def actualizar_longitud(self, event=None):
        """Actualizar la etiqueta de longitud cuando se mueve la barra"""
        self.longitud_label.config(text=f"{self.longitud.get()} caracteres")

    def generar_contraseña(self):
        caracteres = ""
        if self.usar_letras.get():
            caracteres += string.ascii_letters
        if self.usar_numeros.get():
            caracteres += string.digits
        if self.usar_simbolos.get():
            caracteres += "@&$!#?"

        if caracteres:
            self.contraseña_generada.set(''.join(random.choice(caracteres) for _ in range(self.longitud.get())))
            print(f"[+] Contraseña generada: {self.contraseña_generada.get()}") 

    def encriptar_contraseña(self, contraseña):
        contraseña_bytes = contraseña.encode('utf-8')
        contraseña_encriptada = base64.b64encode(contraseña_bytes)
        return contraseña_encriptada.decode('utf-8')

    def guardar_contraseña(self):
        id_usuario = self.user_id  

        self.titulo = self.entry_titulo.get()
        self.descripcion = self.entry_descripcion.get()

        if self.contraseña_generada.get() and self.titulo and self.descripcion:
            contraseña_encriptada = self.encriptar_contraseña(self.contraseña_generada.get())
            almacenar_password(id_usuario, self.titulo, self.descripcion, contraseña_encriptada)
            print("[+] Contraseña guardada exitosamente")  

            # Mostrar mensaje de confirmación en status_label
            self.status_label.config(
                text="Contraseña guardada",
                foreground="white"
            )
        else:
            print("[!] Debe completar todos los campos antes de guardar la contraseña.")
            self.status_label.config(
                text="Debe completar todos los campos antes de guardar la contraseña.",
                foreground="red"
            )

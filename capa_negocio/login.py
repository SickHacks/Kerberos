import os
import hashlib
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from capa_datos.database import (
    obtener_datos_usuario, 
    actualizar_intentos_fallidos, 
    registrar_usuario,
    almacenar_datos_registro
)
from capa_negocio.utils import mostrar_datos_registro

class LoginScreen(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success  # Callback para el éxito en el login
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def create_widgets(self):
        # Título principal
        self.title_label = ttk.Label(self, text="KERBEROS", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        # Subtítulo
        self.subtitle_label = ttk.Label(self, text="Gestor de contraseñas", font=("Helvetica", 12))
        self.subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))

        # Campo de correo electrónico
        self.email_label = ttk.Label(self, text="Correo Electrónico", anchor="center")
        self.email_label.grid(row=2, column=0, columnspan=2)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=3, column=0, columnspan=2, pady=5)

        # Campo de contraseña maestra
        self.password_label = ttk.Label(self, text="Contraseña Maestra", anchor="center")
        self.password_label.grid(row=4, column=0, columnspan=2)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=5, column=0, columnspan=2, pady=5)

        # Campo de confirmación de contraseña (visible solo en modo registro)
        self.confirm_password_label = ttk.Label(self, text="Repita Contraseña Maestra", anchor="center")
        self.confirm_password_entry = ttk.Entry(self, show="*")

        # Campo para la ruta del archivo binario (2FA)
        self.filepath_label = ttk.Label(self, text="Ruta del Archivo Binario (2FA)", anchor="center")
        self.filepath_entry = ttk.Entry(self)

        self.or_label = ttk.Label(self, text="ó", font=("Helvetica", 10))

        # Botón para adjuntar archivo binario
        self.archivo_button = ttk.Button(self, text="Adjuntar archivo binario", bootstyle=INFO, command=self.seleccionar_archivo)

        # Botones de acción para iniciar sesión o crear cuenta
        self.action_button = ttk.Button(self, text="Iniciar Sesión", command=self.login, bootstyle="success")
        self.toggle_button = ttk.Button(self, text="Crear cuenta", command=self.toggle_mode)

        # Mensaje de estado
        self.status_label = ttk.Label(self, text="", foreground="red")
        self.status_label.grid(row=12, column=0, columnspan=2, pady=(10, 0))

        # Colocar elementos para el modo de inicio de sesión
        self.display_login_mode()

    def display_login_mode(self):
        """Configura los elementos para el modo de inicio de sesión."""
        self.subtitle_label.config(text="Gestor de contraseñas")
        self.action_button.config(text="Iniciar Sesión", command=self.login)
        self.toggle_button.config(text="Crear cuenta", command=self.toggle_mode)
        self.email_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        self.email_entry.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        self.password_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        self.password_entry.grid(row=5, column=0, columnspan=2, pady=(0, 15))
        self.filepath_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))
        self.filepath_entry.grid(row=7, column=0, columnspan=2, pady=(0, 5))
        self.or_label.grid(row=8, column=0, columnspan=2, pady=(0, 5))
        self.archivo_button.grid(row=9, column=0, columnspan=2, pady=(5, 15))
        self.action_button.grid(row=10, column=0, columnspan=2, pady=(0, 5))
        self.toggle_button.grid(row=11, column=0, columnspan=2, pady=5)
        self.confirm_password_label.grid_remove()
        self.confirm_password_entry.grid_remove()

    def display_register_mode(self):
        """Configura los elementos para el modo de registro."""
        self.subtitle_label.config(text="Creación de cuenta")
        self.action_button.config(text="Confirmar creación de cuenta", command=self.register)
        self.toggle_button.config(text="Volver a inicio de sesión", command=self.toggle_mode)
        self.email_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        self.email_entry.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        self.password_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        self.password_entry.grid(row=5, column=0, columnspan=2, pady=(0, 15))
        self.confirm_password_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))
        self.confirm_password_entry.grid(row=7, column=0, columnspan=2, pady=(0, 15))
        self.action_button.grid(row=8, column=0, columnspan=2, pady=(0, 5))
        self.toggle_button.grid(row=9, column=0, columnspan=2, pady=5)
        self.filepath_label.grid_remove()
        self.filepath_entry.grid_remove()
        self.or_label.grid_remove()
        self.archivo_button.grid_remove()

    def toggle_mode(self):
        """Alterna entre el modo de inicio de sesión y el modo de registro."""
        if self.action_button['text'] == "Iniciar Sesión":
            self.display_register_mode()
        else:
            self.display_login_mode()

    def seleccionar_archivo(self):
        """Abre el diálogo para seleccionar un archivo binario 2FA."""
        archivo = filedialog.askopenfilename(filetypes=[("Archivos binarios", "*.bin")])
        if archivo:
            self.filepath_entry.delete(0, 'end')
            self.filepath_entry.insert(0, archivo)

    def register(self):
        """Función para registrar un nuevo usuario."""
        correo = self.email_entry.get()
        contraseña_maestra = self.password_entry.get()
        confirmar_contraseña = self.confirm_password_entry.get()

        # Validar si las contraseñas coinciden
        if contraseña_maestra != confirmar_contraseña:
            self.status_label.config(text="[!] Las contraseñas no coinciden. Intente de nuevo.")
            return

        # Generar hash de la contraseña y archivo binario para 2FA
        hash_contraseña = hashlib.sha256(contraseña_maestra.encode()).hexdigest()
        binario_2fa = os.urandom(32)

        # Abrir diálogo para que el usuario elija la ubicación de guardado del archivo binario
        filepath = filedialog.asksaveasfilename(
            defaultextension=".bin",
            filetypes=[("Archivo binario", "*.bin")],
            initialfile=f"{correo.split('@')[0]}_2fa.bin",
            title="Guardar archivo 2FA"
        )

        if not filepath:  # Si el usuario cancela la selección
            self.status_label.config(text="No se ha seleccionado una ubicación para el archivo 2FA.")
            return

        # Guardar el archivo binario en la ubicación seleccionada
        with open(filepath, 'wb') as file:
            file.write(binario_2fa)

        # Registrar usuario en la base de datos
        registrar_usuario(correo, hash_contraseña, binario_2fa)
        self.status_label.config(
            text="Cuenta creada exitosamente\nArchivo 2FA guardado en la ubicación seleccionada.\nEste archivo se necesita para iniciar sesión en el programa",
            foreground="white",
            anchor="center",
            justify="center"
        )

    def login(self):
        """Función para iniciar sesión del usuario con verificación de 2FA."""
        correo = self.email_entry.get()
        contraseña_maestra = self.password_entry.get()
        archivo_2fa = self.filepath_entry.get()
        
        datos_usuario = obtener_datos_usuario(correo)

        if datos_usuario is None:
            self.status_label.config(text=f"[!] No existe una cuenta asociada a {correo}")
            return

        # Verificar si la cuenta está bloqueada
        if datos_usuario["bloqueado_usuario"]:
            self.status_label.config(text="[!] La cuenta está bloqueada.", foreground="red")
            self.crear_registro_sesion(datos_usuario["id_usuario"], "Bloqueado")
            return

        # Verificar contraseña
        hash_contraseña = hashlib.sha256(contraseña_maestra.encode()).hexdigest()
        if datos_usuario["password_usuario"] != hash_contraseña:
            self.status_label.config(text="[!] Contraseña incorrecta.")
            actualizar_intentos_fallidos(correo, False)
            return

        # Verificar archivo binario 2FA
        if not archivo_2fa or not os.path.exists(archivo_2fa):
            self.status_label.config(text="[!] Archivo 2FA no seleccionado o no encontrado.")
            actualizar_intentos_fallidos(correo, False)
            return

        with open(archivo_2fa, 'rb') as f:
            contenido_2fa = f.read()

        if contenido_2fa != datos_usuario["binario_2fa"]:
            self.status_label.config(text="[!] Archivo 2FA incorrecto.")
            actualizar_intentos_fallidos(correo, False)
            return

        # Si todo es correcto, autenticación exitosa
        self.on_login_success(datos_usuario["id_usuario"])
        self.status_label.config(text="Autenticación exitosa. Bienvenido.", foreground="white")
        self.crear_registro_sesion(datos_usuario["id_usuario"], "Exitoso")

    def crear_registro_sesion(self, id_usuario, resultado):
        """Crea un registro de sesión con el resultado de la autenticación."""
        datos_dispositivo = mostrar_datos_registro()
        almacenar_datos_registro(
            id_usuario, 
            datos_dispositivo['ip'], 
            datos_dispositivo['pais'], 
            datos_dispositivo['region'], 
            datos_dispositivo['ciudad'], 
            datos_dispositivo['os'], 
            datos_dispositivo['dispositivo'], 
            resultado
        )

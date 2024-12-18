import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from capa_datos.database import listar_registros
from capa_negocio.utils import obtener_info_dispositivo, enviar_alerta_cuenta_bloqueada, mostrar_datos_registro

class RegistroSesion(ttk.Frame):
    def __init__(self, master, usuario_id):
        super().__init__(master)
        self.usuario_id = usuario_id  # Recibimos el usuario_id como argumento
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
 
        for widget in self.winfo_children():
            widget.destroy()

        # Contenedor principal para Canvas y Scrollbar
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Crear canvas y scrollbar
        self.canvas = ttk.Canvas(container, borderwidth=0, background="#2b2b2b")
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Scrollbar vertical
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empacar el canvas y el scrollbar en el contenedor
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Título de la sección, centrado
        title_label = ttk.Label(self.scrollable_frame, text="Registro de Sesión", font=("Helvetica", 12, "bold"))
        title_label.pack(pady=5)
        title_label.pack_configure(anchor="center")

        # Verificar si el usuario está autenticado
        if not self.usuario_id:
            ttk.Label(self.scrollable_frame, text="No se ha encontrado una ID de usuario válida.").pack(pady=10)
            return

        # Obtener los registros de inicio de sesión desde la base de datos
        self.registros_almacenados = listar_registros(self.usuario_id)

        if not self.registros_almacenados:
            ttk.Label(self.scrollable_frame, text="No se encontraron registros de inicio de sesión para este usuario.").pack(pady=10)
            return

        # Mostrar registros
        for idx, registro in enumerate(self.registros_almacenados, start=1):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill="x", pady=5)

            ttk.Label(frame, text=f"{idx}. Resultado: {registro['resultado']}").pack(anchor="w")
            ttk.Label(frame, text=f"   IP: {registro['ip']}").pack(anchor="w")
            ttk.Label(frame, text=f"   País: {registro['pais']}").pack(anchor="w")
            ttk.Label(frame, text=f"   Región: {registro['region']}").pack(anchor="w")
            ttk.Label(frame, text=f"   Ciudad: {registro['ciudad']}").pack(anchor="w")
            ttk.Label(frame, text=f"   Sistema Operativo: {registro['os']}").pack(anchor="w")
            ttk.Label(frame, text=f"   Dispositivo: {registro['dispositivo']}").pack(anchor="w")
            ttk.Label(frame, text="-" * 50).pack(anchor="w")

    def refresh_content(self):
        """Método para refrescar el contenido de la lista de registros."""
        self.create_widgets()

    def on_mousewheel(self, event):
        # Control del scroll con rueda del ratón
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

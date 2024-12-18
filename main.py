import ttkbootstrap as ttk
from capa_negocio.login import LoginScreen
from capa_negocio.generador import GeneradorContraseña
from capa_negocio.lista import ListaContraseñas
from capa_negocio.registro_ingresos import RegistroSesion

class KerberosApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")  
        self.title("KERBEROS")
        self.geometry("600x700")

        self.login_screen = LoginScreen(self, self.on_login_success)
        self.main_frame = None
        self.user_id = None
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_frame()
        self.login_screen.pack(pady=50)

    def on_login_success(self, user_id):
        # Llamado cuando el login es exitoso, recibe el user_id
        self.user_id = user_id
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_frame()

        # Crear el notebook para las pestañas
        self.main_frame = ttk.Notebook(self)
        self.main_frame.pack(fill="both", expand=True)

        self.generador_tab = GeneradorContraseña(self.main_frame, self.user_id)
        self.lista_tab = ListaContraseñas(self.main_frame, self.user_id)
        self.registro_tab = RegistroSesion(self.main_frame, self.user_id)

   
        self.main_frame.add(self.generador_tab, text="Generador")
        self.main_frame.add(self.lista_tab, text="Lista de Contraseñas")
        self.main_frame.add(self.registro_tab, text="Registro de Sesión")

  
        self.main_frame.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):

        selected_tab = self.main_frame.select()
        selected_widget = self.main_frame.nametowidget(selected_tab)

        # Llamar al método de actualización de la pestaña seleccionada
        if isinstance(selected_widget, ListaContraseñas):
            selected_widget.create_widgets()  
        elif isinstance(selected_widget, RegistroSesion):
            selected_widget.create_widgets() 


    def clear_frame(self):
        if self.main_frame:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            self.main_frame.destroy()
        elif self.login_screen:
            self.login_screen.pack_forget()

if __name__ == "__main__":
    app = KerberosApp()
    app.mainloop()

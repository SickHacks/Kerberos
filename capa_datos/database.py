import mysql.connector
from mysql.connector import Error
import base64
from capa_negocio.utils import enviar_alerta_cuenta_bloqueada, mostrar_datos_registro  # Cambiamos la importación

# Valores para el envío de correo de alerta
email_sender = ''
email_password = ''
#----------------  INICAR Y CERRAR CONEXIÓN CON LA BASE DE DATOS  ---------------
def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host='',
            database='',
            user='', 
            password='' 
        )
        if conexion.is_connected():
            return conexion       
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def cerrar_conexion(conexion):
    """Cierra la conexión a la base de datos."""
    if conexion.is_connected():
        conexion.close()
        print("")


# Función para desencriptar contraseña en base64
def desencriptar_contraseña(contraseña_encriptada):
    contraseña_bytes = base64.b64decode(contraseña_encriptada)
    return contraseña_bytes.decode('utf-8')
#--------------------------------------------------------------------------------

### Registrar un usuario en la base de datos ###
def registrar_usuario(email_usuario, password_usuario, binario_2fa):
    conexion = crear_conexion()

    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        sql_insert_query = """INSERT INTO USUARIO 
                              (EMAIL_USUARIO, PASSWORD_USUARIO, BINARIO_2FA) 
                              VALUES (%s, %s, %s)"""
        cursor.execute(sql_insert_query, (email_usuario, password_usuario, binario_2fa))
        conexion.commit()
    except Error as e:
        print(f"Error al registrar el usuario: {e}")
    finally:
        cerrar_conexion(conexion)

def obtener_datos_usuario(email_usuario):
    conexion = crear_conexion()

    if conexion is None:
        return None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT ID_USUARIO, EMAIL_USUARIO, PASSWORD_USUARIO, BINARIO_2FA, BLOQUEADO_USUARIO, INTENTOS_FALLIDOS, FECHA_BLOQUEO
        FROM USUARIO
        WHERE EMAIL_USUARIO = %s
        """
        cursor.execute(query, (email_usuario,))
        datos_usuario = cursor.fetchone()

        if datos_usuario:
            return {
                "id_usuario": datos_usuario["ID_USUARIO"],
                "email_usuario": datos_usuario["EMAIL_USUARIO"],
                "password_usuario": datos_usuario["PASSWORD_USUARIO"],
                "binario_2fa": datos_usuario["BINARIO_2FA"],
                "bloqueado_usuario": bool(datos_usuario["BLOQUEADO_USUARIO"]),
                "intentos_fallidos": datos_usuario["INTENTOS_FALLIDOS"],
                "fecha_bloqueo": datos_usuario["FECHA_BLOQUEO"]
            }
        else:
            return None

    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
    finally:
        cerrar_conexion(conexion)

def actualizar_intentos_fallidos(email_usuario, login_exitoso):
    email_receiver = email_usuario
    conexion = crear_conexion()

    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        
        # Verificar si la cuenta ya está bloqueada
        cursor.execute("SELECT BLOQUEADO_USUARIO FROM USUARIO WHERE EMAIL_USUARIO = %s", (email_usuario,))
        bloqueado = cursor.fetchone()[0]
        
        if bloqueado:
         
            return

        if login_exitoso:
            # Si el login es exitoso, resetear los intentos fallidos a 0
            query = "UPDATE USUARIO SET INTENTOS_FALLIDOS = 0 WHERE EMAIL_USUARIO = %s"
            cursor.execute(query, (email_usuario,))
        else:
            # Incrementar los intentos fallidos
            query = "UPDATE USUARIO SET INTENTOS_FALLIDOS = INTENTOS_FALLIDOS + 1 WHERE EMAIL_USUARIO = %s"
            cursor.execute(query, (email_usuario,))
            
            cursor.execute("SELECT INTENTOS_FALLIDOS FROM USUARIO WHERE EMAIL_USUARIO = %s", (email_usuario,))
            intentos_fallidos = cursor.fetchone()[0]

            if intentos_fallidos >= 3:
                # Bloquear usuario si los intentos fallidos llegan a 3
                query = "UPDATE USUARIO SET BLOQUEADO_USUARIO = TRUE WHERE EMAIL_USUARIO = %s"
                cursor.execute(query, (email_usuario,))
                
                # Enviar alerta de cuenta bloqueada por correo electrónico
                enviar_alerta_cuenta_bloqueada(email_sender, email_password, email_receiver, mostrar_datos_registro())

        conexion.commit()

    except Error as e:
        print(f"Error al actualizar intentos fallidos: {e}")
    finally:
        cerrar_conexion(conexion)

### Guardar una contraseña en la base de datos y asociarle una id ###
def almacenar_password(id_usuario, titulo, descripcion, contraseña_encriptada):
    conexion = crear_conexion()

    if conexion is None:
        return
    try:
        cursor = conexion.cursor()

        query = """INSERT INTO LISTA 
                              (ID_USUARIO, TITULO, DESCRIPCION, PASSWORD_BASE64) 
                              VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (id_usuario, titulo, descripcion, contraseña_encriptada))
        conexion.commit()
        print("Contraseña registrada exitosamente")

    except Error as e:
        print(f"Error al almacenar la contraseña: {e}")
    finally:
        cerrar_conexion(conexion)

### ALMACENAR LOS DATOS DE REGISTRO DE SESIÓN ###
def almacenar_datos_registro(id_usuario, ip_registro, pais_registro, region_registro, ciudad_registro, os_registro, dispositivo_registro, result_registro):
    conexion = crear_conexion()

    if conexion is None:
        return
    try:
        cursor = conexion.cursor()

        query = """INSERT INTO REGISTRO_INGRESO 
                              (ID_USUARIO, IP_REGISTRO, PAIS_REGISTRO, REGION_REGISTRO, CIUDAD_REGISTRO, OS_REGISTRO, DISPOSITIVO_REGISTRO, RESULT_REGISTRO) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (id_usuario, ip_registro, pais_registro, region_registro, ciudad_registro, os_registro, dispositivo_registro, result_registro))
        conexion.commit()
        print("Datos de sesión almacenados exitosamente")

    except Error as e:
        print(f"Error al almacenar el registro de sesión: {e}")
    finally:
        cerrar_conexion(conexion)

### LISTAR CONTRASEÑAS PARA LA PESTAÑA LISTA ###
def listar_password(id_usuario):
    conexion = crear_conexion()

    if conexion is None:
        return []
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT TITULO, DESCRIPCION, PASSWORD_BASE64 FROM LISTA WHERE ID_USUARIO = %s
        """
        cursor.execute(query, (id_usuario,))

        # Usar fetchall para obtener todas las contraseñas
        datos_lista = cursor.fetchall()

        if datos_lista:
            # Crear una lista para almacenar todas las contraseñas desencriptadas
            lista_contraseñas = []
            for datos in datos_lista:
                # Desencriptar la contraseña
                contraseña_desencriptada = desencriptar_contraseña(datos["PASSWORD_BASE64"])
                lista_contraseñas.append({
                    "titulo": datos["TITULO"],
                    "descripcion": datos["DESCRIPCION"],
                    "password_desencriptada": contraseña_desencriptada,
                })
            return lista_contraseñas
        else:
            return []

    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return []
    finally:
        cerrar_conexion(conexion)

### LISTAR REGISTROS PARA LA PESTAÑA REGISTROS_INGRESOS ###
def listar_registros(id_usuario):
    conexion = crear_conexion()

    if conexion is None:
        return []
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT RESULT_REGISTRO, IP_REGISTRO, PAIS_REGISTRO, REGION_REGISTRO, 
        CIUDAD_REGISTRO, OS_REGISTRO, DISPOSITIVO_REGISTRO 
        FROM REGISTRO_INGRESO WHERE ID_USUARIO = %s
        """
        cursor.execute(query, (id_usuario,))

        # Usar fetchall para obtener todos los registros de inicio de sesión
        datos_registro_ingreso = cursor.fetchall()

        if datos_registro_ingreso:
            # Crear una lista para almacenar los registros de ingreso
            lista_registro_ingreso = []
            for registro in datos_registro_ingreso:
                lista_registro_ingreso.append({
                    "resultado": registro["RESULT_REGISTRO"],
                    "ip": registro["IP_REGISTRO"],
                    "pais": registro["PAIS_REGISTRO"],
                    "region": registro["REGION_REGISTRO"],
                    "ciudad": registro["CIUDAD_REGISTRO"],
                    "os": registro["OS_REGISTRO"],
                    "dispositivo": registro["DISPOSITIVO_REGISTRO"]
                })
            return lista_registro_ingreso
        else:
            return []

    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return []
    finally:
        cerrar_conexion(conexion)

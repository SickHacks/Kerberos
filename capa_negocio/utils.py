import os
import ssl
import smtplib
import platform
import uuid
import requests
from email.message import EmailMessage

import os
import platform
import uuid
import requests

def obtener_info_dispositivo(archivo_oui):
    # Dirección MAC
    mac_address = uuid.getnode()
    mac_str = ':'.join(f'{(mac_address >> 8 * i) & 0xff:02x}' for i in range(5, -1, -1)).upper()

    # Cargar OUI_LIST
    lista_oui = {}
    with open(archivo_oui, 'r', encoding='utf-8') as f:
        for linea in f:
            if ' : ' in linea:
                partes = linea.split(' : ')
                oui = partes[0].strip("' ")
                nombre = partes[1].strip("' \n")
                lista_oui[oui] = nombre

    # Sistema operativo
    sistema_cliente = platform.system()
    os_cliente = {
        'Windows': 'Windows', 'Linux': 'Linux', 'AIX': 'AIX', 'FreeBSD': 'FreeBSD',
        'Darwin': 'MacOS', 'Java': 'Java Virtual Machine (JVM)', 'SunOS': 'SunOS: También conocido como Solaris'
    }.get(sistema_cliente, 'No se reconoce el sistema operativo')

    # Llamada a la API para obtener IP y ubicación
    api_key = ''
    # api.ipgeolocation.io
    url = ''
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            ip = datos_api.get('ip', 'Desconocido')
            pais = datos_api.get('country_name', 'Desconocido')
            region = datos_api.get('state_prov', 'Desconocido')
            ciudad = datos_api.get('city', 'Desconocido')
        else:
            print(f"Error en la API: {respuesta.status_code}")
            ip, pais, region, ciudad = 'Desconocido', 'Desconocido', 'Desconocido', 'Desconocido'
    except requests.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        ip, pais, region, ciudad = 'Desconocido', 'Desconocido', 'Desconocido', 'Desconocido'

    # Obtener fabricante a partir del OUI
    oui_str = mac_str[:8].replace(":", "-")
    nombre_fabricante = lista_oui.get(oui_str, 'Desconocido')

    return {
        'ip': ip,
        'pais': pais,
        'region': region,
        'ciudad': ciudad,
        'os': os_cliente,
        'dispositivo': nombre_fabricante,
        'mac': mac_str,
        'oui': oui_str
    }

def enviar_alerta_cuenta_bloqueada(email_sender, email_password, email_receiver, datos_registro):
    subject = 'Alerta: Cuenta Bloqueada'
    body = f"""
Estimado usuario,

Le informamos que su cuenta de Kerberos ha sido bloqueada debido a un exceso de intentos de inicio de sesión. Si usted realizó estas acciones, puede ignorar este aviso.

A continuación se muestra la información del intento de inicio de sesión:

Información:
IP: {datos_registro['ip']}
País: {datos_registro['pais']}
Región: {datos_registro['region']}
Ciudad: {datos_registro['ciudad']}
Sistema Operativo: {datos_registro['os']}
Dispositivo: {datos_registro['dispositivo']}
MAC: {datos_registro['mac']}

Agradecemos su comprensión.

Atentamente,

Equipo de Seguridad de Kerberos
"""

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def mostrar_datos_registro():
    archivo_oui = os.path.join(os.path.dirname(__file__), 'oui_list.txt')
    datos = obtener_info_dispositivo(archivo_oui)

    # Retorna un diccionario con la información en lugar de un string
    return {
        'ip': datos.get('ip', 'Desconocido'),
        'pais': datos.get('pais', 'Desconocido'),       
        'region': datos.get('region', 'Desconocido'),    
        'ciudad': datos.get('ciudad', 'Desconocido'),    
        'os': datos.get('os', 'Desconocido'),
        'dispositivo': datos.get('dispositivo', 'Desconocido'),
        'mac': datos.get('mac', 'Desconocido'),
        'oui': datos.get('oui', 'Desconocido')
    }


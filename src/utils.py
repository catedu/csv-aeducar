import base64
from pathlib import Path
import smtplib, ssl
import os
from time import sleep

import pandas as pd
import streamlit as st

from dotenv import load_dotenv, find_dotenv

import requests

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv("src/.env")

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
port = 587
subject = "Error en csv"
body = ""
sender_email = os.getenv("EMAIL_SENDER")
receiver_email = "asesor@catedu.es"
password = os.getenv("EMAIL_PASS")


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="subida_usuarios.csv">Descarga aquí tu archivo csv</a>'
    return href


def send_error_mail(zlx_file):
    # Crea un multipart email y setea los headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if zlx_file:
        # Open PDF file in binary mode
        with open(zlx_file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=zlx_file.split("/")[1],
        )

        # Add attachment to message and convert message to string
        message.attach(part)

    text = message.as_string()

    with smtplib.SMTP("smtp.aragon.es", port) as server:
        try:
            server.set_debuglevel(True)
            # identify ourselves, prompting server for supported features
            server.ehlo()
            server.starttls()
            server.esmtp_features["auth"] = "LOGIN"
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
            sleep(2)
        except:
            print("Error de autenticación")


def send_success_mail(filename):
    # Crea un multipart email y setea los headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    body = f"Ha sido descargado correctamente {filename}"

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    with smtplib.SMTP("smtp.aragon.es", port) as server:
        try:
            server.set_debuglevel(True)
            # identify ourselves, prompting server for supported features
            server.ehlo()
            server.starttls()
            server.esmtp_features["auth"] = "LOGIN"
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
            sleep(2)
        except:
            print("Error de autenticación")


def send_error_file(uploadedfile):
    file_path = f"data/{uploadedfile.name}"
    with open(file_path, "wb") as f:
        f.write(uploadedfile.getbuffer())
        st.error(
            "Ha habido un problema en el procesamiento del archivo. Introduce tu mail a continuación para que podamos ponernos en contacto contigo."
        )
        if mail := st.text_input(
            "correo electrónico",
            value="",
            max_chars=100,
            type="default",
            placeholder="micorreo@example.com",
            disabled=False,
        ):
            body = f"Ponerte en contacto con {mail}"
            try:
                send_error_mail(file_path)
                os.remove(file_path)
            except:
                send_error_mail(file_path)
            return st.success(
                "Gracias por enviarnos tu contacto. En breve nos pondremos en contacto contigo. Si no lo hacemos, escríbenos a soportecatedu@educa.aragon.es"
            )


def notify_conversion_success(filename):
    headers = {
        "Content-type": "application/json",
    }
    data = '{"text": "Ha sido descargado correctamente ' + filename + '"}'
    # añadir archivo adjunto a un slack webhook

    r = requests.post(
        SLACK_WEBHOOK,
        headers=headers,
        data=data,
    )
    print(r)


def notify_conversion_to_redmine(uploaded_file):
    # TODO: Terminar esta función.
    """Enviar un mensaje a redmine con el archivo adjunto
    y si la conversión ha sido exitosa o no"""
    # Obtener el nombre del archivo
    filename = os.path.basename(uploaded_file)

    # Crear el mensaje
    message = f"El archivo {filename} ha sido convertido con éxito."

    # Enviar el mensaje a Redmine
    url = "https://redmine.example.com/issues.json"
    data = {
        "issue": {
            "subject": "Archivo convertido",
            "description": message,
            "uploads": [
                {
                    "token": "TOKEN",
                    "filename": filename,
                    "content_type": "application/octet-stream",
                    "content": open(uploaded_file, "rb").read(),
                }
            ],
        }
    }
    headers = {"Content-Type": "application/json", "X-Redmine-API-Key": "API_KEY"}
    response = requests.post(url, json=data, headers=headers)

    # Comprobar si la petición ha sido exitosa
    if response.status_code == 201:
        print("Mensaje enviado a Redmine.")
    else:
        print("Error al enviar el mensaje a Redmine.")


if __name__ == "__main__":
    # send_error_mail(Path("prueba-alumnado.xls"))
    # send_success_mail("prueba-alumnado.xls")
    notify_conversion_success("hooooola.txt")

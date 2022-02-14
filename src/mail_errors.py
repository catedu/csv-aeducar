from dotenv import load_dotenv, find_dotenv

from pathlib import Path
import smtplib, ssl
import os
from time import sleep

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv("src/.env")

port = 587
subject = "Error en csv"
body = ""
sender_email = os.getenv("EMAIL_SENDER")
receiver_email = "asesor@catedu.es"
password = os.getenv("EMAIL_PASS")


def send_mail(csv_file=None):
    # Crea un multipart email y setea los headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if csv_file:
        # Open PDF file in binary mode
        with open(csv_file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {csv_file}",
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


if __name__ == "__main__":
    send_mail(Path("prueba-alumnado.xls"))

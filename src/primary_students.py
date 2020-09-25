import pandas as pd
import numpy as np
import re
from texts import columns_to_add, text2num, cursos_inf, cursos_prim
import smtplib, ssl
import os
from records import save_results

from dotenv import load_dotenv

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER")
PASSWORD = os.getenv("PASSWORD")
RECEIVER = os.getenv("RECEIVER")


def send_mail(data):
    sender_email = ADMIN_USER
    password = PASSWORD
    receiver_email = RECEIVER
    port = 465  # For SSL
    smtp_server = "smtp.googlemail.com"
    sender_email = sender_email  # Enter your address
    receiver_email = receiver_email  # Enter receiver address
    password = password

    message = f"""Subject: Your grade

La columna grupo tiene el siguiente formato """ + data.encode().decode(
        "utf-8"
    )
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.set_debuglevel(1)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def generate_df_alumnos_primaria(df):
    def split_alternate(cadena):
        """
        Extraer curso etapa y grupo
        """
        cadena = cadena.lower().strip().replace("º", "")
        curso = re.search("(\d)", cadena).group(0)
        etapa = re.search("(p|prim|primaria|i|inf|infantil)", cadena).group(0)
        grupo = re.search("(\()([a-h])(\))", cadena).group(2)
        return " ".join([curso, etapa, grupo])

    to_delete = list(df.columns)

    df["Nº Alumno GIR"] = df["Nº Alumno GIR"].astype(str)
    df["email"] = "alumnado@education.catedu.es"
    gir_username = (
        df["Nombre"].str.lower().str[0]
        + df["Apellidos"].str.split().str[0].str.lower().str[:3]
        + df["Nº Alumno GIR"].str[-4:]
    )

    df["username"] = gir_username
    df["username"] = np.where(
        df["username"].notnull(),
        df["username"],
        df["Nombre"].str.lower() + df["Nº Alumno GIR"].str[-4:],
    )

    df["username"] = (
        df["username"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    df["firstname"] = df["Nombre"].str.capitalize()
    df["lastname"] = df["Apellidos"].str.capitalize()
    df["password"] = "changeme"
    try:
        df["test"] = df["Grupo"]
        # send_mail(str(list(df["test"])))
        df["Grupo"] = df["Grupo"].apply(lambda x: split_alternate(x))
        df[["curso", "etapa", "grupo"]] = df["Grupo"].str.split(expand=True)
        # df.loc[df["curso"] == "Iº"] = "1º"
        df["curso"] = df["curso"].apply(lambda x: text2num[x])
        df.loc[df["etapa"] == "i", "courses_list"] = pd.Series([cursos_inf] * len(df))
        df.loc[df["etapa"] == "p", "courses_list"] = pd.Series([cursos_prim] * len(df))
        df["etapa"] = df["etapa"].apply(lambda x: "inf" if x == "i" else "prim")

        for item in range(1, 8):

            df["course" + str(item)] = (
                df["courses_list"].apply(
                    lambda x: x[item - 1] if isinstance(x, list) else np.nan
                )
                + "_"
                + df["curso"]
                + "_"
                + df["etapa"]
            )
            df["group" + str(item)] = df["grupo"].str.upper()
            df["role" + str(item)] = "student"

        save_results("Well done!")
        df = df.drop(columns=["curso", "etapa", "grupo", "courses_list", "test"])

    except:
        # send_mail(str(list(df["test"])))
        save_results("Fallo ##############################" + str(df.to_dict()))
        cols = ["curso", "etapa", "grupo", "courses_list", "test"]
        for c in cols:
            if c in list(df.columns):
                df = df.drop(
                    columns=[
                        c,
                    ]
                )
        global columns_to_add
        df1 = pd.DataFrame(columns=columns_to_add[:21])
        df = pd.concat([df, df1])

    df = df.drop(columns=to_delete)

    return df
import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64
import io
import uuid
from load_css import local_css

# local_css("style.css")


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


def filterColumns(column):
    to_preserve = [
        "IDALUMNO",
        "DOCUMENTO",
        "DNI",
        "N_GIR",
        "APELLIDO1",
        "APELLIDO2",
        "NOMBRE",
        "DNI_ALUMNO",
        "EMAIL",
        "EMAIL_PADRE",
        "EMAIL_MADRE",
        "ENSENANZA",
    ]

    if column in to_preserve:
        return False
    else:
        return True


columns_to_add = [
    "course1",
    "course2",
    "course3",
    "course4",
    "course5",
    "course6",
    "course7",
    "course8",
    "course9",
    "course10",
    "course11",
    "course12",
    "course13",
    "group1",
    "group2",
    "group3",
    "group4",
    "group5",
    "group6",
    "group7",
    "group8",
    "group9",
    "group10",
    "group11",
    "group12",
    "group13",
    "role1",
    "role2",
    "role3",
    "role4",
    "role5",
    "role6",
    "role7",
    "role8",
    "role9",
    "role10",
    "role11",
    "role12",
    "role13",
]


def generate_df(df):
    columns = filter(filterColumns, df.columns)
    df = df.drop(columns=columns)

    if "IDALUMNO" in list(df.columns):
        df["N_GIR"] = (df_csv["IDALUMNO"] * 1000).astype(int).astype(str)
    else:
        df["N_GIR"] = df["N_GIR"].astype(str)
    try:
        df["email"] = np.where(df["EMAIL"].notnull(), df["EMAIL"], df["EMAIL_PADRE"])
        df["email"] = np.where(df["EMAIL"].notnull(), df["EMAIL"], df["EMAIL_MADRE"])
    except:
        pass
    df["email"] = np.where(
        df["EMAIL"].notnull(),
        df["EMAIL"],
        "alumnado@education.catedu.es",
    )
    df["password"] = "changeme"

    gir_username = (
        df["NOMBRE"].str.lower().str[0]
        + df["APELLIDO1"].str.replace(" ", "").str.lower().str[:3]
        + df["APELLIDO2"].str.replace(" ", "").str.lower().str[:3]
        + df["N_GIR"].str[-4:]
    )

    # if "DOCUMENTO" in list(df.columns):
    #     df["username"] = np.where(
    #         df["DOCUMENTO"].notnull(),
    #         df["DOCUMENTO"].str.lower(),
    #         gir_username,
    #     )
    # elif "DNI_ALUMNO" in list(df.columns):
    #     df["username"] = np.where(
    #         df["DNI_ALUMNO"].notnull(),
    #         df["DNI_ALUMNO"].str.lower(),
    #         gir_username,
    #     )

    # df["username"] = np.where(
    #     df["username"].notnull(),
    #     df["username"],
    #     df["NOMBRE"].str.lower() + df["N_GIR"].str[-4:],
    # )

    df["username"] = gir_username

    df["username"] = np.where(
        df["username"].notnull(),
        df["username"],
        df["NOMBRE"].str.lower() + df["N_GIR"].str[-4:],
    )

    df["username"] = (
        df["username"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    df["firstname"] = df["NOMBRE"].str.capitalize()
    df["lastname"] = (
        df["APELLIDO1"].str.capitalize() + " " + df["APELLIDO2"].str.capitalize()
    )
    df = df.drop(columns=[column for column in df.columns if column.isupper()])
    df1 = df
    global columns_to_add
    df2 = pd.DataFrame(columns=columns_to_add)
    df1 = pd.concat([df1, df2])
    return df1


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# t = "<div><span class='highlight red'>Aplicación en fase de test</span></div>"
t = "# Aplicación en fase de test"

st.markdown(t, unsafe_allow_html=True)

st.sidebar.write(
    """## Web que genera CSVs listos para subir a Moodle.

### Instrucciones para centros de secundaria

Campos requeridos en el archivo .xls o .csv de entrada (respetando mayúsculas):
* N_GIR
* EMAIL
* NOMBRE
* APELLIDO1
* APELLIDO2
* DNI_ALUMNO o DNI en el caso de profesores

Campos opcionales:
* EMAIL_PADRE
* EMAIL_MADRE

### Instrucciones para centros de infantil y primaria

A final del día 10 de Septiembre de 2020."""
)

st.set_option("deprecation.showfileUploaderEncoding", False)

st.write(
    """
## Prepara tu csv para la carga de usuarios en tu centro aeducar

#### Este proceso, de momento, sólo es válido para centros de Secundaria

Esta aplicación sube los datos a un servidor propiedad del Gobierno de Aragón, para su tramiento y devolución al usuario.

Una vez devuelto el .csv, no se conserva ningún dato en el servidor.

*Más instrucciones desplegando el menú de la izquierda*
"""
)

file_bytes = st.file_uploader("Sube un archivo .csv o .xls", type=("csv", "xls"))

if file_bytes:
    try:
        bytes_data = file_bytes.read()
        s = str(bytes_data)
        data = io.StringIO(s)
        df_csv = pd.read_csv(data, delimiter=";")
        df = generate_df(df_csv)
        df = generate_df(df_csv)
    except:
        df_excel = pd.read_excel(file_bytes, sheet_name="datos")
        df = generate_df(df_excel)

    st.markdown(get_table_download_link(df), unsafe_allow_html=True)

    st.dataframe(df)

    #     df_csv = df_csv.drop(
    #         columns=[
    #             "IDTIPOENS",
    #             "COD_TIPO_ENSENANZA",
    #             "TIPO_ENSENANZA",
    #             "IDENSENANZA",
    #             "COD_ENSENANZA",
    #             "ENSENANZA",
    #             "IDMODALIDAD",
    #             "MODALIDAD",
    #             "CURSO",
    #             "IDGRUPO",
    #             "GRUPO",
    #         ]
    #     )

    #     df_csv["IDALUMNO"] = (df_csv["IDALUMNO"] * 1000).astype(int).astype(str)
    #     df_csv["email"] = np.where(
    #         df_csv["EMAIL"].notnull(), df_csv["EMAIL"], "alumnado@education.catedu.es"
    #     )
    #     df1 = pd.DataFrame()
    #     gir_username = (
    #         df_csv["NOMBRE"].str.lower().str[0]
    #         + df_csv["APELLIDO1"].str.lower().str[:3]
    #         + df_csv["APELLIDO2"].str.lower().str[:3]
    #         + df_csv["IDALUMNO"].str[-4:]
    #     )
    #     df1["username"] = np.where(
    #         df_csv["DOCUMENTO"].notnull(), df_csv["DOCUMENTO"].str.lower(), gir_username
    #     )
    #     df1["username"] = (
    #         df1["username"]
    #         .str.normalize("NFKD")
    #         .str.encode("ascii", errors="ignore")
    #         .str.decode("utf-8")
    #     )
    #     df1["password"] = "changeme"
    #     df1["firstname"] = df_csv["NOMBRE"].str.capitalize()
    #     df1["lastname"] = (
    #         df_csv["APELLIDO1"].str.capitalize()
    #         + " "
    #         + df_csv["APELLIDO2"].str.capitalize()
    #     )
    #     df1["email"] = df_csv["email"]
    #     df2 = pd.DataFrame(columns=columns_to_add)
    #     df1 = pd.concat([df1, df2])
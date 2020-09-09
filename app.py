import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64


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


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.set_option("deprecation.showfileUploaderEncoding", False)

st.write(
    """
# Prepara tu csv para la carga de usuarios en tu centro aeducar

Esta aplicación sube los datos a un servidor propiedad del Gobierno de Aragón, para su tramiento y devolución al usuario.

Una vez devuelto el .csv, no se conserva ningún dato en el servidor.
"""
)

file_bytes = st.file_uploader("Sube un archivo .csv o .xls", type=("csv", "xls"))


if file_bytes:
    try:
        df_csv = pd.read_csv(file_bytes, delimiter=";")

        df_csv = df_csv.drop(
            columns=[
                "IDTIPOENS",
                "COD_TIPO_ENSENANZA",
                "TIPO_ENSENANZA",
                "IDENSENANZA",
                "COD_ENSENANZA",
                "ENSENANZA",
                "IDMODALIDAD",
                "MODALIDAD",
                "CURSO",
                "IDGRUPO",
                "GRUPO",
            ]
        )

        df_csv["IDALUMNO"] = (df_csv["IDALUMNO"] * 1000).astype(int).astype(str)
        df_csv["email"] = np.where(
            df_csv["EMAIL"].notnull(), df_csv["EMAIL"], "alumnado@education.catedu.es"
        )
        df1 = pd.DataFrame()
        gir_username = (
            df_csv["NOMBRE"].str.lower().str[0]
            + df_csv["APELLIDO1"].str.lower().str[:3]
            + df_csv["APELLIDO2"].str.lower().str[:3]
            + df_csv["IDALUMNO"].str[-4:]
        )
        df1["username"] = np.where(
            df_csv["DOCUMENTO"].notnull(), df_csv["DOCUMENTO"].str.lower(), gir_username
        )
        df1["username"] = (
            df1["username"]
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )
        df1["firstname"] = df_csv["NOMBRE"].str.capitalize()
        df1["lastname"] = (
            df_csv["APELLIDO1"].str.capitalize()
            + " "
            + df_csv["APELLIDO2"].str.capitalize()
        )
        df1["email"] = df_csv["email"]
    except:
        df_excel = pd.read_excel("IES Miguel Serve (as).xls", "datos")

        columns = filter(filterColumns, df_excel.columns)
        df_excel = df_excel.drop(columns=columns)
        df_excel["N_GIR"] = df_excel["N_GIR"].astype(str)
        df_excel["email"] = np.where(
            df_excel["EMAIL"].notnull(), df_excel["EMAIL"], df_excel["EMAIL_PADRE"]
        )
        df_excel["email"] = np.where(
            df_excel["EMAIL"].notnull(), df_excel["EMAIL"], df_excel["EMAIL_MADRE"]
        )
        df_excel["email"] = np.where(
            df_excel["EMAIL"].notnull(),
            df_excel["EMAIL"],
            "alumnado@education.catedu.es",
        )

        gir_username = (
            df_excel["NOMBRE"].str.lower().str[0]
            + df_excel["APELLIDO1"].str.lower().str[:3]
            + df_excel["APELLIDO2"].str.lower().str[:3]
            + df_excel["N_GIR"].str[-4:]
        )

        df_excel["username"] = np.where(
            df_excel["DNI_ALUMNO"].notnull(),
            df_excel["DNI_ALUMNO"].str.lower(),
            gir_username,
        )
        df_excel["username"] = np.where(
            df_excel["username"].notnull(),
            df_excel["username"],
            df_excel["NOMBRE"].str.lower() + df_excel["N_GIR"].str[-4:],
        )

        df_excel["username"] = (
            df_excel["username"]
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )

        df_excel["firstname"] = df_excel["NOMBRE"].str.capitalize()
        df_excel["lastname"] = (
            df_excel["APELLIDO1"].str.capitalize()
            + " "
            + df_excel["APELLIDO2"].str.capitalize()
        )
        df_excel = df_excel.drop(
            columns=[column for column in df_excel.columns if column.isupper()]
        )
        df1 = df_excel

    st.markdown(get_table_download_link(df1), unsafe_allow_html=True)
    st.dataframe(df1)

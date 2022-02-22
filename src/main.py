import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64
import re
from texts import TEXTS, columns_to_add, text2num, cursos_inf, cursos_prim
import mail_errors


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


def filterColumnsAlumnosSec(column):
    to_preserve = [
        "N_GIR",
        "APELLIDO1",
        "APELLIDO2",
        "NOMBRE",
        "EMAIL",
        "EMAIL_PADRE",
        "EMAIL_MADRE",
    ]

    if column in to_preserve:
        return False
    else:
        return True


def generate_df_alumnos_secundaria(df, cohort):
    columns = filter(filterColumnsAlumnosSec, df.columns)

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
        + df["N_GIR"].str[-4:]
    )

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

    df["firstname"] = df["NOMBRE"].str.title()
    df["lastname"] = (
        df["APELLIDO1"].fillna("").str.title()
        + " "
        + df["APELLIDO2"].fillna("").str.title()
    )

    if cohort:
        df["cohort1"] = df["GRUPO"]
    else:
        df1 = pd.DataFrame(columns=columns_to_add)
        df = pd.concat([df, df1])

    df = df.drop(columns=columns)
    df = df.drop(columns=[column for column in df.columns if column.isupper()])

    return df


def generate_df_profesores_secundaria(df, cohort):
    df1 = pd.DataFrame()
    df1["username"] = df["Nº documento"].str.lower()
    df1["firstname"] = df["Nombre"].str.title()
    df1["lastname"] = df["Apellido 1"].str.title() + " " + df["Apellido 2"].str.title()
    df1["email"] = "alumnado@education.catedu.es"
    df1["password"] = "changeme"

    if cohort:
        df1["cohort1"] = "Claustro"
        df1["cohort2"] = ""
    else:
        df2 = pd.DataFrame(columns=columns_to_add)
        df1 = pd.concat([df1, df2])
    return df1


def send_error_file(uploadedfile):
    with open(uploadedfile.name, "wb") as f:
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
            mail_errors.body = f"Ponerte en contacto con {mail}"
            try:
                mail_errors.send_mail(uploadedfile.name)
                os.remove(uploadedfile.name)
            except:
                mail_errors.send_mail()
            return st.success(
                "Gracias por enviarnos tu contacto. En breve nos pondremos en contacto contigo. Si no lo hacemos, escríbenos a soportecatedu@educa.aragon.es"
            )


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
img {width: 100%;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# t = "<div><span class='highlight red'>Aplicación en fase de test</span></div>"
t = "# Prepara tu csv para la carga de usuarios en el moodle aeducar de tu centro"

st.markdown(t, unsafe_allow_html=True)

##### SIDEBAR

option = st.sidebar.selectbox(
    "¿Qué datos quieres subir?",
    [
        "Inicio",
        "Alumnado",
        "Profesorado",
        "Centros de Educación de Adultos",
    ],
)

st.set_option("deprecation.showfileUploaderEncoding", False)

if option == "Inicio":
    st.write(TEXTS["intro"])
    st.video("http://youtu.be/3jlNUmzcHLo?hd=1")
elif option == "Alumnado":
    st.sidebar.write(TEXTS["alumnos_secundaria"])
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls"))
    cohort = st.checkbox("Organizar por cohortes")

    if file_bytes:
        try:
            df_excel = pd.read_excel(file_bytes)
            if cohort:
                df = generate_df_alumnos_secundaria(df_excel, cohort)
            else:
                df = generate_df_alumnos_secundaria(df_excel, cohort)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)
            st.dataframe(df)
        except:
            try:
                send_error_file(file_bytes)
            except:
                st.error(
                    "Ha habido un problema enviando el correo de error. Por favor, envía tu archivo a asesor@catedu.es"
                )


elif option == "Profesorado":
    st.sidebar.write(TEXTS["profesores_secundaria"])
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls"))
    cohort = st.checkbox("Organizar por cohortes")

    if file_bytes:
        try:
            df_excel = pd.read_excel(file_bytes)
            if cohort:
                df = generate_df_profesores_secundaria(df_excel, cohort)
            else:
                df = generate_df_profesores_secundaria(df_excel, cohort)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)
            st.dataframe(df)
        except:
            try:
                send_error_file(file_bytes)
            except:
                st.error(
                    "Ha habido un problema enviando el correo de error. Por favor, envía tu archivo a asesor@catedu.es"
                )

elif option == "Centros de Educación de Adultos":
    st.markdown(
        """<embed src="https://drive.google.com/viewerng/
viewer?embedded=true&url=https://github.com/catedu/csv-aeducar/raw/master/src/assets/tuto-subida-masiva-usuarios-EPA.pdf" width="100%" height="980px">""",
        unsafe_allow_html=True,
    )

else:
    st.sidebar.write(TEXTS["en_progreso"])
    st.write(TEXTS["en_progreso"])

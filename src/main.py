import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64

from texts import TEXTS, columns_to_add
import mailing
import primary_students as prim
from maestros import write_maestros_page
from highschool_students import (
    generate_df_alumnos_secundaria,
    generate_df_alumnos_secundaria_nuevo_sigad,
)


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
            mailing.body = f"Ponerte en contacto con {mail}"
            try:
                mailing.send_error_mail(file_path)
                os.remove(file_path)
            except:
                mailing.send_error_mail(file_path)
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

st.set_page_config(
    page_title="csv para Aeducar",
    page_icon="favico.ico",
)
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
        "Alumnado desde GIR",
        "Profesorado desde GIR",
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
            try:
                df_excel = pd.read_excel(file_bytes, sheet_name="datos")
            except:
                df_excel = pd.read_excel(file_bytes, sheet_name=None)
                df_excel = df_excel[list(df_excel.keys())[0]]

            if cohort:
                try:
                    df = generate_df_alumnos_secundaria(df_excel, cohort)
                except:
                    df = generate_df_alumnos_secundaria_nuevo_sigad(df_excel, cohort)
            else:
                try:
                    df = generate_df_alumnos_secundaria(df_excel, cohort)
                except:
                    df = generate_df_alumnos_secundaria_nuevo_sigad(df_excel, cohort)
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
            # mailing.notify_conversion_success(file_bytes.name)
            mailing.send_success_mail(file_bytes.name)
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

elif option == "Alumnado desde GIR":
    st.sidebar.write(TEXTS["alumnos_primaria"])
    try:
        df_test = pd.read_csv("test_ceip.csv")
    except:
        df_test = pd.read_csv(
            "https://raw.githubusercontent.com/catedu/csv-aeducar/master/src/test_ceip.csv"
        )
    df_test["username"][0] = "jlop1234"
    df_test["username"][1] = "llop5678"
    df_test["firstname"][0] = "Javier"
    df_test["firstname"][1] = "Lucía"
    file_bytes = st.file_uploader("Sube un archivo", type=("xls", "csv"))
    cohort = st.checkbox("Organizar por cohortes")

    if not file_bytes:
        st.write(
            "Para sacar los datos necesarios, en GIR Académico, sigue los pasos de la imagen:"
        )
        st.image(
            "https://github.com/catedu/csv-aeducar/raw/master/src/assets/exportar_alumnos_gir.png",
        )
        st.write(
            "### Demo de tabla resultante al subir el .xls obtenido del GIR a esta aplicación"
        )
        if cohort:
            df_test = df_test.drop(columns=list(df_test.columns[5:]))
            df_test["cohort1"] = ""
            df_test["cohort1"][0] = "2pa"
            df_test["cohort1"][1] = "3id"
            st.dataframe(df_test)
        else:
            st.dataframe(df_test)

    else:
        try:
            try:
                df_excel = pd.read_excel(file_bytes, sheet_name=None)
                df_excel = df_excel[list(df_excel.keys())[0]]
            except:
                df_excel = pd.read_excel(file_bytes, sheet_name="datos")
            if cohort:
                df = prim.generate_df_alumnos_primaria(df_excel, cohort)
            else:
                df = prim.generate_df_alumnos_primaria(df_excel, cohort)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)
            st.dataframe(df)
            os.system(f"echo {file_bytes.name} > success.txt")
        except:
            try:
                bytes_data = file_bytes.read().decode("iso-8859-1")
                # st.write(bytes_data)
                s = str(bytes_data)
                # st.write(s)
                # s = s.replace("\t", ",")
                data = io.StringIO(s)
                df_csv = pd.read_csv(data, sep="\t")
                if cohort:
                    df = prim.generate_df_alumnos_primaria(df_csv, cohort)
                else:
                    df = prim.generate_df_alumnos_primaria(df_csv, cohort)
                st.markdown(get_table_download_link(df), unsafe_allow_html=True)
                st.dataframe(df)
                os.system(f"echo {file_bytes.name} > success.txt")
            except:
                try:
                    send_error_file(file_bytes)
                    os.system(f"echo {file_bytes.name} > errors.txt")
                except:
                    st.error(
                        "Ha habido un problema enviando el correo de error. Por favor, envía tu archivo a asesor@catedu.es"
                    )
                    os.system(f"echo {file_bytes.name} > errors.txt")

elif option == "Profesorado desde GIR":
    write_maestros_page()

else:
    st.sidebar.write(TEXTS["en_progreso"])
    st.write(TEXTS["en_progreso"])

import os
import io

import streamlit as st
import pandas as pd
import numpy as np

from texts import TEXTS, columns_to_add
import utils
import primary_students as prim
from maestros import write_maestros_page
import secundaria.estudiantes as se
import secundaria.profesorado as sp

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
    st.sidebar.write(TEXTS["alumnado"])
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
                    df = se.generate_df(df_excel, cohort)
                except:
                    df = se.generate_df_nuevo_sigad(df_excel, cohort)
            else:
                try:
                    df = se.generate_df(df_excel, cohort)
                except:
                    df = se.generate_df_nuevo_sigad(df_excel, cohort)
            st.markdown(utils.get_table_download_link(df), unsafe_allow_html=True)
            st.dataframe(df)
        except:
            try:
                utils.send_error_file(file_bytes)
            except:
                st.error(
                    "Ha habido un problema enviando el correo de error. Por favor, envía tu archivo a asesor@catedu.es"
                )


elif option == "Profesorado":
    st.sidebar.write(TEXTS["profesorado"])
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls"))
    cohort = st.checkbox("Organizar por cohortes")

    if file_bytes:
        try:
            df_excel = pd.read_excel(file_bytes)
            if cohort:
                df = sp.generate_df(df_excel, cohort)
            else:
                df = sp.generate_df(df_excel, cohort)
            st.markdown(utils.get_table_download_link(df), unsafe_allow_html=True)
            st.dataframe(df)
            # utils.notify_conversion_success(file_bytes.name)
            utils.send_success_mail(file_bytes.name)
        except:
            try:
                utils.send_error_file(file_bytes)
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
    st.sidebar.write(TEXTS["alumnado_GIR"])
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
            st.markdown(utils.get_table_download_link(df), unsafe_allow_html=True)
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
                st.markdown(utils.get_table_download_link(df), unsafe_allow_html=True)
                st.dataframe(df)
                os.system(f"echo {file_bytes.name} > success.txt")
            except:
                try:
                    utils.send_error_file(file_bytes)
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

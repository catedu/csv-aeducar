import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64
from load_css import local_css
import re
from texts import TEXTS

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


columns_to_add = [
    "course1",
    "group1",
    "role1",
    "course2",
    "group2",
    "role2",
    "course3",
    "group3",
    "role3",
    "course4",
    "group4",
    "role4",
    "course5",
    "group5",
    "role5",
    "course6",
    "group6",
    "role6",
    "course7",
    "group7",
    "role7",
    "course8",
    "group8",
    "role8",
    "course9",
    "group9",
    "role9",
    "course10",
    "group10",
    "role10",
    "course11",
    "group11",
    "role11",
    "course12",
    "group12",
    "role12",
    "course13",
    "group13",
    "role13",
]

text2num = {
    "1º": "primero",
    "2º": "segundo",
    "3º": "tercero",
    "4º": "cuarto",
    "5º": "quinto",
    "6º": "sexto",
}

cursos_inf = [
    "proyecto6",
    "proyecto4",
    "proyecto3",
    "proyecto2",
    "proyecto1",
    "english",
    "proyecto5",
]

cursos_prim = [
    "lengua",
    "sociales",
    "matematicas",
    "ingles",
    "edfisica",
    "artistica",
    "ciencias",
]


def generate_df_alumnos_primaria(df):
    def split_alternate(cadena):
        """
        Convertir cosas como I3B (B) o P1ºA (A)
        a 3º INF (B)
        a 1º PRIM (A)
        """
        cadena = cadena.strip()
        curso = cadena[1] + "º"
        etapa = "PRIM" if cadena[0] == "P" else "INF"
        grupo = cadena[-3:]
        return " ".join([curso, etapa, grupo])

    to_delete = list(df.columns)

    global text2num
    global cursos_inf
    global cursos_prim

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
        try:
            df[["curso", "etapa", "grupo"]] = df["Grupo"].str.split(expand=True)
        except:
            df["Grupo"] = df["Grupo"].apply(lambda x: split_alternate(x))
            df[["curso", "etapa", "grupo"]] = df["Grupo"].str.split(expand=True)
            df.loc[df["curso"] == "Iº"] = "1º"
        df["curso"] = df["curso"].apply(lambda x: text2num[x])
        df["etapa"] = df["etapa"].str.lower()
        df["grupo"] = df["grupo"].str[1]
        df.loc[df["etapa"] == "inf", "courses_list"] = pd.Series([cursos_inf] * len(df))
        df.loc[df["etapa"] == "prim", "courses_list"] = pd.Series(
            [cursos_prim] * len(df)
        )

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
            df["group" + str(item)] = df["grupo"]
            df["role" + str(item)] = "student"

        df = df.drop(columns=["curso", "etapa", "grupo", "courses_list"])

    except:
        cols = ["curso", "etapa", "grupo", "courses_list"]
        for c in cols:
            if c in list(df.columns):
                print(c)
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


def generate_df_maestros(df):
    def split(word):
        return [char for char in word]

    global text2num
    global cursos_inf
    global cursos_prim

    df1 = pd.DataFrame()
    df1["username"] = df["Nº Documento"].str.lower()
    df1["firstname"] = df["Nombre"]
    df1["lastname"] = df["Apellidos"]
    df1["email"] = "alumnado@education.catedu.es"
    df1["password"] = "changeme"
    try:
        df1["grupo"] = df["grupo"].apply(
            lambda x: split(x)
            if isinstance(x, str) and bool(re.match("\d(i|p)\w", x))
            else np.nan
        )
        df1[["curso", "etapa", "grupo"]] = df1["grupo"].apply(pd.Series)
        df1["course"] = df1["curso"].apply(
            lambda x: text2num[x + "º"]
            if isinstance(x, str) and bool(re.match("\d", x))
            else np.nan
        )
        df1["group"] = df1["grupo"].apply(
            lambda x: x.upper()
            if isinstance(x, str) and bool(re.match("\w", x))
            else np.nan
        )

        df1.loc[df1["etapa"] == "i", "etapa"] = "inf"
        df1.loc[df1["etapa"] == "p", "etapa"] = "prim"
        df1.loc[df1["etapa"] == "inf", "courses_list"] = pd.Series(
            [cursos_inf] * len(df1)
        )
        df1.loc[df1["etapa"] == "prim", "courses_list"] = pd.Series(
            [cursos_prim] * len(df1)
        )

        for item in range(1, 8):
            df1["course" + str(item)] = df1["courses_list"].apply(
                lambda x: x[item - 1] if isinstance(x, list) else np.nan
            )
            df1.loc[df1["course" + str(item)].notnull(), "course" + str(item)] = (
                df1["course" + str(item)] + "_" + df1["course"] + "_" + df1["etapa"]
            )
            df1["group" + str(item)] = df1["group"]
            df1.loc[
                df1["group"].astype(str).str.isupper(), "role" + str(item)
            ] = "editingteacher"

        df1 = df1.drop(columns=["courses_list", "curso", "etapa", "course", "group"])

    except:
        global columns_to_add
        df2 = pd.DataFrame(columns=columns_to_add)
        df1 = pd.concat([df1, df2])

    return df1


def generate_df_alumnos_secundaria(df):
    columns = filter(filterColumnsAlumnosSec, df.columns)
    df = df.drop(columns=columns)

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

    df["firstname"] = df["NOMBRE"].str.capitalize()
    df["lastname"] = (
        df["APELLIDO1"].fillna("").str.capitalize()
        + " "
        + df["APELLIDO2"].fillna("").str.capitalize()
    )
    df = df.drop(columns=[column for column in df.columns if column.isupper()])
    df1 = df
    global columns_to_add
    df2 = pd.DataFrame(columns=columns_to_add)
    df1 = pd.concat([df1, df2])
    return df1


def generate_df_profesores_secundaria(df):
    df1 = pd.DataFrame()
    df1["username"] = df["Nº documento"].str.lower()
    df1["firstname"] = df["Nombre"].str.capitalize()
    df1["lastname"] = (
        df["Apellido 1"].str.capitalize() + " " + df["Apellido 2"].str.capitalize()
    )
    df1["email"] = "alumnado@education.catedu.es"
    df1["password"] = "changeme"
    global columns_to_add
    df2 = pd.DataFrame(columns=columns_to_add)
    df1 = pd.concat([df1, df2])
    return df1


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
    "¿Qué datos quieres subir",
    [
        "",
        "Alumnado de Infantil y Primaria",
        "Alumnado de Secundaria",
        "Profesorado de Infantil y Primaria",
        "Profesorado de Secundaria",
    ],
)

st.set_option("deprecation.showfileUploaderEncoding", False)

if option == "":
    st.write(TEXTS["intro"])
elif option == "Alumnado de Secundaria":
    st.sidebar.write(TEXTS["alumnos_secundaria"])
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls"))

    if file_bytes:
        df_excel = pd.read_excel(file_bytes, sheet_name="datos")
        df = generate_df_alumnos_secundaria(df_excel)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
        st.dataframe(df)
elif option == "Profesorado de Secundaria":
    st.sidebar.write(TEXTS["profesores_secundaria"])
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls"))

    if file_bytes:
        df_excel = pd.read_excel(file_bytes)
        df = generate_df_profesores_secundaria(df_excel)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
        st.dataframe(df)
elif option == "Alumnado de Infantil y Primaria":
    st.sidebar.write(TEXTS["alumnos_primaria"])
    st.write(
        "#### Solo se rellenarán los datos del curso, grupo y rol si la columna grupo tiene el siguiente formato `I3B (B)`, `P4A (A)` o `3º INF (B)`,`4º PRIM (A)`"
    )
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
    file_bytes = st.file_uploader(
        "Sube un archivo .xls",
        type=("xls", "csv"),
        encoding="ISO-8859-1",
    )
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
        st.dataframe(df_test)

    else:
        bytes_data = file_bytes.read()
        s = str(bytes_data)
        s = s.replace("\t", ",")
        data = io.StringIO(s)
        df_csv = pd.read_csv(data)
        df = generate_df_alumnos_primaria(df_csv)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
        st.dataframe(df)


elif option == "Profesorado de Infantil y Primaria":
    st.sidebar.write(TEXTS["maestros"])
    maestros = {
        "Nombre": {0: "José María", 1: "María", 2: "Berta"},
        "Apellidos": {0: "Gasca López", 1: "Arenedo Marín", 2: "Gutiérrez Sánchez"},
        "Sexo": {0: "Hombre", 1: "Mujer", 2: "Mujer"},
        "Documento": {0: "DNI", 1: "DNI", 2: "DNI"},
        "Nº Documento": {0: "12345678V", 1: "87654321V", 2: "13246587V"},
        "Localidad": {0: "Zaragoza", 1: "Zaragoza", 2: "Zaragoza"},
        "Provincia": {0: "Zaragoza", 1: "Zaragoza", 2: "Zaragoza"},
        "Nº Registro": {0: 20000044356345, 1: 200007044356346, 2: 200004704435634},
        "Especialidad": {0: np.nan, 1: np.nan, 2: np.nan},
        "Destinos Activos": {0: 2, 1: 2, 2: 2},
        "grupo": {0: "1ia", 1: "2pb", 2: ""},
    }
    df_uploaded = pd.DataFrame(maestros)
    df_test = generate_df_maestros(df_uploaded)
    file_bytes = st.file_uploader(
        "Sube un archivo .xls",
        type=("xls", "csv"),
        encoding="ISO-8859-1",
    )
    if not file_bytes:
        st.write(
            """### Instrucciones

Para sacar los datos necesarios, en GIR Académico, sigue los pasos de la imagen:"""
        )
        st.image(
            "https://github.com/catedu/csv-aeducar/raw/master/src/assets/exportar_maestros_gir.png",
        )
        st.write("### Demo de archivo tabla extraída de GIR")
        st.dataframe(df_uploaded)
        st.write(
            "### Demo de tabla resultante al subir el .xls obtenido del GIR a esta aplicación"
        )
        st.dataframe(df_test)

    else:
        bytes_data = file_bytes.read()
        s = str(bytes_data)
        s = s.replace("\t", ",")
        data = io.StringIO(s)
        df_csv = pd.read_csv(data)
        df = generate_df_maestros(df_csv)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
        st.dataframe(df)

else:
    st.sidebar.write(TEXTS["en_progreso"])
    st.write(TEXTS["en_progreso"])
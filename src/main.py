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

TEXTS = {
    "intro": """
Esta aplicación sube los datos a un servidor propiedad del Gobierno de Aragón, para su tramiento y devolución al usuario.

Una vez devuelto el .csv, no se conserva ningún dato en el servidor.

*Más instrucciones desplegando el menú de la izquierda*
""",
    "alumnos_secundaria": """## Descarga tu .xls del SIGAD

En Utilidades -> Informes -> ALUM -> descarga Listado completo de alumnos con todos sus datos.

Campos mínimos requeridos en el archivo .xls:
* N_GIR
* EMAIL (aunque haya registros vacíos)
* NOMBRE
* APELLIDO1
* APELLIDO2

Campos opcionales:
* EMAIL_PADRE
* EMAIL_MADRE

Puedes probar el funcionamiento descargando [este archivo para tests](https://github.com/catedu/csv-aeducar/raw/master/src/prueba-alumnado.xls).
""",
    "profesores_secundaria": """## Descarga tu .xls del SIGAD

### Sería necesario añadir el campo mail. Si alguien sabe cómo sacar estos datos del SIGAD incluyendo el mail del profesorado, que envíe un correro a asesor@catedu.es para que actualice el funcionamiento de esta aplicación, indicándome cómo ha obtenido estos datos y un .xls de prueba aunque sea con sólo un registro y datos falsos. De momento todos los registros tendrán el mismo mail. El profesorado podrá acceder a su perfil y modificarlo ya en su moodle.

En Personal -> Búsqueda -> Exportar -> descarga Listado completo de profesores con todos sus datos.

Campos mínimos requeridos en el archivo .xls:
* Nombre
* Apellido 1
* Apellido 2
* Nº documento

Puedes probar el funcionamiento descargando [este archivo para tests](https://github.com/catedu/csv-aeducar/raw/master/src/prueba-profesorado.xls).
""",
    "en_progreso": """## Servicio no disponbile.

Este servicio estará disponible durante la semana del 14 al 18 de Septiembre

    """,
}


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
        df["APELLIDO1"].str.capitalize() + " " + df["APELLIDO2"].str.capitalize()
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
    df["password"] = "changeme"
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
else:
    st.sidebar.write(TEXTS["en_progreso"])
    st.write(TEXTS["en_progreso"])
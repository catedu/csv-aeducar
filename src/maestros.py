import streamlit as st
from texts import TEXTS, columns_to_add, text2num, cursos_inf, cursos_prim
import pandas as pd
import numpy as np
import re
import io
import base64
import os
import mailing


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


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="subida_usuarios.csv">Descarga aquí tu archivo csv</a>'


def generate_df_maestros(df, cohort):
    def split(word):
        return list(word)

    df1 = pd.DataFrame()
    df1["username"] = df["Nº Documento"].str.lower()
    df1["firstname"] = df["Nombre"]
    df1["lastname"] = df["Apellidos"]
    df1["email"] = "alumnado@education.catedu.es"
    df1["password"] = "changeme"
    if cohort:
        df1["cohort1"] = "Claustro"
        try:
            df1["cohort2"] = df["grupo"]
        except:
            pass
    else:
        try:
            df1["grupo"] = df["grupo"].apply(
                lambda x: split(x)
                if isinstance(x, str) and bool(re.match("\d(i|p)\w", x))
                else np.nan
            )
            df1[["curso", "etapa", "grupo"]] = df1["grupo"].apply(pd.Series)
            df1["course"] = df1["curso"].apply(
                lambda x: text2num[x]
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

            df1 = df1.drop(
                columns=["courses_list", "curso", "etapa", "course", "group"]
            )

        except:
            df2 = pd.DataFrame(columns=columns_to_add)
            df1 = pd.concat([df1, df2])

    return df1


def write_maestros_page():
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
    file_bytes = st.file_uploader("Sube un archivo .xls", type=("xls", "csv"))
    cohort = st.checkbox("Organizar por cohortes")
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
        df_test = generate_df_maestros(df_uploaded, cohort)
        st.dataframe(df_test)
    else:
        try:
            bytes_data = file_bytes.read().decode("iso-8859-1")
            s = str(bytes_data)
            s = s.replace("\t", ",")
            data = io.StringIO(s)
            df_csv = pd.read_csv(data)
            df = generate_df_maestros(df_csv, cohort)
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

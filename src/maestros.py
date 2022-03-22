import pandas as pd
import numpy as np
import re
from texts import columns_to_add, text2num, cursos_inf, cursos_prim


def generate_df_maestros(df, cohort):
    def split(word):
        return [char for char in word]

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

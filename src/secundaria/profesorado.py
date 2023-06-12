import pandas as pd
from texts import columns_to_add


def generate_df(df, cohort):
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

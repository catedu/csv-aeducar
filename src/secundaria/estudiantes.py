import numpy as np
import pandas as pd
from texts import TEXTS, columns_to_add


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


def generate_df(df, cohort):
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


def generate_df_nuevo_sigad(df, cohort):
    columns_to_delete = df.columns.to_list()

    df["ID Alumno Centro"] = df["ID Alumno Centro"].astype(str)

    df["email"] = "alumnado@education.catedu.es"

    df["password"] = "changeme"

    base_username = (
        df["Nombre"].str.lower().str[0]
        + df["Apellido1"].str.replace(" ", "").str.lower().str[:3]
    )

    df["username"] = base_username

    df["username"] = np.where(
        df["Nº documento"].notnull(),
        df["username"] + df["Nº documento"].str[-4:],
        df["Nombre"].str.lower() + df["ID Alumno Centro"].str[-4:],
    )

    df["username"] = (
        df["username"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    df["firstname"] = df["Nombre"].str.title()
    df["lastname"] = (
        df["Apellido1"].fillna("").str.title()
        + " "
        + df["Apellido2"].fillna("").str.title()
    )

    if cohort:
        df["cohort1"] = df["Enseñanza"].str[:4].str.strip(" ") + df["Grupo Estudio"]
    else:
        df1 = pd.DataFrame(columns=columns_to_add)
        df = pd.concat([df, df1])

    # print(df.columns)
    # print(columns_to_delete)

    df = df.drop(columns=columns_to_delete)

    return df

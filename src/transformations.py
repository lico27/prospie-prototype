import pandas as pd

def transform_classification_table(df, classification_type, id_col, name_col):

    """
    Splits combined classifications into separate tables and tidies them.
    """

    return (df[df["classification_type"] == classification_type]
        .drop_duplicates(subset=["classification_desc"], keep="first")
        .drop(columns=["registered_num", "classification_type"])
        .rename(columns={"classification_code": id_col, "classification_desc": name_col})
    )

def transform_join_tables(df, classification_type, id_col):

    """
    Builds join tables to manage many-to-many relationships between funders and their classifications.
    """

    return df[df["classification_type"] == classification_type
        ].drop(columns=["classification_type", "classification_desc"]
        ).rename(columns={"classification_code": id_col})
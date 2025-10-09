import pandas as pd

def build_classifications_tables(df):
    #explode classifications and normalise into columns
    exploded_df_classifications = df.explode("classifications")
    classifications_df = pd.json_normalize(exploded_df_classifications["classifications"])

    #reset indexes and combine
    exploded_df_classifications = exploded_df_classifications.reset_index(drop=True)
    classifications_df = classifications_df.reset_index(drop=True)
    classifications_final = pd.concat([exploded_df_classifications, classifications_df], axis=1)

    #drop unnecessary columns and rows
    classifications_final = classifications_final.drop(columns=["name", "website", "activities", "objectives", "income", "expenditure", "classifications", "country_continent", "local_authority", "region"])
    classifications_final = classifications_final[classifications_final["classification_type"] != "How"]

    #build classification tables
    beneficiaries = classifications_final[
        classifications_final["classification_type"] == "Who"
    ].drop_duplicates(subset=['classification_desc'], keep='first'
    ).drop(columns=["registered_num", "classification_type"])

    causes = classifications_final[
        classifications_final["classification_type"] == "What"
    ].drop_duplicates(subset=['classification_desc'], keep='first'
    ).drop(columns=["registered_num", "classification_type"])

    #build join tables
    funder_causes = classifications_final[
        classifications_final["classification_type"] == "What"
    ].drop(columns=["classification_type", "classification_desc"])

    funder_beneficiaries = classifications_final[
        classifications_final["classification_type"] == "Who"
    ].drop(columns=["classification_type", "classification_desc"])

    return beneficiaries, funder_beneficiaries, causes, funder_causes

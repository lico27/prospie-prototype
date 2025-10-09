import pandas as pd

def build_classifications_tables(df):
    # Explode classifications and normalise into columns
    exploded_df_classifications = df.explode("classifications")
    classifications_df = pd.json_normalize(exploded_df_classifications["classifications"])
    
    # Ensure expected columns exist
    expected_columns = ['classification_type', 'classification_desc', 'classification_code']
    for col in expected_columns:
        if col not in classifications_df.columns:
            classifications_df[col] = None
    
    # Reset indexes and combine
    exploded_df_classifications = exploded_df_classifications.reset_index(drop=True)
    classifications_df = classifications_df.reset_index(drop=True)
    classifications_final = pd.concat([exploded_df_classifications, classifications_df], axis=1)
    
    # Drop unnecessary columns and rows
    classifications_final = classifications_final.drop(columns=["name", "website", "activities", "objectives", "income", "expenditure", "classifications", "country_continent", "local_authority", "region"])
    classifications_final = classifications_final[classifications_final["classification_type"] != "How"]
    
    # Build classification tables
    beneficiaries = classifications_final[
        classifications_final["classification_type"] == "Who"
    ].drop_duplicates(subset=['classification_desc'], keep='first'
    ).drop(columns=["registered_num", "classification_type"]
    ).rename(columns={"classification_code": "ben_id", "classification_desc": "ben_name"})
    
    causes = classifications_final[
        classifications_final["classification_type"] == "What"
    ].drop_duplicates(subset=['classification_desc'], keep='first'
    ).drop(columns=["registered_num", "classification_type"]
    ).rename(columns={"classification_code": "cause_id", "classification_desc": "cause_name"})
    
    # Build join tables
    funder_causes = classifications_final[
        classifications_final["classification_type"] == "What"
    ].drop(columns=["classification_type", "classification_desc"]
    ).rename(columns={"classification_code": "cause_id"})
    
    funder_beneficiaries = classifications_final[
        classifications_final["classification_type"] == "Who"
    ].drop(columns=["classification_type", "classification_desc"]
    ).rename(columns={"classification_code": "ben_id"})
    
    return beneficiaries, funder_beneficiaries, causes, funder_causes
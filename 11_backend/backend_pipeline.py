from dataframe_builder import *
from dotenv import load_dotenv
import os

#get keys from env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

def get_backend_data(user_data, funder_number, model):
    """
    Takes the user's input, creates embeddings where relevant, and combines with funder/grants data to create the dataframes for the score calculator.
    """

    #generate embeddings
    user_name_em, user_concat_em = create_user_embeddings(user_data, model)

    #get funder data
    funder_data, funder_areas, funder_beneficiaries, funder_causes = get_funder_data(funder_number, url, key)

    #get grants data
    grants_df = build_grants_df(funder_number, url, key)

    #enrich grants data
    grants_df = enrich_grants_df(grants_df, funder_number, url, key)

    #get lookup tables
    areas_df, hierarchies_df = get_lookup_tables(url, key)

    #build pair dataframe
    pair_df = build_pair_df(user_data, funder_data, funder_areas, funder_beneficiaries, funder_causes, user_name_em, user_concat_em)

    return grants_df, areas_df, hierarchies_df, pair_df
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
import os
import sys
from scoring_logic import calculate_alignment_score

#add project root to path
sys.path.insert(0, os.path.dirname(__file__))
from backend_utils import get_table_from_supabase

#get keys from env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

#TEMPORARY
test_user_data = {
    "user_id": "1234567",
    "user_name": "Test Charity",
    "user_areas": ["London", "Manchester"],
    "user_beneficiaries": ["Children/young People"],
    "user_causes": ["Education/training"],
    "user_extracted_class": json.dumps(["education", "youth development"]),
    "user_activities": "We provide educational support to young people",
    "user_objectives": "To improve educational outcomes for disadvantaged youth"
}
test_funder_number = "1202663"
model = SentenceTransformer("all-roberta-large-v1")

def create_user_embeddings(user_data, model):
    """
    Generates embeddings for user's charity name and text sections (activities and objectives).
    """

    #replace nas with empty string
    user_name = user_data.get("user_name", "") or ""
    user_activities = user_data.get("user_activities", "") or ""
    user_objectives = user_data.get("user_objectives", "") or ""

    #get embedding for name
    user_name_em = model.encode(user_name)

    #concatenate text sections and embed
    concat_text = f"{user_activities} {user_objectives}"
    concat_text = concat_text.lower()
    user_concat_em = model.encode(concat_text)

    return user_name_em, user_concat_em

# user_name_em, user_concat_em = create_user_embeddings(test_user_data, model)

def get_funder_data(funder_number, url, key):
    """
    Fetches data for the selected funder from supabase and builds dataframes via join tables.
    """
    supabase = create_client(url, key)

    #fetch funder data from supabase
    funder_response = supabase.table("funders").select("*").eq("registered_num", funder_number).execute()
    funder_data = funder_response.data[0]

    if not funder_data:
        return {"error": True}

    #get classifications
    funder_area_joins = supabase.table("funder_areas").select("area_id").eq("registered_num", funder_number).execute()
    funder_area_ids = [join["area_id"] for join in funder_area_joins.data] if funder_area_joins.data else []

    funder_ben_joins = supabase.table("funder_beneficiaries").select("ben_id").eq("registered_num", funder_number).execute()
    funder_ben_ids = [join["ben_id"] for join in funder_ben_joins.data] if funder_ben_joins.data else []

    funder_cause_joins = supabase.table("funder_causes").select("cause_id").eq("registered_num", funder_number).execute()
    funder_cause_ids = [join["cause_id"] for join in funder_cause_joins.data] if funder_cause_joins.data else []

    #get names from ids
    funder_areas = []
    if funder_area_ids:
        fetched_resp = supabase.table("areas").select("area_name").in_("area_id", funder_area_ids).execute()
        funder_areas = [area["area_name"] for area in fetched_resp.data]

    funder_beneficiaries = []
    if funder_ben_ids:
        fetched_resp = supabase.table("beneficiaries").select("ben_name").in_("ben_id", funder_ben_ids).execute()
        funder_beneficiaries = [ben["ben_name"] for ben in fetched_resp.data]

    funder_causes = []
    if funder_cause_ids:
        fetched_resp = supabase.table("causes").select("cause_name").in_("cause_id", funder_cause_ids).execute()
        funder_causes = [cause["cause_name"] for cause in fetched_resp.data]

    return funder_data, funder_areas, funder_beneficiaries, funder_causes

# funder_data, funder_areas, funder_beneficiaries, funder_causes = get_funder_data(test_funder_number, url, key)



def build_grants_df(funder_number, url, key):
    """
    Fetches grants data for the selected funder and builds a dataframe.
    """

    supabase = create_client(url, key)

    try:
        #get all grants for this funder
        all_grant_ids = []
        offset = 0
        batch_size = 1000

        while True:
            funder_grant_joins = supabase.table("funder_grants").select("grant_id").eq("registered_num", funder_number).range(offset, offset + batch_size - 1).execute()

            if not funder_grant_joins.data:
                break

            grant_ids_batch = [join["grant_id"] for join in funder_grant_joins.data]
            all_grant_ids.extend(grant_ids_batch)
            if len(funder_grant_joins.data) < batch_size:
                break

            offset += batch_size

        #fetch grants
        all_grants = []
        if all_grant_ids:
            batch_size = 100
            total_batches = (len(all_grant_ids) - 1) // batch_size + 1

            for i in range(0, len(all_grant_ids), batch_size):
                batch_ids = all_grant_ids[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                grants_response = supabase.table("grants").select("*").in_("grant_id", batch_ids).execute()
                all_grants.extend(grants_response.data)

        grants_df = pd.DataFrame(all_grants)
        grants_df["registered_num"] = funder_number

    except Exception as e:
        return {
            "error": True,
            "message": f"Error fetching grants: {str(e)}"
        }

build_grants_df(test_funder_number, url, key)







# def get_lookup_tables()

# def build_pair_df()
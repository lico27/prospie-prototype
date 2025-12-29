import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
import os
import sys
from collections import defaultdict
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
test_funder_number = "262861"
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
                grants_response = supabase.table("grants").select("*").in_("grant_id", batch_ids).execute()
                all_grants.extend(grants_response.data)

        grants_df = pd.DataFrame(all_grants)
        grants_df["registered_num"] = funder_number

    except Exception as e:
        return {
            "error": True,
            "message": f"Error fetching grants: {str(e)}"
        }
    
    return grants_df

grants_df = build_grants_df(test_funder_number, url, key)

def enrich_grants_df(grants_df, url, key):
    """
    Gets recipient data to enrich the grants dataframe.
    """

    supabase = create_client(url, key)

    if len(grants_df) > 0:
        grant_ids_list = grants_df["grant_id"].tolist()

        #join grants to recipients
        all_recipient_joins = []
        offset = 0
        batch_size = 1000

        while True:
            recipient_joins = supabase.table("recipient_grants").select("grant_id, recipient_id").in_("grant_id", grant_ids_list).range(offset, offset + batch_size - 1).execute()

            if not recipient_joins.data:
                break

            all_recipient_joins.extend(recipient_joins.data)
            if len(recipient_joins.data) < batch_size:
                break

            offset += batch_size

        #map grants to unique recipients
        grant_to_recipient = {join["grant_id"]: join["recipient_id"] for join in all_recipient_joins}
        recipient_ids = list(set(grant_to_recipient.values()))

        #fetch recipient data
        all_recipients = []
        batch_size = 100

        for i in range(0, len(recipient_ids), batch_size):
            batch_ids = recipient_ids[i:i+batch_size]
            fetched_recipients = supabase.table("recipients").select("*").in_("recipient_id", batch_ids).execute()
            all_recipients.extend(fetched_recipients.data)

        recipients_df = pd.DataFrame(all_recipients)

        #get classifications for reecipients
        if len(all_recipients) > 0:
            recipient_ids_list = [r["recipient_id"] for r in all_recipients]

            #areas
            recipient_area_joins = []
            offset = 0
            while True:
                joins = supabase.table("recipient_areas").select("recipient_id, area_id").in_("recipient_id", recipient_ids_list).range(offset, offset + 999).execute()
                if not joins.data:
                    break
                recipient_area_joins.extend(joins.data)
                if len(joins.data) < 1000:
                    break
                offset += 1000

            #beneficiaries
            recipient_ben_joins = []
            offset = 0
            while True:
                joins = supabase.table("recipient_beneficiaries").select("recipient_id, ben_id").in_("recipient_id", recipient_ids_list).range(offset, offset + 999).execute()
                if not joins.data:
                    break
                recipient_ben_joins.extend(joins.data)
                if len(joins.data) < 1000:
                    break
                offset += 1000

            #causes
            recipient_cause_joins = []
            offset = 0
            while True:
                joins = supabase.table("recipient_causes").select("recipient_id, cause_id").in_("recipient_id", recipient_ids_list).range(offset, offset + 999).execute()
                if not joins.data:
                    break
                recipient_cause_joins.extend(joins.data)
                if len(joins.data) < 1000:
                    break
                offset += 1000

            #get tables for lookups
            beneficiaries_df = get_table_from_supabase(url, key, "beneficiaries")
            causes_df = get_table_from_supabase(url, key, "causes")
            areas_lookup_df = get_table_from_supabase(url, key, "areas")
            area_lookup = dict(zip(areas_lookup_df["area_id"], areas_lookup_df["area_name"]))
            ben_lookup = dict(zip(beneficiaries_df["ben_id"], beneficiaries_df["ben_name"]))
            cause_lookup = dict(zip(causes_df["cause_id"], causes_df["cause_name"]))

            #group by id
            recipient_areas_map = defaultdict(list)
            recipient_bens_map = defaultdict(list)
            recipient_causes_map = defaultdict(list)

            for join in recipient_area_joins:
                area_name = area_lookup.get(join["area_id"])
                if area_name:
                    recipient_areas_map[join["recipient_id"]].append(area_name)

            for join in recipient_ben_joins:
                ben_name = ben_lookup.get(join["ben_id"])
                if ben_name:
                    recipient_bens_map[join["recipient_id"]].append(ben_name)

            for join in recipient_cause_joins:
                cause_name = cause_lookup.get(join["cause_id"])
                if cause_name:
                    recipient_causes_map[join["recipient_id"]].append(cause_name)

            #add classifications to df
            recipients_df["recipient_areas"] = recipients_df["recipient_id"].map(lambda x: recipient_areas_map.get(x, []))
            recipients_df["recipient_beneficiaries"] = recipients_df["recipient_id"].map(lambda x: recipient_bens_map.get(x, []))
            recipients_df["recipient_causes"] = recipients_df["recipient_id"].map(lambda x: recipient_causes_map.get(x, []))

        #join recipients to grants
        grants_df["recipient_id"] = grants_df["grant_id"].map(grant_to_recipient)
        grants_df = grants_df.merge(
            recipients_df,
            left_on="recipient_id",
            right_on="recipient_id",
            how="left"
        )

    grants_df["funder_num"] = test_funder_number

    return grants_df

grants_df = enrich_grants_df(grants_df, url, key)


# def get_lookup_tables()

# def build_pair_df()
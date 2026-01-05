import json
import pandas as pd
import gc
from sentence_transformers import SentenceTransformer
import numpy as np
from supabase import create_client
import os
import sys
from collections import defaultdict

#add project root to path
sys.path.insert(0, os.path.dirname(__file__))
from backend_utils import get_table_from_supabase

def create_user_embeddings(user_data, model):
    """
    Generates embeddings for user's charity name and text sections (activities and objectives).
    """

    #replace nas with empty string
    user_name = user_data.get("user_name", "") or ""
    user_activities = user_data.get("user_activities", "") or ""
    user_objectives = user_data.get("user_objectives", "") or ""

    #get embedding for name
    user_name_em = model.encode(user_name).tolist()

    #concatenate text sections and embed
    concat_text = f"{user_activities} {user_objectives}"
    concat_text = concat_text.lower()
    user_concat_em = model.encode(concat_text).tolist()

    return user_name_em, user_concat_em

def get_funder_data(funder_number, url, key):
    """
    Fetches data for the selected funder from supabase and builds dataframes via join tables.
    """
    supabase = create_client(url, key)

    #fetch funder data from supabase
    funder_response = supabase.table("funders").select("*").eq("registered_num", funder_number).execute()

    if not funder_response.data or len(funder_response.data) == 0:
        #get a random funder to suggest
        import random
        count_response = supabase.table("funders").select("registered_num", count="exact").execute()
        total_funders = count_response.count if hasattr(count_response, 'count') else 0

        if total_funders > 0:
            random_offset = random.randint(0, total_funders - 1)
            random_funder_response = supabase.table("funders").select("registered_num").limit(1).range(random_offset, random_offset).execute()
            suggested_funder = random_funder_response.data[0]["registered_num"] if random_funder_response.data else None
        else:
            suggested_funder = None

        error_msg = f"Funder number {funder_number} not found in database"
        if suggested_funder:
            error_msg += f". Try {suggested_funder} instead"
        raise ValueError(error_msg)

    funder_data = funder_response.data[0]

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

    #get list entries
    funder_list_joins = supabase.table("funder_list").select("list_id").eq("registered_num", funder_number).execute()
    funder_list_ids = [join["list_id"] for join in funder_list_joins.data] if funder_list_joins.data else []

    list_entries = []
    if funder_list_ids:
        fetched_resp = supabase.table("list_entries").select("list_type").in_("list_id", funder_list_ids).execute()
        list_entries = [entry["list_type"] for entry in fetched_resp.data]

    return funder_data, funder_areas, funder_beneficiaries, funder_causes, list_entries

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

def enrich_grants_df(grants_df, funder_number, url, key):
    """
    Gets recipient data to enrich the grants dataframe.
    """

    supabase = create_client(url, key)

    if len(grants_df) > 0:
        grant_ids_list = grants_df["grant_id"].tolist()

        #join grants to recipients
        all_recipient_joins = []
        batch_size = 100

        for i in range(0, len(grant_ids_list), batch_size):
            batch_ids = grant_ids_list[i:i+batch_size]
            recipient_joins = supabase.table("recipient_grants").select("grant_id, recipient_id").in_("grant_id", batch_ids).execute()

            if recipient_joins.data:
                all_recipient_joins.extend(recipient_joins.data)

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
            batch_size = 100
            for i in range(0, len(recipient_ids_list), batch_size):
                batch_ids = recipient_ids_list[i:i+batch_size]
                joins = supabase.table("recipient_areas").select("recipient_id, area_id").in_("recipient_id", batch_ids).execute()
                if joins.data:
                    recipient_area_joins.extend(joins.data)

            #beneficiaries
            recipient_ben_joins = []
            for i in range(0, len(recipient_ids_list), batch_size):
                batch_ids = recipient_ids_list[i:i+batch_size]
                joins = supabase.table("recipient_beneficiaries").select("recipient_id, ben_id").in_("recipient_id", batch_ids).execute()
                if joins.data:
                    recipient_ben_joins.extend(joins.data)

            #causes
            recipient_cause_joins = []
            for i in range(0, len(recipient_ids_list), batch_size):
                batch_ids = recipient_ids_list[i:i+batch_size]
                joins = supabase.table("recipient_causes").select("recipient_id, cause_id").in_("recipient_id", batch_ids).execute()
                if joins.data:
                    recipient_cause_joins.extend(joins.data)

            #get tables for lookups
            beneficiaries_df = get_table_from_supabase(url, key, "beneficiaries")
            causes_df = get_table_from_supabase(url, key, "causes")
            areas_lookup_df = get_table_from_supabase(url, key, "areas")
            area_lookup = dict(zip(areas_lookup_df["area_id"], areas_lookup_df["area_name"]))
            ben_lookup = dict(zip(beneficiaries_df["ben_id"], beneficiaries_df["ben_name"]))
            cause_lookup = dict(zip(causes_df["cause_id"], causes_df["cause_name"]))

            #cleanup lookup dataframes
            del beneficiaries_df, causes_df, areas_lookup_df
            gc.collect()

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

            #cleanup temporary lists and maps
            del recipient_area_joins, recipient_ben_joins, recipient_cause_joins
            del recipient_areas_map, recipient_bens_map, recipient_causes_map
            del area_lookup, ben_lookup, cause_lookup
            gc.collect()

        #join recipients to grants
        grants_df["recipient_id"] = grants_df["grant_id"].map(grant_to_recipient)
        grants_df = grants_df.merge(
            recipients_df,
            left_on="recipient_id",
            right_on="recipient_id",
            how="left"
        )

    grants_df["funder_num"] = funder_number

    return grants_df

def get_lookup_tables(url, key):
    """
    Gets lookup tables from supabase for reference later.
    """

    areas_df = get_table_from_supabase(url, key, "areas")
    hierarchies_df = get_table_from_supabase(url, key, "area_hierarchy")

    return areas_df, hierarchies_df

def build_pair_df(user_data, funder_data, funder_areas, funder_beneficiaries, funder_causes, list_entries, user_name_em, user_concat_em):
    """
    Creates a dataframe of user and funder pairs.
    """

    pair_df = pd.DataFrame([{
        #user
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"],
        "user_name_em": user_name_em,
        "user_areas": user_data["user_areas"],
        "user_beneficiaries": user_data["user_beneficiaries"],
        "user_causes": user_data["user_causes"],
        "user_concat_em": user_concat_em,
        "user_extracted_class": user_data["user_extracted_class"],

        #funder
        "funder_registered_num": funder_data["registered_num"],
        "funder_name": funder_data["name"],
        "website": funder_data["website"],
        "areas": funder_areas,
        "beneficiaries": funder_beneficiaries,
        "causes": funder_causes,
        "concat_em": funder_data.get("concat_em"),
        "extracted_class": funder_data.get("extracted_class"),
        "is_potential_sbf": funder_data.get("is_potential_sbf", False),
        "is_nua": funder_data.get("is_nua", False),
        "is_on_list": len(list_entries) > 0,
        "list_entries": list_entries
    }])

    return pair_df

#garbage collection code adapted from Shaibu (2024)
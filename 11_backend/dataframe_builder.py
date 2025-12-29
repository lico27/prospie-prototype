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

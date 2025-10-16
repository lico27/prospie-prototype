import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client

#get keys from env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

#create client instance
supabase = create_client(url, key)

def pipe_to_supabase(df, table, unique_key):

    #make df into dictionaries to be readable by supabase
    df = df.to_dict("records")

    try:
        print(f"Attempting to upsert to table: {table}")
        #pipe df to supabase
        response = (
            supabase.table(table)
            .upsert(df, on_conflict = unique_key)
            .execute()
        )
    except Exception as e:
        print(f"Error upserting to {table}: {e}")
        raise
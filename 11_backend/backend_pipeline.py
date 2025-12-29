from dataframe_builder import *


#get keys from env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

user_name_em, user_concat_em = create_user_embeddings(test_user_data, model)

funder_data, funder_areas, funder_beneficiaries, funder_causes = get_funder_data(test_funder_number)

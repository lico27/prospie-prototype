from dataframe_builder import *

user_name_em, user_concat_em = create_user_embeddings(test_user_data, model)

funder_data, funder_areas, funder_beneficiaries, funder_causes = get_funder_data(test_funder_number, url, key)

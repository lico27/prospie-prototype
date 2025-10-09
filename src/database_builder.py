import os
from dotenv import load_dotenv
from cc_api_data_extractor import get_prototype_data

#get key from env
load_dotenv()
api_key = os.getenv("API_KEY")

#define api variables
hdr ={
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": f"{api_key}",
    }
operation = ["allcharitydetailsV2", "charityoverview", "charitygoverningdocument"]
# c_nums, _ = get_sample()
c_nums = [225859, 210928, 239754, 1185248, 1173390, 1156861, 1132685, 1166968, 1134632] #, 265281, 287535, 1185673, 1197528, 1051202, 1091991, 1157548, 1185248, 1173390, 1156861, 1132685, 1166968, 1134632, 276201, 1192734, 225071, 1083273, 309344, 1188721]
charity_data = {}
columns = ["reg_charity_number", "charity_name", "web", "activities", "charitable_objects", "latest_income", "latest_expenditure", "who_what_where", "CharityAoOCountryContinent", "CharityAoOLocalAuthority", "CharityAoORegion"]
df_rows = []

#call charity commission api and extract data to build tables
funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas = get_prototype_data(operation, hdr, c_nums, charity_data, columns, df_rows)
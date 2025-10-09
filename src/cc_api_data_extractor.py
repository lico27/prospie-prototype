import pandas as pd
import janitor
import os
from dotenv import load_dotenv
from cc_api.cc_api_client import call_cc_api
from cc_api.classifications_extractor import build_classifications_tables
from cc_api.areas_extractor import build_areas_tables

#get key from env
load_dotenv()
api_key = os.getenv("API_KEY")

def get_prototype_data():

	#define api variables
	hdr ={
		"Cache-Control": "no-cache",
		"Ocp-Apim-Subscription-Key": f"{api_key}",
		}
	operation = ["allcharitydetailsV2", "charityoverview", "charitygoverningdocument"]
	# c_nums, _ = get_sample()
	c_nums = [225859, 210928, 239754, 1185248, 1173390, 1156861, 1132685, 1166968, 1134632]
	charity_data = {}
	columns = ["reg_charity_number", "charity_name", "web", "activities", "charitable_objects", "latest_income", "latest_expenditure", "who_what_where", "CharityAoOCountryContinent", "CharityAoOLocalAuthority", "CharityAoORegion"]
	df_rows = []

	#call api
	df = call_cc_api(operation, hdr, c_nums, charity_data, columns, df_rows)

	#rename columns to match schema
	df = df.rename(columns={
		"reg_charity_number": "registered_num",
		"charity_name": "name",
		"web": "website",
		"charitable_objects": "objectives",
		"latest_income": "income",
		"latest_expenditure": "expenditure",
		"who_what_where": "classifications",
		"CharityAoOCountryContinent": "country_continent",
		"CharityAoOLocalAuthority": "local_authority",
		"CharityAoORegion": "region"
	})

	#build funders table
	funders = df.drop(columns=["classifications", "country_continent", "local_authority", "region"])

	#build beneficiaries and causes tables and join tables
	beneficiaries, funder_beneficiaries, causes, funder_causes = build_classifications_tables(df)
	
	#build areas table and join table
	funder_areas, areas = build_areas_tables(df)	

	return funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas
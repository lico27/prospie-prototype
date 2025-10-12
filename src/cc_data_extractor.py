import pandas as pd
import janitor
import os
from dotenv import load_dotenv
from .api_clients import call_cc_api
from .cc_api.classifications_extractor import build_classifications_tables
from .cc_api.funder_areas_extractor import build_areas_tables
from .cc_api.areas_table_builder import transform_area_columns
from .sample_function import get_sample

#get key from env
load_dotenv()
api_key = os.getenv("API_KEY")

def extract_cc_data(c_nums):

	#define api variables
	hdr ={
		"Cache-Control": "no-cache",
		"Ocp-Apim-Subscription-Key": f"{api_key}",
		}
	operation = ["allcharitydetailsV2", "charityoverview", "charitygoverningdocument"]
	charity_data = {}
	columns = ["reg_charity_number", "charity_name", "web", "activities", "charitable_objects", "latest_income", "latest_expenditure", "who_what_where", "CharityAoOCountryContinent", "CharityAoOLocalAuthority", "CharityAoORegion"]
	df_rows = []

	#call api
	df = call_cc_api(operation, hdr, c_nums, charity_data, columns, df_rows)

	return df


def get_funder_data():

	# c_nums, _ = get_sample()
	c_nums = ["1015792", "1168435", "239754", "265281", "287535", "1185673", "1197528", "1051202"]

	df = extract_cc_data(c_nums)

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

	return funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, c_nums


def get_recipient_data(recipient_grants, areas, funder_areas):

	#convert recipients to list
	c_nums = list(recipient_grants[recipient_grants["recipient_id"].str.isdigit()]["recipient_id"])

	c_nums = c_nums[:5] #remove this

	recipient_df = extract_cc_data(c_nums)

	#rename and prepare for area extraction
	recipient_df = recipient_df.rename(columns={
		"reg_charity_number": "registered_num",
		"CharityAoOCountryContinent": "country_continent",
		"CharityAoOLocalAuthority": "local_authority",
		"CharityAoORegion": "region"
	})

	#extract area names from recipient data
	_, recipient_all_areas = transform_area_columns(recipient_df)
	recipient_all_areas = recipient_all_areas.drop_duplicates()

	#merge with existing areas table to get area IDs
	recipient_areas = recipient_all_areas.merge(
		areas.rename(columns={"area_level": "area_type"}),
		on=["area_name", "area_type"]
	)[["registered_num", "area_id"]].drop_duplicates()

	#build recipient table
	recipients = recipient_df[["registered_num", "charity_name", "activities"]]
	recipients = recipients.rename(columns={"registered_num": "recipient_id", "charity_name": "name"})

	return recipients, recipient_areas
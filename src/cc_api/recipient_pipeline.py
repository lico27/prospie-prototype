from src.cc_api.client import extract_cc_data
from src.cc_api.areas_builder import transform_area_columns
from src.utils import clean_data

def get_recipient_data(recipient_grants, areas):

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

	#clean data
	cc_recipient_tables = [recipients, recipient_areas]
	clean_tables_recipients = clean_data(cc_recipient_tables, ["name"], ["activities"], [])
	recipients, recipient_areas = clean_tables_recipients

	return recipients, recipient_areas

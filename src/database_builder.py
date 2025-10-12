from src.cc_data_extractor import get_funder_data, get_recipient_data
from src.giving360_api_data_extractor import get_grant_data

def get_data():

	#call charity commission api and extract data to build tables for funders
	funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, c_nums = get_funder_data()

	#call giving360 api and extract data
	grants, funder_grants, recipient_grants = get_grant_data(c_nums)

	#call charity commission api and extract data to build tables for recipients
	recipients, recipient_areas = get_recipient_data(recipient_grants, areas)

	return funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, grants, funder_grants, recipients, recipient_grants, recipient_areas

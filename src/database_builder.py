from .cc_funder_data_extractor import get_funder_data
from .giving360_api_data_extractor import get_grant_data

def get_data():

	#call charity commission api and extract data to build tables
	funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, c_nums = get_funder_data()

	# call giving360 api and extract data
	grants, funder_grants = get_grant_data(c_nums)

	#check data types, clean data

	return funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, grants, funder_grants
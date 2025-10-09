from cc_api_data_extractor import get_prototype_data
from giving360_api_data_extractor import get_grant_data

#call charity commission api and extract data to build tables
funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas = get_prototype_data()

#call giving360 api and extract data

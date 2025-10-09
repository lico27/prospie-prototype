from cc_funder_data_extractor import get_funder_data
from giving360_api_data_extractor import get_grant_data

#call charity commission api and extract data to build tables
funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, c_nums = get_funder_data()

#call giving360 api and extract data
grants = get_grant_data(c_nums)

grants_sample = grants[:5]

for grant in grants_sample:
        print(grant["data"]["fundingOrganization"][0]["name"] + " gave " + str(grant["data"]["amountAwarded"]) + grant["data"]["currency"] + " to " + grant["data"]["recipientOrganization"][0]["name"] + " for a project entitled " + grant["data"]["title"] + " on " + str(grant["data"]["awardDate"]))
import pandas as pd
from .api_clients import call_360_api

c_nums = ["1015792"] #, "1168435", "1113488"] #remember to remove this

grants = call_360_api(c_nums)
grants_sample = grants[:5]
for grant in grants_sample:
        print(grant["data"]["fundingOrganization"][0]["name"] + " gave " + str(grant["data"]["amountAwarded"]) + " to " + grant["data"]["recipientOrganization"][0]["name"])

df = pd.json_normalize(grants)

grant_columns = ["grant_id", "data.title", "data.description", "data.amountAwarded", "data.currency", "data.awardDate"]
grant_df = df[grant_columns]

print(grant_df.head())
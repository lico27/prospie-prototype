import pandas as pd
from .api_clients import call_360_api

def get_grant_data(c_nums):

        """
        Gets data from the 360Giving API.
        Returns dataframes to be piped to database, containing information about grants reported to 360Giving.
        Also builds join tables to deal with many-to-many relationships in the database.
        """

        try:
                #call api and normalise data from lists into required columns
                grants = call_360_api(c_nums)
                df = pd.json_normalize(grants)
                grant_columns = ["grant_id", "funder_registered_num", "data.title", "data.description", "data.amountAwarded", "data.currency", "data.awardDate", "data.recipientOrganization"]
                grant_df = df[grant_columns]
        except Exception as e:
                print(f"Error with initial API call: {e}")
                raise

        try:
                #explode recipient list and normalise into columns
                exploded_df_recipients = grant_df.explode("data.recipientOrganization")
                recipients_df = pd.json_normalize(exploded_df_recipients["data.recipientOrganization"])
                recipients_df.columns = ["recipient_" + col for col in recipients_df.columns]

                #reset indexes and combine
                exploded_df_recipients = exploded_df_recipients.reset_index(drop=True)
                recipients_df = recipients_df.reset_index(drop=True)
                grants = pd.concat([exploded_df_recipients, recipients_df], axis=1)
        except Exception as e:
                print(f"Error processing recipient data: {e}")
                raise

        try:
                #finalise and tidy grants table
                grants = grants[["grant_id", "data.title", "data.description", "data.amountAwarded", "data.currency", "data.awardDate", "recipient_id"]]
                grants.loc[:, 'data.awardDate'] = grants['data.awardDate'].astype(str).str.strip().str[:4]
                grants = grants.rename(columns={"data.title": "grant_title",
                                                "data.description": "grant_desc",
                                                "data.amountAwarded": "amount",
                                                "data.currency": "currency",
                                                "data.awardDate": "year"
                                                })
                grants["recipient_id"] = grants["recipient_id"].str.replace("^GB-CHC-", "", regex=True)

                #build join tables
                funder_grants = grant_df[["grant_id", "funder_registered_num"]].rename(columns={"funder_registered_num": "registered_num"})
                recipient_grants = grants[["grant_id", "recipient_id"]]

                #drop unnecessary column
                grants = grants.drop(columns=["recipient_id"])

        except Exception as e:
                print(f"Error building tables: {e}")
                raise

        return grants, funder_grants, recipient_grants

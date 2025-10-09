import time
import requests
import pandas as pd

API_URL = "https://api.threesixtygiving.org/api/v1/"

def get_grant_data(c_nums):

    grants = []
        
    for num in c_nums:
        org_id = "GB-CHC-" + num
        url = API_URL + "org/" + org_id + "/grants_made/"
        
        try:
            while url is not None:
                r = requests.get(url, headers={"Accept": "application/json"})
                r.raise_for_status()
                
                data = r.json()
                grants.extend(data["results"])
                url = data["next"]
                
                time.sleep(0.6)
                
        except requests.exceptions.HTTPError as e:
            # Skip this charity if there's an HTTP error (e.g., 404 not found)
            print(f"Skipping {num}: {e}")
            continue
        except requests.exceptions.RequestException as e:
            # Catch any other request-related errors
            print(f"Error fetching grants for {num}: {e}")
            continue
    
    return grants
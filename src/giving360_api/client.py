import requests
import time

def call_360_api(c_nums):

    API_URL = "https://api.threesixtygiving.org/api/v1/"
    grants = []

    for num in c_nums:
        org_id = "GB-CHC-" + num
        url = API_URL + "org/" + org_id + "/grants_made/"

        try:
            while url is not None:
                r = requests.get(url, headers={"Accept": "application/json"})
                r.raise_for_status()

                data = r.json()

                for grant in data["results"]:
                    grant["funder_registered_num"] = num

                grants.extend(data["results"])
                url = data["next"]

                #limit requests
                if url is not None:
                    time.sleep(0.6)

        except requests.exceptions.HTTPError as e:
            continue
        except requests.exceptions.RequestException as e:
            print(f"Error fetching grants for {num}: {e}")
            continue

    return grants

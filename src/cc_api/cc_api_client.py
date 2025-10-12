import urllib.request
import json
import pandas as pd

def call_cc_api(operation, hdr, c_nums, charity_data, columns, df_rows):

	"""
	Calls the Charity Commission API to get data for a list of charity numbers.

	Parameters
	----------
	operation : list of API operations to call for each charity number.
	hdr : dictionary of headers to use for the API request.
	c_nums : list of charity numbers to get data for.
	charity_data : dictionary to store the data for each charity number.
	columns : list of the columns/variables required from the API.
	df_rows : list to store the data for each charity number per row.

	Returns a dataframe containing the data for each charity number.
	"""

	for num in c_nums:
		charity_data[num] = {}

		#get data from each api operation
		for op in operation:
			url = f"https://api.charitycommission.gov.uk/register/api/{op}/{num}/0"
			try:
				req = urllib.request.Request(url, headers=hdr)
				req.get_method = lambda: 'GET'
				response = urllib.request.urlopen(req)
				
				data = json.load(response)
				response.close()
				
				#get relevant columns from operation and add to charity data
				for col in columns:
					if col in data and data[col] is not None:
						charity_data[num][col] = data[col]
															
			except Exception as e:
				print(f"Error with {op}/{num}: {e}")

	#get relevant data and combine into one row per charity
	for num, data in charity_data.items():
		row = {col: data.get(col, None) for col in columns}
		row['reg_charity_number'] = num
		df_rows.append(row)

	#convert to dataframe
	try:
		df = pd.DataFrame(df_rows)
	except Exception as e:
		print(f"Error creating dataframe: {e}")
		raise

	return df
import json
import requests

# Goal is to access "Trichloroethene"
C2HCl3_synonym = ""

# Read the JSON going out-to-in as you read this code
# Get the database list of adsorbates
URL = "https://adsorbents.nist.gov/isodb/api/gases.json/"
gas_list = json.loads(requests.get(URL).content)

# Get the dictionary containing information for this gas
C2HCl3_dict = gas_list[0]

# Get the list of synonyms of this gas
C2HCl3_synonyms_list = C2HCl3_dict.get("synonyms")

# "Trichloroethene" is in index 4 (5th position)
C2HCl3_synonym = C2HCl3_synonyms_list[4]

# Print the value to confirm that we have found the correct name
print("Another name for 'C2HCl3' is: " + 
        "'" + C2HCl3_synonym + "'")

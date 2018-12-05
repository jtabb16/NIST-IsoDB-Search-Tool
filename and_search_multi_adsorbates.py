###############################################################################
# Author: Jack Tabb (Undergraduate Researcher)
# Date: June 06, 2018
# Research Group: Clemson's Scott Research Group
#                 in Department of Chemical and Biomolecular Engineering
# Purpose: Allow 'And'-search of multi-component isotherm data on 
#          NIST/ARPA-E Database of Novel and 
#          Emerging Adsorbent Materials
# Using Code From: NIST ISODB API 
#                   (https://adsorbents.nist.gov/isodb/index.php#apis)
#                  And NIST's example tool
#                   (https://github.com/dwsideriusNIST/adsorption_tools)
# Python version: 3.6.5
# Input: User-Specified Adsorbate gases
# Output: Simplified database entries that match the search parameters.
#           DOI -- Digital Object Identifier (permanent identity of an article 
#                   or document linked on the internet)
#           title -- The title of the research paper containing information 
#                       about the requested adsorbates
#           journal -- The journal that the NIST database accessed the research
#                       paper from
#           year -- The year that the research paper was published in the journal
#           authors -- The people who contributed to / made the research paper
#           adsorbentMaterial -- The material that the research paper discusses 
#                                   adsorbates adsorbing onto
#           isotherms -- Filenames of the isotherm data that the NIST database 
#                           has aquired from the research papers
# How to use this "And"-search tool:
#   1. Scroll down to the bottom of this file and set "allowMore" and 
#       "needIsoData" to the desired values. Further instructions are down there.
#   2. Ensure that this script ("and_search_multi_adsorbates.py"), the 
#       "relevant_biblio_entry.py" module, and the folder named "results" 
#           are all in the same directory.
#   3. Ensure you have the necessary imported modules (listed in the next 
#       section of this script). You may need to use a package manager such as 
#           pip or conda to install them.
#   4. Run this script in a shell / terminal / command-line.
#       Ex: python3 and_search_multi_adsorbates.py
#   5. When the program runs, it will ask for which adsorbates you want to 
#       search for. Follow the on-screen instructions.
#   6. Go to the results folder to see your most recent results. 
#       They are named as yyyymmdd_hhmmss. For example, "20180605_142520"
#           means 2:25 (and 20 seconds) PM on June 5th, 2018.
#   7. Use the results as follows:
#       Find original research paper with DOI at http://dx.doi.org/{DOI}    
#       Example: http://dx.doi.org/10.1002/chem.200902144
#       Access the isotherm data at: https://adsorbents.nist.gov/isodb/api/isotherm/{filename}.json
#       You can also change the .json to .csv
#       Example: https://adsorbents.nist.gov/isodb/api/isotherm/10.1002Aic.10306.Isotherm1.csv
###############################################################################



###############################################################################
# Import Python Packages
# End User is responsible for installation of missing packages using an 
#   appropriate Python package manager (such as pip)
import json
import requests
import sys
import time
import os

# Import other modules from this project
from relevant_biblio_entry import RelevantBilbioEntry as RBE
###############################################################################



###############################################################################
# Define helper functions
def welcome():
    print("Welcome to 'AND' search for NIST-ISODB!")

def get_user_input():
    user_adsorbate_set = set()
    print("Using the naming scheme from the NIST-ISODB, " +
            "list the adsorbate materials " +
            "you wish to find isotherm data for.\n" +
            "\tEx: 'N2' instead of 'Nitrogen' and 'H2' instead of 'Hydrogen'")
    print("Enter adsorbates separated by a space. Then press enter: ")
    user_adsorbate_set = {str(adsorbate) for adsorbate in input().split()}
    print("")
    return user_adsorbate_set

def check_adsorbates(user_adsorbate_set):
    print("Checking for adsorbate synonyms...")
    # Get the database listing of adsorbates and their synonyms
    gas_JSON_list = get_JSON("api/gases.json/")

    # Find the InChIKey that corresponds to each adsorbate material
    # NOTE: InChI stands for International Chemical Identifier
    #       InChIKey is a digital representation of the InChI
    #       For more details, see:
    #       https://en.wikipedia.org/wiki/International_Chemical_Identifier
    InChIKey_set = set()
    found_adsorbate_set = set()
    for NIST_gas_dict in gas_JSON_list:
        adsorbate_synonym_set = set(NIST_gas_dict["synonyms"])
        for user_adsorbate in user_adsorbate_set:
            if user_adsorbate in adsorbate_synonym_set:
                found_adsorbate_set.add(user_adsorbate)
                InChIKey_set.add(NIST_gas_dict["InChIKey"])

    # If all adsorbates weren't found, the rest of the program won't work, 
    #   so exit the script.
    # NOTE: If an InChIKey could not be found for the listed adsorbate(s), 
    #       then it is possible that another name for the adsorbate(s) may work.
    if (len(user_adsorbate_set) != len(found_adsorbate_set)):
        sys.exit("ERROR: " + str(user_adsorbate_set - found_adsorbate_set) +
                " is/are not recognized " +
                "as a valid name for a gas." +
                "\nTry using another name for the molecule(s)")

    # If the above statement didn't get triggered, then all user-specified
    #   adsorbates were found. This means that we can continue
    return InChIKey_set

def find_relevant_entries(user_InChIKey_set, allow_more=False, 
                                            need_iso_data=True):
    print("Finding relevant entries...")
    # Get the database listing of all research papers
    biblio_JSON_list = get_JSON("api/biblios.json/")

    # Iterate through all entries in the database for isotherm data
    relevant_biblio_entries = []
    biblio_count = 0 # Count how many entries are in the database
    for biblio_entry in biblio_JSON_list:
        biblio_count += 1
        # We only want listings in the json that have an "adsorbates" list
        if "adsorbates" in biblio_entry:
            # Get the list of adsorbates that this entry is for
            biblio_adsorbate_list = biblio_entry["adsorbates"]
            biblio_isotherm_list = biblio_entry["isotherms"]
            biblio_adsorbate_InChIKey_set = {biblio_adsorbate_dict["InChIKey"] 
                                                for biblio_adsorbate_dict in 
                                                biblio_adsorbate_list}
            # If this entry has isotherm data and the user only wants entries 
            # with isotherm data or if the user doesn't care if there is 
            # isotherm data.
            #   If all user-specified adsorbates are found in this entry,
            #       and only user-specified adsorbates are found in this entry
            #   OR
            #   If all user-specified adsorbates are found in this entry,
            #       but other adsorbates are in the entry, too,
            #       And the user is okay with more adsorbates being in an entry
            #           than he/she specified.
            # Then, this entry is of use, so keep track of it
            if ( ((need_iso_data==True) and (len(biblio_isotherm_list) > 0)) \
                    or ((need_iso_data==False)) ) \
                and \
               ( (biblio_adsorbate_InChIKey_set == user_InChIKey_set) or \
                    ((biblio_adsorbate_InChIKey_set >= user_InChIKey_set) \
                    and allow_more==True) ):
                        relevant_biblio_entries.append(biblio_entry)
    # Show how many results were found out of how many entries there 
    #   were in the database
    print (f"{len(relevant_biblio_entries)} out of {biblio_count} entries" +
            " matched your search parameters")
    return relevant_biblio_entries

def instantiate_relevant_biblio_entries(relevant_biblio_entries):
    print("Formatting entries...")
    # Instantiate all relevant biblio entries as an object in Python with 
    # the information that we care about
    relevant_entries_formatted_list = []
    for entry in relevant_biblio_entries:
        relevant_entries_formatted_list.append(RBE(entry["DOI"],
                                    entry["title"],
                                    entry["journal"],
                                    entry["year"],
                                    entry["authors"],
                                    entry["adsorbentMaterial"],
                                    entry["adsorbates"],
                                    entry["isotherms"]))
    return relevant_entries_formatted_list

def get_JSON(api_url=''):
    print("Fetching JSON file from database...")
    host = "adsorbents.nist.gov/isodb/"
    URL = "https://" + host + api_url
    JSON_file = requests.get(URL)
    JSON_list = json.loads(JSON_file.content)
    return JSON_list

def put_results_in_file(formatted_relevant_biblio_entry_list):
    timestr = time.strftime("%Y%m%d_%H%M%S") # Get the current time and date
    # Create a new file for output with the time and date as a part of its name
    file_name = (os.path.dirname(os.path.realpath(__file__)) + "/results/" + 
                timestr + ".txt")
    with open(file_name, 'w') as output_file:
        output_file.write("Find original research paper with DOI at " +
                            "http://dx.doi.org/{DOI}\n")
        output_file.write("Example: http://dx.doi.org/10.1002/chem.200902144\n")
        output_file.write("Access the isotherm data at: https://adsorben" +
            "ts.nist.gov/isodb/api/isotherm/{filename}.json\n")
        output_file.write("You can also change the .json to .csv\n")
        output_file.write("Example: https://adsorbents.nist.gov/isodb/api/" + 
            "isotherm/10.1002Aic.10306.Isotherm1.csv\n")
        output_file.write("Below is a listing of all results that match your" +
            " search parameters:\n\n")
        # Print all the results
        for entry in formatted_relevant_entries:
            output_file.write(str(entry)+"\n\n")
    print("Results printed to " + file_name)
###############################################################################



###############################################################################
# Use the helper functions to run the program
if __name__ == "__main__":
    welcome() # Welcome the user of the program
    user_adsorbates = get_user_input() # Get all user input
    InChIKeys = check_adsorbates(user_adsorbates) # Check user input

    # Now that we have the list of InChIKeys that apply to the user-specified 
    #   adsorbates to find isotherms for, we can search for the isotherm data.
    # To allow search results that contain the specified adsorbates 
    #   AND any other adsorbates, set allowMore=True.
    # To search for only the user-specified adsorbates (exclusivley), set
    #   allowMore=False.
    # To only get results that have isotherm data, set needIsoData=True.
    # If the user doesn't care about having isotherm data (results can be a mix 
    #   of having isotherm data and not having isotherm data), 
    #   set needIsoData=False.
    # NOTE: This tool has only been tested with allowMore=False and needIsoData=True
    allowMore = False
    needIsoData=True
    relevant_entries = find_relevant_entries(InChIKeys, allowMore, needIsoData)
    # Format all relevant biblio entries for sharing.
    formatted_relevant_entries = instantiate_relevant_biblio_entries(
                                                            relevant_entries)
    # Share the formatted, relevant entries with the user.
    put_results_in_file(formatted_relevant_entries)
###############################################################################
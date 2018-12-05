###############################################################################
# Author: Jack Tabb (Undergraduate Researcher)
# Date: June 06, 2018
# Research Group: Clemson's Scott Research Group
#                 in Department of Chemical and Biomolecular Engineering
# Purpose: Support the 'And'-search tool with structured data output.
###############################################################################

class RelevantBilbioEntry:
    def __init__(self, _doi="", _title="", _journal="", _year="", _authors=[""], 
                    _adsorbentMaterial=[""], _adsorbates=[{}], _isotherms = [{}]):
        self._doi = _doi
        self._title = _title
        self._journal = _journal
        self._year = _year
        self._authors = _authors
        self._adsorbentMaterial = _adsorbentMaterial
        self._adsorbates = _adsorbates
        self._isotherms = _isotherms

    def __str__(self):
        """Define a string representation of all information in this class"""
        returnString = ""
        returnString += "DOI: " + self._doi + "\n"
        returnString += "title: " + self._title +"\n"
        returnString += "journal: " + self._journal +"\n"
        returnString += "year: " + str(self._year) + "\n"
        returnString += "authors: " + ", ".join([author for author in self._authors]) + "\n"
        returnString += "adsorbentMaterial: " + ", ".join([adsM for adsM in self._adsorbentMaterial]) +"\n"
        returnString += "adsorbates: "
        for adsorbate_dict in self._adsorbates:
            returnString += adsorbate_dict["name"] + ", "
        returnString += "\n"
        returnString += "isotherms: "
        for isotherm_dict in self._isotherms:
            returnString += isotherm_dict["filename"] + ", "
        return returnString

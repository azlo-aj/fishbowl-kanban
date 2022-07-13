def get_category(cell):
    '''input a cell from CSTMFLD. reads cell contents and extracts and returns the part category, e.g. "Weldment"'''
    val = re.search(r'(?<="name": "Category", "type": "Drop-Down List", "value": ")[A-Z][a-z]*', cell)
    # (?<=...) matches if the current string is preceeded by a match for "...". This preceeding string is not included in the returned string
    # [A-Z][a-z]* matches any capital letter preceeded by any number of lowercase letters
    if val:
        return val.group(0) # group(0) refers to the first string match found (not including excluded chars)
    else:
        return None
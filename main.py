import re
import pandas as pd

df = pd.read_csv(r'kanban query.csv', encoding='latin-1', na_filter=False) # IMPORT FISHBOWL QUERY
df.drop(columns=['BOMITEMDESCRIPTION','ITEMNAME', 'BOMITEMID'], inplace=True) # DROP UNUSED COLUMNS
df.sort_values(by=['PARTDESCRIPTION','BOMITEMPART'], axis=0, ascending=True) # SORT BY RAW MATERIAL
rgoods = df.loc[df['TYPEID'].astype(int) == 20] # RAW GOODS DF
fgoods = df.loc[df['TYPEID'].astype(int) == 10] # FINISHED GOODS DF

def get_category(cell):
    '''input a cell from CSTMFLD. reads cell contents and extracts and returns the part category, e.g. "Weldment"'''
    val = re.search(r'(?<="name": "Category", "type": "Drop-Down List", "value": ")[A-Z][a-z]*', cell)
    # (?<=...) matches if the current string is preceeded by a match for "...". This preceeding string is not included in the returned string
    # [A-Z][a-z]* matches any capital letter preceeded by any number of lowercase letters
    if val:
        return val.group(0) # group(0) refers to the first string match found (not including excluded chars)
    else:
        return None

def find_cats(df):
    '''takes input DF, reads CSTMFLD column, and creates a new column representing extracted category values'''
    df['CAT'] = None
    for i in df['CSTMFLD'].index:
        result = re.search(r'(?<="name": "Category", "type": "Drop-Down List", "value": ")[A-Z][a-z]*', df.at[i, 'CSTMFLD'])
        if result:
            df.at[i, 'CAT'] = result.group(0)
    return df
df = find_cats(df)


class Ticket(rgoods, fgoods):
    def __init__(self):
        pass
    def get_header_df(self):
        '''Returns a dataframe containing values used in the ticket header'''
        pass
    def get_finished_goods_df(self):
        '''Returns a dataframe in which each row is a finished good for the ticket'''
        pass   
    def get_raw_goods_df(self):
        '''Returns a dataframe in which each row is a raw good for the ticket'''
        pass

print('end')
import re
import pandas as pd

class WOquery():
    def __init__(self, inputCSV):
        # INITIAL SETUP
        self.df = pd.read_csv(inputCSV, encoding='latin-1', na_filter=False) # IMPORT FISHBOWL QUERY
        self.df.columns = [x.lower() for x in self.df.columns] # MAKE COLUMNS LOWERCASE
        self.df.drop(self.df.columns[self.df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True) # DROP BLANK COLS
        self.df.drop(columns=['bomitemdescription','itemname', 'bomitemid'], inplace=True) # DROP UNUSED COLUMNS
        self.df.sort_values(by=['partdescription','bomitempart'], axis=0, ascending=True) # SORT BY RAW MATERIAL
        self.df = self.uppercase(self.df) # MAKE STR VALUES UPPERCASE
        
        # CREATE SOME NEW COLUMNS
        self.df['processed'] = False # MARKS WHEN ROW HAS BEEN PROCESSED INTO A TICKET
        self.df['cat'] = None # MARKS CATEGORY. OBTAINED FROM CUSTOM FIELD COLUMN
        
        # EXTRACT CATEGORY FROM CUSTOM FIELD COLUMN
        findstr = '"name": "Category", "type": "Drop-Down List", "value": "'
        self.df = self.extract_cstmfld(findstr, 'cat', self.df)
        
    @classmethod          
    def extract_cstmfld(self, findstr, outputcol, df, readstr=r"[A-Z][a-z]*", uppercase=True):
        '''
        extracts the value of a custom field and outputs it to another column
        '''  
        for i in df['cstmfld'].index:
            result = re.search(r'(?<=' + f'{findstr}' + r')' + f'{readstr}', df.at[i, 'cstmfld'])
            if result and uppercase:
                df.at[i, outputcol] = result.group(0).upper()
            elif result:
                df.at[i, outputcol] = result.group(0)
        return df
    
    @classmethod            
    def uppercase(self, df):
        '''
        Makes all string values in df uppercase
        '''
        for col in df.columns:
            if col == 'cstmfld' or col == 'partdescription':
                continue
            df[col] = df[col].astype(str).str.upper()
        return df         

    @classmethod    
    def col_uniques(cls, df, col):
        '''
        Returns a list of unique values for the given column
        e.g. vals = WOquery.col_uniques(df, 'cat')
        '''
        return pd.unique(df[col]).tolist()
        
    def shorty(self, typeid=None, category=None, processed=None, df=None):
        ''' 
        Returns a trimmed version of self.df. Empty arguments do nothing.
        Rows with column values that do not match those listed in the arguments are dropped.
        '''
        if df is None:
            df = self.df
        if isinstance(typeid, int) or isinstance(typeid, str):
            if typeid == 10 or str(typeid).upper() == "FINISHED" or str(typeid).upper() == "F":
                df = df.loc[df['typeid'].astype(int) == 10]
            elif typeid == 20 or str(typeid.upper()) == "RAW" or str(typeid.upper()) == "R":
                df = df.loc[df['typeid'].astype(int) == 20]
        if isinstance(category, str) or isinstance(category, list) or isinstance(category, tuple):
            category = [val.upper() for val in category] # uppercases all items
            df = df.loc[df['cat'].isin(category)]
        if isinstance(processed, bool):
            processed = str(processed).upper() # uppercases all items
            df = df.loc[df['processed'].isin(processed)]
        return df

class Ticket():
    '''
    WOquery() iterates through the imported dataframe. Out of the rows which are still marked
    'false' in the 'processed' column, it determines which group rows belong on
    a single kanban ticket. It sends a dataframe containing just the selected rows to
    Ticket() to be sorted and processed for eventual PDF generation. The rows which were
    exported are marked as "True" in the 'processed' column from WOquery().df
    '''
    def __init__(self, df):
        self.tix = df
        pass
    def gen_header(self):
        '''Returns a dataframe containing values used in the ticket header'''
        pass
    def gen_finished_goods(self):
        '''Returns a dataframe in which each row is a finished good for the ticket'''
        pass   
    def gen_raw_goods(self):
        '''Returns a dataframe in which each row is a raw good for the ticket'''
        pass

wo = WOquery('kanban query.csv')
shorty = wo.shorty(typeid=20)





# rgoods = df.loc[df['TYPEID'].astype(int) == 20] # RAW GOODS DF
# fgoods = df.loc[df['TYPEID'].astype(int) == 10] # FINISHED GOODS DF

print('end')
print('end')
import re
import pandas as pd

class WOquery():
    def __init__(self, inputCSV):
        # INITIAL SETUP
        self.df = pd.read_csv(inputCSV, encoding='latin-1', na_filter=False) # IMPORT FISHBOWL QUERY
        self.df.columns = [x.lower() for x in self.df.columns] # MAKE COLUMNS LOWERCASE
        self.df = self.uppercase(self.df) # MAKE STR VALUES UPPERCASE
        self.df.drop(columns=['bomitemdescription','itemname', 'bomitemid'], inplace=True) # DROP UNUSED COLUMNS
        self.df.sort_values(by=['partdescription','bomitempart'], axis=0, ascending=True) # SORT BY RAW MATERIAL
        
        # CREATE SOME NEW COLUMNS
        self.df['processed'] = False # MARKS WHEN ROW HAS BEEN PROCESSED INTO A TICKET
        self.df['cat'] = None # MARKS CATEGORY. OBTAINED FROM CUSTOM FIELD COLUMN
        
        # EXTRACT CATEGORY FROM CUSTOM FIELD COLUMN
        findstr = '"name": "Category", "type": "Drop-Down List", "value": "'
        self.df = self.extract_cstmfld(findstr, 'cat', self.df)
        
    @classmethod            
    def extract_cstmfld(self, findstr, outputcol, df, readstr=r"[A-Z][a-z]*"):
        for i in df['cstmfld'].index:
            result = re.search(r'(?<=' + f'{findstr}' + r')' + f'{readstr}', df.at[i, 'cstmfld'])
            if result:
                df.at[i, outputcol] = result.group(0)
        return df
                
    @classmethod
    def uppercase(cls, df):
        for col in df.columns:
            df[col] = df[col].astype(str).str.upper()          

    @classmethod    
    def col_uniques(cls, df, col):
        '''
        Returns a list of unique values for the given column
        e.g. vals = WOquery.col_uniques(df, 'cat')
        '''
        return pd.unique(df[col]).tolist()
        
    def shorty(self, typeid, cats=[], processed=[]):
        ''' 
        Returns a trimmed version of self.df. Empty arguments do nothing.
        Rows with column values that do not match those listed in the arguments are dropped.
        '''
        df = self.df
        if isinstance(typeid, int) or isinstance(typeid, str):
            if typeid == 10 or str(typeid).upper() == "FINISHED" or str(typeid).upper() == "F":
                df = df.loc[df['typeid'].astype(int) == 10]
            elif typeid == 20 or str(typeid.upper()) == "RAW" or str(typeid.upper()) == "R":
                df = df.loc[df['typeid'].astype(int) == 20]
        if cats:
            cats = [cat.upper() for cat in cats] # uppercases all items in list
            df = df.loc[df['typeid'].isin(cats)]
        
        return df
    
                
        
        
    def rgoods(self):
        returnflag = True
        def cat(category):
            nonlocal returnflag
            returnflag = False
            df = self.df.loc[self.df['TYPEID'].astype(int) == 20]
            return df.loc[df['cat'].astype(bool) == category.upper()] 
        def u():
            return None # UNPROCESSED RAW GOODS DF
        if returnflag == True:
            return self.df.loc[self.df['TYPEID'].astype(int) == 20] # RAW GOODS DF
    
    def fgoods(self):
        return self.df.loc[self.df['TYPEID'].astype(int) == 10] # FINISHED GOODS DF

class Ticket(WOquery):
    def get_header_df(self):
        '''Returns a dataframe containing values used in the ticket header'''
        pass
    def get_finished_goods_df(self):
        '''Returns a dataframe in which each row is a finished good for the ticket'''
        pass   
    def get_raw_goods_df(self):
        '''Returns a dataframe in which each row is a raw good for the ticket'''
        pass

wo = WOquery('kanban query.csv')
shorty = wo.shorty(10, ['RAW'])





# rgoods = df.loc[df['TYPEID'].astype(int) == 20] # RAW GOODS DF
# fgoods = df.loc[df['TYPEID'].astype(int) == 10] # FINISHED GOODS DF

print('end')
print('end')
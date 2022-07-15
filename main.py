import re
import pandas as pd
from datetime import datetime

class WOquery():
    def __init__(self, input_csv):
        # INITIAL SETUP
        self.df = pd.read_csv(input_csv, encoding='latin-1', na_filter=False) # IMPORT FISHBOWL QUERY
        self.df.columns = [x.lower() for x in self.df.columns] # MAKE COLUMNS LOWERCASE
        self.df.drop(self.df.columns[self.df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True) # DROP BLANK COLS
        self.df.drop(columns=['bomitemdescription','itemname', 'bomitemid'], inplace=True) # DROP UNUSED COLUMNS
        self.df = self.uppercase() # MAKE STR VALUES UPPERCASE
        self.df = self.clean_dates() # CLEAN UP DATES
        
        # FIX NUMERIC DATATYPES AND VALUES
        for col in ('typeid','invqty', 'woitemqty', 'woitemtotal', 'qtyordered'):
            self.df[col] = pd.to_numeric(self.df[col]) 
        self.df['invqty'].fillna(value=0, inplace=True)
                                 
        # CREATE SOME NEW COLUMNS
        self.df['cat'] = None # MARKS CATEGORY. OBTAINED FROM CUSTOM FIELD COLUMN
        self.df['ticket'] = None
        self.df['processed'] = False # MARKS WHEN ROW HAS BEEN PROCESSED INTO A TICKET
        
        # EXTRACT CATEGORY FROM CUSTOM FIELD COLUMN
        findstr = '"name": "Category", "type": "Drop-Down List", "value": "'
        self.df = self.extract_cstmfld(findstr, 'cat')
        
        # FILL TICKET COLUMN WITH TICKET TYPE
        self.df = self.find_ticket_type()
        
    @staticmethod    
    def col_uniques(df, col):
        '''
        Returns a list of unique values for the given column
        e.g. unique_vals = WOquery.col_uniques(df, 'cat')
        '''
        return pd.unique(df[col]).tolist()    
    
    def sort_df(self, ticket=None, df=None):
        '''  
        sorts the dataframe based on the order needed for either WIP or ASSEMBLY tickets
        '''  
        if df is None:
            df=self.df
        if ticket == "WIP":
            df.sort_values(by=['partdescription','bomitempart'], axis=0, ascending=True, inplace=True)
        elif ticket == "ASSEMBLY":
            df.sort_values(by=['wonum','datescheduledfulfillment'], axis=0, ascending=True, inplace=True)
        else:
            raise Exception("No sort method selected. You must chose either 'WIP' or 'ASSEMBLY'")
        df.reset_index(drop=True, inplace=True) 
        return df

    def extract_cstmfld(self, findstr, outputcol, df=None, readstr=r"[A-Z]*[a-z]*", uppercase=True, required=True):
        '''
        extracts a value from the cstmfld column and outputs it to another column
        '''  
        if df is None:
            df=self.df
        for i in df['cstmfld'].index:
            result = re.search(r'(?<=' + f'{findstr}' + r')' + f'{readstr}', df.at[i, 'cstmfld'])
            if result and uppercase:
                df.at[i, outputcol] = result.group(0).upper()
            elif result:
                df.at[i, outputcol] = result.group(0)
            elif required:
                raise Exception('A necessary Fishbowl custom field is either unreadable or missing information.')
        return df
    
    def clean_dates (self, df=None):
        '''
        Changes the imported date values into MM/DD/YY strings
        '''
        if df is None:
            df=self.df
        for i in df['datescheduledfulfillment'].index:
            date = datetime.strptime(df.at[i, 'datescheduledfulfillment'], '%Y-%m-%d %H:%M:%S.0')
            date = datetime.strftime(date, '%y/%m/%d')
            df.at[i, 'datescheduledfulfillment'] = date
        # df['datescheduledfufillment'].apply(lambda x: datetime.strptime(x, '%x'))
        return df

    def uppercase(self, df=None):
        '''
        Makes (almost) all string values in df uppercase. Needed for several methods to read strings correctly.
        '''
        if df is None:
            df=self.df
        for col in df.columns:
            if col == 'cstmfld' or col == 'partdescription':
                continue
            df[col] = df[col].astype(str).str.upper()
        return df
  
    def find_ticket_type(self, df=None):
        '''
        Determines the type of ticket the row belongs to and adds the value to the "ticket" column.
        e.g. "WIP part" or "Assembly"
        '''
        if df is None:
            df=self.df
        for i in df.index:
            typeid = df.at[i, 'typeid']
            cat = df.at[i, 'cat']
            if (typeid == 10 and cat == "STEEL") or (typeid == 20 and cat == "RAW"):
                ticket = "WIP"
            if (typeid == 10 and cat == "WELDMENT") or (typeid == 20 and \
                (cat == "FASTENER" or cat == "ACCESSORY" or cat == "STEEL")):
                ticket = "ASSEMBLY"
            if cat == "COMPLETE":
                ticket = "COMPLETE"
            df.at[i,'ticket'] = ticket
        return df
  
    def filter(self, typeid=None, category=None, processed=None, ticket=None, pn=None, wonum=None, df=None):
        '''
        Returns a filtered version of a dataframe. "None" arguments change nothing. Otherwise, rows with column
        values that do not match those listed in the arguments are dropped from the returned dataframe.
        '''
        def check_if_none(var):
            if var is not None:
                raise Exception(f"{var} is of the wrong data type")
        
        if df is None:
            df = self.df
        if isinstance(typeid, int) or isinstance(typeid, str):
            if typeid == 10 or str(typeid).upper() == "FINISHED" or str(typeid).upper() == "F":
                df = df.loc[df['typeid'].astype(int) == 10]
            elif typeid == 20 or str(typeid.upper()) == "RAW" or str(typeid.upper()) == "R":
                df = df.loc[df['typeid'].astype(int) == 20]
        else: check_if_none(typeid)
        if isinstance(category, str) or isinstance(category, list):
            if isinstance(category, str):
                category = [category]
            category = [val.upper() for val in category] # uppercases all items
            df = df.loc[df['cat'].isin(category)]
        else: check_if_none(category)
        if isinstance(processed, bool):
            processed = [processed]
            df = df.loc[df['processed'].isin(processed)]
        else: check_if_none(processed)
        if isinstance(ticket, str):
            ticket = [ticket.upper()]
            df = df.loc[df['ticket'].isin(ticket)]
        else: check_if_none(ticket)
        if isinstance(pn, str):
            pn = [pn]
            df = df.loc[df['bomitempart'].isin(pn)]
        else: check_if_none(pn)
        if isinstance(wonum, str) or isinstance(wonum, list):
            if isinstance(wonum, str):
                wonum = [wonum]
            df = df.loc[df['wonum'].isin(wonum)]
        else: check_if_none(wonum)
        return df
    
    def method_explained(self):
        '''
        1. Select next row where processed=false and typeid = 10
        2. Partnum becomes the "active" part.
        3. determine the ticket type (WIP or ASSEMBLY)
            If WIP:
                FINISHED GOODS:
                coalesce all rows with the same partnum where type=10 and cat=steel
                note the woitemnum(s)
                note qty per, sum qty totals
                RAW GOODS:
                coalesce all rows with the same woitemnum from before where type=20
                note qty per, sum qty totals
            If ASSEMBLY:
                FINISHED GOODS:
                coalesce all rows with the same partnum where type=10 and cat=weldment
                note the woitemnum(s)
                note qty per, sum qty totals
                RAW GOODS:
                coalesce all rows with the same woitemnum from before where type=20
                note qty per, sum qty totals
         5. Make header df by gathering:
             all wonums from before     
             earliest issue date
             current inv
             sum of all woitemtotals
        6. save headerDF, finishedDF, and rawDF to a dictionary, df_dict
        7. return this dictionary at the end of the func. access with df_dict['df_name']
             
        '''  
        
    def export_wip_info(self, df=None):
        if df is None:
            df = self.df
        df = self.filter(processed=False, ticket="WIP", df=df) # filter dataframe down to unprocessed and WIP only
        active_part = self.filter(typeid="F", df=df)['bomitempart'].iloc[0] # grabs the very first "finished goods" part from the filtered df
        fgoods = self.filter(typeid="F", pn=active_part, df=df) # finished goods dataframe. contains all instances of active_part
        wonums = fgoods['wonum'].tolist() # create a list of all work order numbers for the active_part. used to find raw.
        rgoods = self.filter(typeid="R", wonum=wonums, df=df) # raw goods dataframe. contains all raws for the wonums from active_part
        wip_dict = {
            "fgoods": fgoods,
            "rgoods": rgoods
        }
        # now we mark the rows from above as processed=true in the original dataframe
        for i in df['processed'].index:
            self.df['processed'].at[i] = True
        return wip_dict
        
    def export_assem_info(self):
        if df is None:
            df = self.df
        df = self.filter(processed=False, ticket="ASSEMBLY", df=df) # filter dataframe down to unprocessed and WIP only
        active_part = self.filter(typeid="F", df=df)['bomitempart'].iloc[0] # grabs the very first "finished goods" part from the filtered df
        fgoods = self.filter(typeid="F", pn=active_part, df=df) # finished goods dataframe. contains all instances of active_part
        wonums = fgoods['wonum'].tolist() # create a list of all work order numbers for the active_part. used to find raw.
        rgoods = self.filter(typeid="R", wonum=wonums, df=df) # raw goods dataframe. contains all raws for the wonums from active_part
        assem_dict = {
            "fgoods": fgoods,
            "rgoods": rgoods
        }
        # now we mark the rows from above as processed=true in the original dataframe
        for i in df['processed'].index:
            self.df['processed'].at[i] = True
        return assem_dict

    def moreToBeProcessed(self, ticket=None, df=None):
        '''
        This method determines if there are more tickets of a certain type to be processed.
        Ticket type can either be "WIP" or "ASSEMBLY"
        '''
        if df is None:
            df=self.df
        if ticket == "WIP":
            df = self.filter(processed=False, ticket="WIP", df=df)
            if df.empty:
                return False
            else:
                return True
        elif ticket == "ASSEMBLY":
            df = self.filter(processed=False, ticket="ASSEMBLY", df=df)
            if df.empty:
                return False
            else:
                return True
        else:
            raise Exception('Cannot determine if there are more items to be processed. Check ticket type.')
        
class Ticket():
    '''
    imports info needed for a single ticket. takes that info and formats it into a presentable PDF.
    '''
    def __init__(self, tkt_dict):
        self.fgoods = tkt_dict["fgoods"]
        self.rgoods = tkt_dict["rgoods"]
        
    def gen_header(self):
        header = {"part_num": self.fgoods['bomitempart'].iloc[0],
            "part_desc": self.fgoods['partdescription'].iloc[0],
            "wo_nums": self.fgoods['wonum'].tolist(),
            "total_qty": self.fgoods['woitemtotal'].sum(),
            "earliest_date": self.fgoods['datescheduledfulfillment'].sort_values().iloc[0],
            # "ticket_type": "WIP"
        }
    
    def fgoods(self):
        pass
    
    def rgoods(self):
        pass

# MAIN LOOP
wo = WOquery('kanban query.csv')
wo.sort_df(ticket="WIP")
while True:
    tkt = Ticket(wo.export_wip_info())
    # tkt.make_page()
    if not wo.moreToBeProcessed(ticket="WIP"):
        break
wo.sort_df(ticket="ASSEMBLY")
while True:
    tkt = Ticket(wo.export_assem_info())
    # tkt.make_page()
    if not wo.moreToBeProcessed(ticket="ASSEMBLY"):
        break
    
print('end')
print('end')



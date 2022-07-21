import re
import pandas as pd
from datetime import datetime
import time

class WOquery():
    def __init__(self, input_csv, extract_cats=True):
        self.df = pd.read_csv(input_csv, encoding='latin-1', na_filter=False) # IMPORT FISHBOWL QUERY
        self.extract_cats = extract_cats
        self.setup()
           
    def setup(self):
        # LETTER CASE CHANGES
        self.df.columns = [x.lower() for x in self.df.columns] # MAKE COLUMNS LOWERCASE
        self.df = self.uppercase_df() # MAKE STR VALUES UPPERCASE

        # FIX DATES AND NUMERIC VALUES
        for col in ('typeid','invqty', 'woitemqty', 'woitemtotal', 'qtyordered'):
            self.df[col] = pd.to_numeric(self.df[col]) 
        self.df['invqty'].fillna(value=0, inplace=True)
        self.clean_dates()
        
        # DELETE UNNECESSARY COLUMNS
        self.df.drop(self.df.columns[self.df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True, errors='ignore') # DROP BLANK COLS
        self.df.drop(columns=['bomitemdescription','itemname', 'bomitemid'], inplace=True, errors='ignore')
        if not self.extract_cats:
            self.df.drop(columns=['cstmfld'], inplace=True, errors='ignore')
        
        # CREATE SOME NEW COLUMNS
        if self.extract_cats:
            self.df['cat'] = None # MARKS CATEGORY. OBTAINED FROM CUSTOM FIELD COLUMN
            self.df['ticket'] = None
        self.df['processed'] = False # MARKS WHEN ROW HAS BEEN PROCESSED INTO A TICKET
        
        # FILL NEW COLUMNS
        if self.extract_cats:
            findstr = '"name": "Category", "type": "Drop-Down List", "value": "'
            self.extract_cstmfld(findstr, 'cat')
            self.find_ticket_types()

    def uppercase_df(self, df=None):
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
        
    def clean_dates (self):
        '''
        Changes the imported date values into MM/DD/YY strings
        '''
        col = self.df['datescheduledfulfillment']
        for i in col.index:
            date = datetime.strptime(col.at[i], '%Y-%m-%d %H:%M:%S.0')
            date = datetime.strftime(date, '%y/%m/%d')
            col.at[i] = date
        self.df['datescheduledfulfillment'] = col
        return self
      
    def find_ticket_types(self):
        '''
        Determines the type of ticket the row belongs to and adds the value to the "ticket" column.
        e.g. "WIP part" or "Assembly"
        '''
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
        self.df=df
        return self
    
    def extract_cstmfld(self, findstr, outputcol, readstr=r"[A-Z]*[a-z]*", uppercase=True, required=True):
        '''
        extracts a value from the cstmfld column and outputs it to another column
        '''  
        df=self.df
        for i in df['cstmfld'].index:
            result = re.search(r'(?<=' + f'{findstr}' + r')' + f'{readstr}', df.at[i, 'cstmfld'])
            if result and uppercase:
                df.at[i, outputcol] = result.group(0).upper()
            elif result:
                df.at[i, outputcol] = result.group(0)
            elif required:
                raise Exception('A necessary Fishbowl custom field is either unreadable or missing information.')
        self.df=df
        return self
    
    def sort_df(self, ticket=None):
        '''  
        sorts the dataframe based on the order needed for either WIP or ASSEMBLY tickets
        '''  
        if ticket == "WIP":
            self.df.sort_values(by=['partdescription','bomitempart'], axis=0, ascending=True, inplace=True)
        elif ticket == "ASSEMBLY":
            self.df.sort_values(by=['datescheduledfulfillment', 'wonum'], axis=0, ascending=True, inplace=True)
        else:
            self.df.sort_values(by=['bomitempart', 'partdescription','datescheduledfulfillment','wonum'], axis=0, ascending=True, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        return self

  
    def filter(self, typeid=None, category=None, processed=None, ticket=None, pn=None, wonum=None, df=None):
        '''
        Returns a filtered version of a dataframe. "None" arguments change nothing. Otherwise, rows with column
        values that do not match those listed in the arguments are dropped from the returned dataframe.
        '''
        if df is None:
            df = self.df
        if isinstance(typeid, int) or isinstance(typeid, str):
            if typeid == 10 or str(typeid).upper() == "FINISHED" or str(typeid).upper() == "F":
                df = df.loc[df['typeid'].astype(int) == 10]
            elif typeid == 20 or str(typeid.upper()) == "RAW" or str(typeid.upper()) == "R":
                df = df.loc[df['typeid'].astype(int) == 20]
        if isinstance(processed, bool):
            processed = [processed]
            df = df.loc[df['processed'].isin(processed)]
        if isinstance(pn, str):
            pn = [pn]
            df = df.loc[df['bomitempart'].isin(pn)]
        if isinstance(wonum, str) or isinstance(wonum, list):
            if isinstance(wonum, str):
                wonum = [wonum]
            df = df.loc[df['wonum'].isin(wonum)]
        if self.extract_cats:
            if isinstance(category, str) or isinstance(category, list):
                if isinstance(category, str):
                    category = [category]
                category = [val.upper() for val in category] # uppercases all items
                df = df.loc[df['cat'].isin(category)]
            if isinstance(ticket, str):
                ticket = [ticket.upper()]
                df = df.loc[df['ticket'].isin(ticket)]
        return df
    


    def format_fgoods(self, df):
        '''
        Returns a dictionary that gives info needed to fill out the header of a part's ticket/PDF page
        '''
        
        def reformat_date (date):
            '''
            Change date values into MM/DD/YY
            '''
            date = datetime.strptime(date, '%y/%m/%d')
            date = datetime.strftime(date, '%m/%d/%y')
            return date
        
        fg = { "part_num": df['bomitempart'].iat[0],
                    "description": df['partdescription'].iat[0],
                    "wo_nums": df['wonum'].tolist(),
                    "total_qty": df['woitemtotal'].sum(),
                    "earliest_date": reformat_date(df['datescheduledfulfillment'].sort_values().iat[0]),
                    "inventory": df['invqty'].iat[0],
                    # "ticket_type": "WIP"
        }
        return fg
    
    def format_rgoods(self, df):
        '''
        input argument is a DF comprised of all raw goods for a specific finished good from the master DF
        Coalesces the information and any duplicate rows into just one row per part
        Returns a dataframe in which each row represents a raw-good line item on that ticket/PDF page
        '''
        rg = pd.DataFrame(columns=["part_num", "description", "per", "total", "inventory"])
        rg['part_num'] = pd.Series(df['bomitempart'].unique())
        for i in rg['part_num'].index:
            pn = rg['part_num'].at[i]
            rg.at[i, 'description'] = df.loc[df['bomitempart'] == pn, 'partdescription'].iat[0]
            rg.at[i, 'per'] = df.loc[df['bomitempart'] == pn, 'woitemqty'].iat[0]
            rg.at[i, 'total'] = df.loc[df['bomitempart'] == pn, 'woitemtotal'].sum()
            rg.at[i, "inventory"] = df.loc[df['bomitempart'] == pn, 'invqty'].iat[0]
        rg.drop(columns=['index'], inplace=True, errors='ignore')
        return rg
    
    def get_ticket_info(self, ticket=None):
        '''
        when called, this finds and returns all info needed to create a single kanban ticket and then marks those rows as processed=True
        Ticket type can either be "WIP" or "ASSEMBLY"
        '''
        df = self.df
        df = self.filter(processed=False, ticket=ticket, df=df) # filter by proccessed and ticket type only
        active_part = self.filter(typeid="F", df=df)['bomitempart'].iat[0] # grab the very first item
        fgoods = self.filter(typeid="F", pn=active_part, df=df) # finished goods dataframe. contains all instances of active_part
        wonums = fgoods['wonum'].tolist() # find all "finished good" instances of active_part
        rgoods = self.filter(typeid="R", wonum=wonums, df=df) # find all the "raw good" instances for active_part
        
        for i in fgoods.index:
            self.df['processed'].at[i] = True
        for i in rgoods.index:
            self.df['processed'].at[i] = True
            
        fgoods = self.format_fgoods(fgoods)
        rgoods = self.format_rgoods(rgoods)
        
        ticket_info = {
            "fgoods": fgoods,
            "rgoods": rgoods
        }    
        return ticket_info

    def more_to_process(self, ticket=None):
        '''
        This method determines if there are more tickets of a certain type to be processed.
        Ticket type can either be "WIP" or "ASSEMBLY"
        '''
        df=self.df
        if self.extract_cats and ticket is not None:
            if ticket == "WIP":
                df = self.filter(processed=False, ticket="WIP", df=df)
                return not df.empty
            elif ticket == "ASSEMBLY":
                df = self.filter(processed=False, ticket="ASSEMBLY", df=df)
                return not df.empty
            else:
                raise Exception('Cannot determine if there are more items to be processed.')
        else:   
            df = self.filter(processed=False, df=df)
            return not df.empty
            
####################################################################################################    

class Ticket():
    '''
    imports info needed for a single ticket. takes that info and formats it into a presentable PDF.
    '''
    def __init__(self, tkt_dict):
        self.fgoods = tkt_dict["fgoods"]
        self.rgoods = tkt_dict["rgoods"]
        
   

    
####################################################################################################    
    
class KanbanTicketer():
    def __init__(self, fileloc, separate=True):
        self.file = fileloc
        self.separate = separate # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
    
    def make_packet(self, query, ticket=None):
        packet = None
        query.sort_df(ticket=ticket)
        while True:
            if not query.more_to_process(ticket=ticket):
                break
            tkt = Ticket(query.get_ticket_info(ticket=ticket))
            # tkt.makePDF() # make into a PDF page
            # tkt.addpage(packet, tkt.page) # add page to packet
        return packet

    def run(self):
        start_time = time.time()
        query = WOquery(self.file, self.separate)
        if self.separate:
            self.make_packet(query, "WIP")
            self.make_packet(query, "ASSEMBLY")
        else:
            self.make_packet(query)
        print("Process finished --- %s seconds ---" % (time.time() - start_time))


k = KanbanTicketer('KANBAN QUERY.csv')
k.run()
print('end')
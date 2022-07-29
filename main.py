from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import filedialog
from WOquery import *
from Ticket import *
import time
import os
import pyperclip
import sys

keep_going = True
mode = "Read CF"
csv_path = ""
save_dir = ""
total_items = 0
progress = 0
start_col = 0
start_row = 0

def resolve_path(path):
    '''
    copied from https://stackoverflow.com/questions/60937345/
    how-to-set-up-relative-paths-to-make-a-portable-exe-build-in-pyinstaller-with-p/
    '''
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


class FishbowlTicketer():
    def __init__(self, fileloc, mode):
        self.file = fileloc
        self.mode = mode # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
        self.position = 0
        self.step = 0
        
    def save_packet(self, ticket, packet):
        # root_dir = os.path.dirname(os.path.abspath(__file__))
        # pdf_dir = root_dir + '/PDFs/'
        # if not os.path.isdir(pdf_dir):
        #     os.mkdir(pdf_dir, 0o0777)
        if ticket is not None:
            pdf_path = save_dir + f"TICKET - {str(ticket)}.pdf"
        else:
            pdf_path = save_dir + "TICKET - ALL.pdf"
        with open(pdf_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, packet)
    
    def make_packet(self, query, ticket=None):
        merged_doc = Document()
        wip_doc = Document()
        assembly_doc = Document()
        if ticket:
            query.sort_df(ticket)
        else:
            query.sort_df("WIP")
        while True:
            global progress
            if not keep_going:
                break
            if not query.more_to_process(ticket):
                break 
            label_progress.config(text="Progress: " + "{:.2f}%".format(progress))
            progressbar.step(self.step)
            progress += self.step 
            tkt = Ticket(query.get_ticket_info(ticket))
            doc = tkt.make_PDF()
            if self.mode == "Guess":
                ticket = tkt.get_ticket()
            if ticket == "WIP":
                wip_doc.add_document(doc)
                self.save_packet(ticket, wip_doc)
            elif ticket == "ASSEMBLY":
                assembly_doc.add_document(doc)
                self.save_packet(ticket, assembly_doc)
            else:
                merged_doc.add_document(doc)
                self.save_packet(ticket, merged_doc)
                
    def run(self):
        start_time = time.time()
        print(self.mode)
        query = WOquery(self.file)
        self.step = 1 / query.get_num_of_fgoods() * 100
        if self.mode == "Read CF":
            self.make_packet(query, "ASSEMBLY")
            self.make_packet(query, "WIP")
        else:
            self.make_packet(query)
        time_ran = time.time() - start_time
        time_ran = "{:.0f}".format(time_ran)
        label_progress.config(text=f"Completed in {time_ran} secs")
        progressbar.stop()

# ---------------------------------------------------------------------------- #
# -------------------------------- app window -------------------------------- #
# ---------------------------------------------------------------------------- #

# -------------------------------- WINDOWS -------------------------------- #

# ROOT WINDOW - SETUP
root = tk.Tk()
root.title("Fishbowl Ticketer")
root.option_add("*tearOff", False)
root.geometry("300x280")

# ROOT WINDOW - LAYOUT
root.columnconfigure(0, weight=1, minsize=20)
root.rowconfigure(0, weight=1, minsize=10)
root.rowconfigure(1, weight=1, minsize=10)
root.rowconfigure(2, weight=1, minsize=10)
root.rowconfigure(3, weight=1, minsize=0)

# ROOT WINDOW - STYLE
style = ttk.Style(root)
root.tk.call('source', resolve_path('forest-dark.tcl'))
style.theme_use('forest-dark')

# FILE DIALOG - STYLE
fd = tk.Tk()
fd_Style = ttk.Style(fd)
fd_Style.theme_use('default')
fd.withdraw()

# -------------------------------- FRAMES -------------------------------- #

# GUI - FILE OPTIONS GUI
rootframe = ttk.Frame(master=root, style='Card')
rootframe.grid(row = 1, columnspan=2, padx=5, pady=5)

# GUI - RUN PROGRAM
runframe = ttk.Frame(master=root, width=200, height=100, style='Card')
runframe.grid(row=2, column=0, padx=5, pady=5)
for i in range(0,5):
    runframe.rowconfigure(i, weight=1, minsize=10)

# GUI - FOOTER
footer = ttk.Frame(master=root)
footer.grid(row=3, column=0, pady=5, sticky="S")

# -------------------------------- FUNCTIONS -------------------------------- #

def choose_save_dir():
    '''
    creates a new file dialog window that only accepts .csv
    '''
    global save_dir
    save_dir = filedialog.askdirectory(master=fd, title="Choose a save directory", 
                                       initialdir='./../')
    fd.withdraw()
    if save_dir == "":
        return None
    else:
        run_ticketer()

        
def open_csv():
    '''
    creates a new file dialog window for choosing a save dir
    '''
    global csv_path
    csv_path = filedialog.askopenfilename(master=fd, title="Choose a file", 
                filetypes=[('CSV','*.csv')], initialdir='./../')
    fd.withdraw()

mode = StringVar(rootframe)
mode.set("Read CF")
def set_mode(option):
    '''
    allows selection of items from drop down
    '''
    option = mode.get()
    
def stop_running(event):
    global keep_going
    keep_going = False
    
def run_ticketer():
    print ("run ticketer")
    print ("path: " + csv_path)
    if csv_path == "":
        return
    m = mode.get()
    k = FishbowlTicketer(fileloc=csv_path, mode=m)
    background_thread = threading.Thread(target=k.run)
    background_thread.daemon = True
    background_thread.start()
    
def copy_sql_code():
    # f = open('sql.txt', 'r')
    # sql_code = f.read()
    # f.close()
    sql_code = """
    SELECT  WO.num AS WONum, WOITEM.TYPEID,  wostatus.name AS woStatus, PART.NUM AS BOMITEMPART, 
            PART.DESCRIPTION AS PARTDESCRIPTION, COALESCE(BOMITEM.DESCRIPTION, '') AS BOMITEMDESCRIPTION, 
            (WOITEM.QTYTARGET / WO.QTYTARGET) AS WOITEMQTY, WOITEM.QTYTARGET AS WOITEMTOTAL, 
            MOITEM.DESCRIPTION AS ITEMNAME, wo.qtyOrdered, WO.dateScheduled AS dateScheduledFulfillment,
            qtyonhand.qty AS invQTY, PART.CUSTOMFIELDS AS CSTMFLD, WOITEM.ID AS BOMITEMID
            
    FROM    wo
            INNER JOIN woitem ON wo.id = woitem.woid
            INNER JOIN moitem ON woitem.moitemid = moitem.id
            LEFT JOIN qtyonhand ON woitem.partId = qtyonhand.partid
            LEFT JOIN wostatus ON wostatus.id = wo.statusid
            LEFT JOIN bomitem ON moitem.bomitemid = bomitem.id
            LEFT JOIN part ON woitem.partid = part.id

    WHERE   wo.dateScheduled BETWEEN $RANGE{Select_date_range|This week|Date}
            AND wostatus.name NOT LIKE 'FULFILLED'

    ORDER BY COALESCE(moitem.sortidinstruct, 500), TYPEID ASC, BOMITEMPART DESC"""
    print('copied')
    pyperclip.copy(sql_code)
    print( pyperclip.paste())
# -------------------------------- GUI - FILE OPTIONS -------------------------------- #

# WIDGETS
button_run = ttk.Button(master=rootframe, text="Choose File", width=25, command=open_csv)
label_mode = ttk.Label(master=rootframe, text="Separation mode:")
select_mode = ttk.OptionMenu(rootframe, mode, "Read CF", "Guess", "None", command=set_mode)

# WIDGET PLACEMENT
button_run.grid(row=start_row, column=start_col, padx=5, pady=5, columnspan=2)
label_mode.grid(row=start_row+1, column=start_col, padx=5, pady=5, sticky="w")
select_mode.config(width=7)
select_mode.grid(row=start_row+1, column=start_col+1, columnspan=2, padx=5, pady=5, sticky="e")

# -------------------------------- GUI - RUN PROGRAM -------------------------------- #
# WIDGETS
progressbar = ttk.Progressbar(runframe, value=0, length=200, mode='determinate')
label_progress = tk.Label(runframe, text=f"Progress: {str(progress)}%")
button_run = ttk.Button(master=runframe, text="Generate Tickets", style='Accent.TButton', 
                        width=25, command=choose_save_dir)

# WIDGET PLACEMENT
progressbar.grid(row=2, columnspan=4, padx=5, pady=13, )
label_progress.grid(row=1, padx=5, columnspan=3)
button_run.grid(row=3, padx=5, columnspan=2)

# -------------------------------- GUI - FOOTER -------------------------------- #

# WIDGETS
label_version = tk.Label(master=footer, text="v00.1", width=8, height=1, fg="#6e6e6e")
# get_sql_code = tk.Label(master=footer, text="SQL Code", width=12, height=1, fg="#6e6e6e")
button_sql = tk.Button(master=footer, text="SQL Code to Clipboard", width=16, command=copy_sql_code, 
                       bd=0, activebackground="#313131", fg="#6e6e6e")

# WIDGET PLACEMENT
label_version.grid(row=0, column=1)
button_sql.grid(row=0, column=0)

root.bind('<Destroy>', stop_running)
root.mainloop()
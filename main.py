from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.font_manager import is_opentype_cff_font
from sqlalchemy import true
from tkcalendar import DateEntry
from tkinter.ttk import Progressbar
import threading
from tkinter import filedialog
from WOquery import *
from Ticket import *
import time
import os

keep_going = True
mode = "Read CF"

class FishbowlTicketer():
    def __init__(self, fileloc, mode):
        self.file = fileloc
        self.mode = mode # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
        self.position = 0
        
    def get_percent(self):
        return self.position
    
    def print_current_progress(self, query):
        total = query.get_num_of_fgoods()
        progress = self.position / total
        print(f"Progress: {self.position} / {total} (" + "{:.2f}".format(progress) + ")")
        
    def save_packet(self, ticket, packet):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_dir = root_dir + '/PDFs/'
        if not os.path.isdir(pdf_dir):
            os.mkdir(pdf_dir, 0o0777)
        if ticket is not None:
            pdf_path = pdf_dir + f"{str(ticket)}.pdf"
        else:
            pdf_path = pdf_dir + "ALL.pdf"
        with open(pdf_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, packet)
    
    def make_packet(self, query, ticket=None):
        merged_doc = Document()
        wip_doc = Document()
        assembly_doc = Document()
        if ticket:
            # print(f'sorting by {ticket}')
            query.sort_df(ticket)
        else:
            query.sort_df("WIP")
        while True:
            if not keep_going:
                break
            self.print_current_progress(query)
            if not query.more_to_process(ticket):
                break  
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
            self.position += 1

    def run(self):
        start_time = time.time()
        print(self.mode)
        query = WOquery(self.file)
        total = query.get_num_of_fgoods()
        print(f"There are {total} parts")
        if self.mode == "Read CF":
            self.make_packet(query, "WIP")
            self.make_packet(query, "ASSEMBLY")
        else:
            self.make_packet(query)
        print("Process finished --- %s seconds ---" % (time.time() - start_time))

# ---------------------------------------------------------------------------- #
# -------------------------------- app window -------------------------------- #
# ---------------------------------------------------------------------------- #

global progress_percent
progress_percent = 0
csv_path=""
start_col = 0
start_row = 0

# -------------------------------- WINDOWS -------------------------------- #

# ROOT WINDOW - SETUP
root = tk.Tk()
root.title("Fishbowl Ticketer")
root.option_add("*tearOff", False)
root.geometry("300x420")

# ROOT WINDOW - LAYOUT
root.columnconfigure(0, weight=1, minsize=20)
root.rowconfigure(0, weight=1, minsize=20)
root.rowconfigure(1, weight=1, minsize=20)
root.rowconfigure(2, weight=1, minsize=10)
root.rowconfigure(3, weight=0, minsize=10)

# ROOT WINDOW - STYLE
style = ttk.Style(root)
root.tk.call('source', 'forest-dark.tcl')
style.theme_use('forest-dark')

# FILE DIALOG - STYLE
fd = tk.Tk()
fd_Style = ttk.Style(fd)
fd_Style.theme_use('default')
fd.withdraw()

# -------------------------------- FRAMES -------------------------------- #

# GUI - FILE OPTIONS GUI
rootframe = ttk.Frame(master=root, style='Card')
rootframe.grid(columnspan=2, padx=5, pady=5)

# GUI - RUN PROGRAM
runframe = ttk.Frame(master=root, width=200, height=100, style='Card')
runframe.grid(row=1, column=0, padx=5, pady=5)
for i in range(0,5):
    runframe.rowconfigure(i, weight=1, minsize=10)

# GUI - FOOTER
footer = ttk.Frame(master=root)
footer.grid(row=3, column=0, pady=5, sticky="S")

# -------------------------------- FUNCTIONS -------------------------------- #

def open_csv():
    '''
    creates a new file dialog window that only accepts .csv
    '''
    csv_path = filedialog.askopenfilename(master=fd, filetypes=[('CSV','*.csv')], initialdir='./')
    if csv_path == "":
            return
    m = mode.get()
    k = FishbowlTicketer(fileloc=csv_path, mode=m)
    background_thread = threading.Thread(target=k.run)
    background_thread.daemon = True
    background_thread.start()

mode = StringVar(rootframe)
mode.set("Read CF")
def set_mode(option):
    '''
    allows selection of items from drop down
    '''
    option = mode.get()

def print_button():
    print('BUTTON')
    
def stop_running(event):
    global keep_going
    keep_going = False

# -------------------------------- GUI - FILE OPTIONS -------------------------------- #

# WIDGETS
button_run = ttk.Button(master=rootframe, text="Choose File", width=25, command=open_csv)
label_date_start = ttk.Label(master=rootframe, text="Start date:")
label_date_end = tk.Label(master=rootframe, text="End date:")
date_start = DateEntry(master=rootframe, width=7, background='#3e5c3e', foreground='white', borderwidth=2)
date_end = DateEntry(master=rootframe, width=7, background='#3e5c3e', foreground='white', borderwidth=2)
label_mode = ttk.Label(master=rootframe, text="Split mode:")
select_mode = ttk.OptionMenu(rootframe, mode, "Read CF", "Guess", "None", command=set_mode)

# WIDGET PLACEMENT
button_run.grid(row=start_row, column=start_col, padx=5, pady=5, columnspan=2)
label_date_start.grid(row=start_row+1, column=start_col, padx=5, pady=5, sticky="w")
label_date_end.grid(row=start_row+2, column=start_col, padx=5, pady=5, sticky="w")
date_start.grid(row=start_row+1, column=start_col+1, padx=5, pady=5, sticky="e")
date_end.grid(row=start_row+2, column=start_col+1, padx=5, pady=5, sticky="e")
label_mode.grid(row=start_row+3, column=start_col, padx=5, pady=5, sticky="w")
select_mode.config(width=7)
select_mode.grid(row=start_row+3, column=start_col+1, columnspan=2, padx=5, pady=5, sticky="e")

# -------------------------------- GUI - RUN PROGRAM -------------------------------- #

# WIDGETS
progressbar = ttk.Progressbar(runframe, value=progress_percent, length=200, mode='determinate')
label_progress = tk.Label(runframe, text=f"Progress: {progress_percent}%")
button_run = ttk.Button(master=runframe, text="Generate Tickets", style='Accent.TButton', width=25)

# WIDGET PLACEMENT
progressbar.grid(row=2, columnspan=4, padx=5, pady=13, )
label_progress.grid(row=1, padx=5, columnspan=3)
button_run.grid(row=3, padx=5, columnspan=2)

# -------------------------------- GUI - FOOTER -------------------------------- #

# WIDGETS
button_run = ttk.Button(master=root, text="Save Config", width=10)
label_version = tk.Label(master=footer, text="v00.01", width=12, height=1, fg="#6e6e6e")

# WIDGET PLACEMENT
button_run.grid(row=2, padx=5, pady=5)
label_version.grid(row=0, column=0)


root.bind('<Destroy>', stop_running)
root.mainloop()
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import filedialog
from WOquery import *
from Ticket import *
from sql_code import get_code
import time
import datetime
from datetime import date
import os
import sys
from PIL import Image

running = False
keep_going = True
mode = "Read CF"
csv_path = ""
save_dir = ""
total_items = 0
progress = 0
START_COL = 0
START_ROW = 0

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
        today = date.today()
        pdf_path = save_dir + os.sep + f"{today}_TKT_"
        if ticket is not None:
            pdf_path += f"{str(ticket)}.pdf"
        else:
            pdf_path += "COMBINED.pdf"
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
        global csv_path
        global running
        if running:
            return
        if self.mode == "Select":
            label_progress.config(text="Select a separation mode")
            return
        start_time = time.time()
        running = True
        query = WOquery(self.file)
        self.step = 1 / query.get_num_of_fgoods() * 100
        if self.mode == "Read CF":
            self.make_packet(query, "ASSEMBLY")
            self.make_packet(query, "WIP")
        else:
            self.make_packet(query)
        time_ran = time.time() - start_time
        time_ran = "{:.0f}".format(time_ran)
        label_progress.config(text=f"Completed in {time_ran} sec")
        progressbar.stop()
        csv_path = ""
        running = False

# -------------------------------- TK WINDOWS -------------------------------- #

# ROOT WINDOW - SETUP
root = tk.Tk()
root.title("Brazos Ticketer")
root.option_add("*tearOff", False)
root.geometry("280x430")

# ROOT WINDOW - LAYOUT
root.columnconfigure(0, weight=1, minsize=20)
root.rowconfigure(0, weight=1, minsize=10)
root.rowconfigure(1, weight=1, minsize=10)
root.rowconfigure(2, weight=1, minsize=10)
root.rowconfigure(3, weight=1, minsize=0)

# ROOT WINDOW - STYLE
style = ttk.Style(root)
root.tk.call('source', 'forest-dark.tcl')
style.theme_use('forest-dark')

# FILE DIALOG & STYLE
fd = tk.Tk()
fd_Style = ttk.Style(fd)
fd_Style.theme_use('default')
fd.withdraw()

# -------------------------------- FRAMES -------------------------------- #

# GUI - FILE OPTIONS GUI
rootframe = ttk.Frame(master=root, style='Card')
rootframe.grid(row = 1, columnspan=2, padx=2, pady=5)

# GUI - RUN PROGRAM
runframe = ttk.Frame(master=root, width=200, height=100, style='Card')
runframe.grid(row=2, column=0, padx=5, pady=2)
for i in range(0,5):
    runframe.rowconfigure(i, weight=1, minsize=10)

# GUI - FOOTER
footerframe = ttk.Frame(master=root)
footerframe.grid(row=3, column=0, pady=5, sticky="S")

# -------------------------------- FUNCTIONS -------------------------------- #

def open_csv():
    '''
    creates a new file dialog window for choosing a save dir
    '''
    global csv_path
    csv_path = filedialog.askopenfilename(master=fd, title="Choose a file", 
                filetypes=[('CSV','*.csv')], initialdir='./../')
    fd.withdraw()

def choose_save_dir():
    '''
    creates a new file dialog window that only accepts .csv
    '''
    global save_dir
    save_dir = filedialog.askdirectory(master=fd, title="Choose a save directory", 
                                       initialdir='./../')
    fd.withdraw()

mode = StringVar(rootframe)
mode.set("Read CF")
def set_mode(option):
    '''
    allows selection of items from drop down
    '''
    option = mode.get()
    
def run_ticketer():
    global save_dir
    global csv_path
    if datetime.datetime.now() > datetime.datetime(2022, 9, 11):
        return
    if csv_path == "" or save_dir == "":
        return
    m = mode.get()
    k = FishbowlTicketer(fileloc=csv_path, mode=m)
    background_thread = threading.Thread(target=k.run)
    background_thread.daemon = True
    background_thread.start()
    
def open_sql_window():
    sql_window  = tk.Toplevel(root)
    sql_window.title("Fishbowl SQL Code")
    sql_code = get_code()
    text_sql = tk.Text(master=sql_window, width=76, height=21, padx=15, pady=10)
    text_sql.insert('end', sql_code)
    text_sql.config(state='disable')
    text_sql.pack(expand=True)

def stop_running(event):
    global keep_going
    keep_going = False
    root.destroy()
    sys.exit(0)

# -------------------------------- GUI - IMG LOGO -------------------------------- #

img = tk.PhotoImage(file="logo.png")
logo = ttk.Label(root, image=img)
logo.image = img
logo.grid(row=0, column=0, columnspan=2, padx=5, pady=5,)

# -------------------------------- GUI - FILE OPTIONS -------------------------------- #

# WIDGETS
button_choosefile = ttk.Button(master=rootframe, text="Browse Input File", width=25, command=open_csv)
button_choosedir = ttk.Button(master=rootframe, text="Browse Save Directory", width=25, command=choose_save_dir)
label_mode = ttk.Label(master=rootframe, text="Separation mode:")
mode_list = ["Select","Read CF", "Guess", "None"]
select_mode = ttk.OptionMenu(rootframe, mode, *mode_list, command=set_mode,)

# WIDGET PLACEMENT
button_choosefile.grid(row=START_ROW, column=START_COL, padx=5, pady=5, columnspan=2)
button_choosedir.grid(row=START_ROW+1, column=START_COL, padx=5, pady=5, columnspan=2)
label_mode.grid(row=START_ROW+2, column=START_COL, padx=5, pady=5, sticky="w")
select_mode.config(width=7)
select_mode.grid(row=START_ROW+2, column=START_COL+1, columnspan=2, padx=5, pady=5, sticky="e")

# -------------------------------- GUI - RUN PROGRAM -------------------------------- #
# WIDGETS
progressbar = ttk.Progressbar(runframe, value=0, length=200, mode='determinate')
label_progress = tk.Label(runframe, text=f"Progress: {str(progress)}%")
button_choosefile = ttk.Button(master=runframe, text="Generate Tickets", style='Accent.TButton', 
                        width=25, command=run_ticketer)

# WIDGET PLACEMENT
progressbar.grid(row=2, columnspan=4, padx=5, pady=13)
label_progress.grid(row=1, padx=5, columnspan=3)
button_choosefile.grid(row=3, padx=5, columnspan=2)

# -------------------------------- GUI - FOOTER -------------------------------- #

# WIDGETS
label_version = tk.Label(master=footerframe, text="v1.0", width=12, height=1, fg="#6e6e6e")
# get_sql_code = tk.Label(master=footer, text="SQL Code", width=12, height=1, fg="#6e6e6e")
button_sql = tk.Button(master=footerframe, text="SQL Code", width=12, 
                       bd=0, activebackground="#313131", fg="#6e6e6e", command=open_sql_window)

# WIDGET PLACEMENT
label_version.grid(row=0, column=1)
button_sql.grid(row=0, column=0)

# -------------------------------- MAINLOOP -------------------------------- #

root.wm_attributes('-toolwindow', 'True') # remove icon from titlebar
root.bind('<Destroy>', stop_running)
root.mainloop()
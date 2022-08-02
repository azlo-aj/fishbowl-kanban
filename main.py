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

ywin = None
xwin = None

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
    
    def update_progress(self):
        global progress
        label_progress.config(text="Progress: " + "{:.2f}%".format(progress))
        progressbar.step(self.step)
        progress += self.step
        
    def need_to_select(self):
        global csv_path
        global save_dir
        if csv_path == "":
            label_progress.config(text="Select an input file")
            return True
        if save_dir == "":
            label_progress.config(text="Select a save directory")
            return True
        if self.mode == "Select":
            label_progress.config(text="Select a separation mode")
            return True
    
    def make_packet(self, query, ticket=None):
        merged_doc = Document()
        doc1 = Document()
        doc2 = Document()
        if ticket:
            query.sort_df(ticket)
        else:
            query.sort_df("WIP")
        while True:
            if not keep_going:
                break
            if not query.more_to_process(ticket):
                break 
            self.update_progress()
            tkt = Ticket(query.get_ticket_info(ticket))
            doc = tkt.make_PDF()
            if ticket == "WIP":
                doc1.add_document(doc)
                self.save_packet(ticket, doc1)
            elif ticket == "ASSEMBLY":
                doc2.add_document(doc)
                self.save_packet(ticket, doc2)
            else:
                merged_doc.add_document(doc)
                self.save_packet(ticket, merged_doc)
                
    def guess_packet(self, query, ticket):
        doc1 = Document()
        doc2 = Document()
        query.sort_df(ticket)
        while True:
            # check if we can continue
            if not keep_going: break
            if not query.more_to_process(ticket): break
            # now let's start making a ticket
            tkt = Ticket(query.get_ticket_info(ticket))
            doc = tkt.make_PDF()
            if self.mode == "Guess":
                if tkt.get_ticket() == ticket:
                    self.update_progress()
                    doc1.add_document(doc)
                    self.save_packet(ticket, doc1)
            elif self.mode == "Read CF":
                self.update_progress()
                if ticket == "WIP":
                    doc1.add_document(doc)
                    self.save_packet(ticket, doc1)
                elif ticket == "ASSEMBLY":
                    doc2.add_document(doc)
                    self.save_packet(ticket, doc2)
            else:
                self.update_progress()
                doc1.add_document(doc)
                self.save_packet(ticket, doc1)


    def run(self):
        global csv_path
        global running
        global progress
        if running:
            return
        if self.need_to_select():
            return
        running = True
        start_time = time.time()
        progress = 0
        query = WOquery(self.file, self.mode)
        self.step = 1 / query.get_num_of_fgoods() * 100
        if self.mode == "Read CF":
            self.guess_packet(query, "ASSEMBLY")
            self.guess_packet(query, "WIP")
        if self.mode == "Guess":
            # Ticket type is guessed during get_ticket_info(), so we have to iterate through everything regardless.
            # An item is marked as "processed" after iteration (even if we didn't use it),
            # so we make a backup of the dataframe before processing anything, then process one ticket type.
            # After that, we restore the backup and process the other ticket type.
            # This allows us to sort_df() for both ticket types.
            self.guess_packet(query, "WIP")
            query.reset_processed()
            self.guess_packet(query, "ASSEMBLY")
        else:
            self.make_packet(query)
        time_ran = time.time() - start_time
        time_ran = "{:.0f}".format(time_ran)
        label_progress.config(text=f"Completed in {time_ran} sec")
        progressbar.stop()
        csv_path = ""
        running = False

# -------------------------------- TK WINDOWS -------------------------------- #
# ROOT - WINDOW
root = tk.Tk()    
root.config(relief="ridge", borderwidth=3, padx=5, pady=5)

# ROOT INITIAL SCREEN LOCATION ON RUN
ywin = int(root.winfo_screenheight()/3)
xwin = int(root.winfo_screenwidth()/2-200)
root.geometry("+%s+%s" % (xwin , ywin))

# ROOT - DRAGGING/MOVING WINDOW
lastClickX = 0
lastClickY = 0
def last_click_pos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y
def drag_window(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))
root.bind('<Button-1>', last_click_pos)
root.bind('<B1-Motion>', drag_window)

# TITLE BAR
root.overrideredirect(True)
title_bar = ttk.Frame(root)
close_button = tk.Button(master=title_bar, text="x", width=2, bd=0, activebackground="#313131", command=root.destroy)
title_bar.pack(expand=1, fill=X)
close_button.pack(side=RIGHT)

# CANVAS - WINDOW
window = tk.Canvas(root)
window.config(highlightcolor="#313131")
window.pack(expand=1, fill=BOTH)

# CANVAS - LAYOUT
window.columnconfigure(0, weight=1, minsize=20)
window.rowconfigure(0, weight=1, minsize=10)
window.rowconfigure(1, weight=1, minsize=10)
window.rowconfigure(2, weight=1, minsize=10)
window.rowconfigure(3, weight=1, minsize=0)

# CANVAS - STYLE
style = ttk.Style(window)
window.tk.call('source', 'forest-dark.tcl')
style.theme_use('forest-dark')

# FILE DIALOG & STYLE
fd = tk.Tk()
fd_Style = ttk.Style(fd)
fd_Style.theme_use('default')
fd.withdraw()

# -------------------------------- FRAMES -------------------------------- #

# GUI - FILE OPTIONS GUI
fileframe = ttk.Frame(master=window, style='Card')
fileframe.grid(row = 1, columnspan=2, padx=2, pady=5)

# GUI - RUN PROGRAM
runframe = ttk.Frame(master=window, width=200, height=100, style='Card')
runframe.grid(row=2, column=0, padx=5, pady=2)
for i in range(0,5):
    runframe.rowconfigure(i, weight=1, minsize=10)

# GUI - FOOTER
footerframe = ttk.Frame(master=window)
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

mode = StringVar(fileframe)
mode.set("Read CF")
def set_mode(option):
    '''
    allows selection of items from drop down
    '''
    option = mode.get()
    
def run_ticketer():
    global save_dir
    global csv_path
    if datetime.datetime.now() > datetime.datetime(2022, 10, 11):
        return
    if csv_path == "" or save_dir == "":
        return
    m = mode.get()
    k = FishbowlTicketer(fileloc=csv_path, mode=m)
    background_thread = threading.Thread(target=k.run)
    background_thread.daemon = True
    background_thread.start()
    
def open_sql_window():
    sql_window  = tk.Toplevel(window)
    sql_window.title("Fishbowl SQL Code")
    sql_code = get_code()
    text_sql = tk.Text(master=sql_window, width=76, height=21, padx=15, pady=10)
    text_sql.insert('end', sql_code)
    text_sql.config(state='disable')
    text_sql.pack(expand=True)

def stop_running(event):
    global keep_going
    keep_going = False
    window.destroy()
    sys.exit(0)

# -------------------------------- GUI - IMG LOGO -------------------------------- #

img = tk.PhotoImage(file="logo.png")
logo = ttk.Label(window, image=img)
logo.image = img
logo.grid(row=0, column=0, columnspan=2, padx=5, pady=5,)

# -------------------------------- GUI - FILE OPTIONS -------------------------------- #

# WIDGETS
button_choosefile = ttk.Button(master=fileframe, text="Browse Input File", width=25, command=open_csv)
button_choosedir = ttk.Button(master=fileframe, text="Browse Save Directory", width=25, command=choose_save_dir)
label_mode = ttk.Label(master=fileframe, text="Separation mode:")
mode_list = ["Select","Read CF", "Guess", "None"]
select_mode = ttk.OptionMenu(fileframe, mode, *mode_list, command=set_mode,)

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

root.bind('<Destroy>', stop_running)
root.mainloop()
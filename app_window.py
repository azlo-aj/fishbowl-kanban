from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from tkinter.ttk import Progressbar
import threading


window = tk.Tk() #creates a window
window.title("Fishbowl Ticketer")
window.option_add("*tearOff", False)
window.geometry("300x420")


style = ttk.Style(window)
window.tk.call('source', 'forest-dark.tcl')
style.theme_use('forest-dark')


window.columnconfigure(0, weight=1, minsize=20)
window.rowconfigure(0, weight=1, minsize=20)
window.rowconfigure(1, weight=1, minsize=20)
window.rowconfigure(2, weight=1, minsize=10)
window.rowconfigure(3, weight=0, minsize=10)


configframe = ttk.Frame(master=window, style='Card')
start_col = 0
start_row = 0
# configframe.columnconfigure(0, weight=1)
# configframe.columnconfigure(1, weight=1)

# mainframe.pack(fill=tk.Y, side=tk.LEFT, expand=True)
configframe.grid(columnspan=2, padx=5, pady=5)




# sideframe = tk.Frame(master=window, width=10, height=75, bg="yellow")
# sideframe.pack(fill=tk.Y, side=tk.RIGHT)



def print_button():
    print('BUTTON')

button = ttk.Button(master=configframe, text="Server Login", width=25, command=print_button)
button.grid(row=start_row, column=start_col, padx=5, pady=5, columnspan=2)



# date = tk.Label(master=mainframe, text="Select a date range for the query", height=2)
# date.grid(row=date_pos, column=0, padx=5, columnspan=2)

start_label = ttk.Label(master=configframe, text="Start date:")
start_label.grid(row=start_row+1, column=start_col, padx=5, pady=5, sticky="w")
start_date = DateEntry(master=configframe, width=7, background='#3e5c3e', foreground='white', borderwidth=2)
# start_date.config(width=8)
start_date.grid(row=start_row+1, column=start_col+1, padx=5, pady=5, sticky="e")

end_label = tk.Label(master=configframe, text="End date:")
end_label.grid(row=start_row+2, column=start_col, padx=5, pady=5, sticky="w")
end_date = DateEntry(master=configframe, width=7, background='#3e5c3e', foreground='white', borderwidth=2)
# end_date.config(width=8)
end_date.grid(row=start_row+2, column=start_col+1, padx=5, pady=5, sticky="e")


def set_mode(option):
    option = mode.get()
    print(option)
mode = StringVar(configframe)
mode.set("Read CF")
mode_label = ttk.Label(master=configframe, text="Split mode:")
mode_label.grid(row=start_row+3, column=start_col, padx=5, pady=5, sticky="w")
mode_select = ttk.OptionMenu(configframe, mode, "Read CF", "Guess", "None", command=set_mode)

mode_select.config(width=7)
mode_select.grid(row=start_row+3, column=start_col+1, columnspan=2, padx=5, pady=5, sticky="e")




runframe = ttk.Frame(master=window, width=200, height=100, style='Card')
runframe.grid(row=1, column=0, padx=5, pady=5)
for i in range(0,5):
    runframe.rowconfigure(i, weight=1, minsize=10)

progress = ttk.Progressbar(runframe, value=0, length=200, mode='determinate')
progress.grid(row=2, columnspan=4, padx=5, pady=13, )
label_count = tk.Label(runframe, text="Progress: 0%")
label_count.grid(row=1, padx=5, columnspan=3)


button = ttk.Button(master=runframe, text="Generate Tickets", style='Accent.TButton', width=25)
button.grid(row=3, padx=5, columnspan=2)



button = ttk.Button(master=window, text="Save Config", width=10)
button.grid(row=2, padx=5, pady=5)


footer = ttk.Frame(master=window)
footer.grid(row=3, column=0, pady=5, sticky="S")
version = tk.Label(master=footer, text="v00.01", width=12, height=1, fg="#6e6e6e")
version.grid(row=0, column=0)



window.mainloop()
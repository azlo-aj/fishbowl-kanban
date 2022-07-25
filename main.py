from pydoc import Doc
from WOquery import *
from Ticket import *
import time
import os

class KanbanTicketer():
    def __init__(self, fileloc, separate=True):
        self.file = fileloc
        self.separate = separate # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
        self.position = 0
    
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
            pdf_path = pdf_dir + "output.pdf"
        with open(pdf_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, packet)
        
    def make_packet(self, query, ticket=None):
        packet = Document()
        query.sort_df(ticket=ticket)
        while True:
            self.print_current_progress(query)
            if not query.more_to_process(ticket=ticket):
                break
            tkt = Ticket(query.get_ticket_info(ticket=ticket))
            doc = tkt.make_PDF() # make into a PDF page
            packet.add_document(doc)
            self.save_packet(ticket, packet)
            self.position += 1

    def run(self):
        start_time = time.time()
        query = WOquery(self.file, self.separate)
        total = query.get_num_of_fgoods()
        print(f"There are {total} parts")
        if self.separate:
            self.make_packet(query, "WIP")
            self.make_packet(query, "ASSEMBLY")
        else:
            self.make_packet(query)
        print("Process finished --- %s seconds ---" % (time.time() - start_time))

k = KanbanTicketer('KANBAN QUERY.csv')
k.run()
print('end')
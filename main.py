from WOquery import *
from Ticket import *
import time
import os

class KanbanTicketer():
    def __init__(self, fileloc, mode=None):
        self.file = fileloc
        self.mode = mode # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
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
            pdf_path = pdf_dir + "ALL.pdf"
        with open(pdf_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, packet)
    
    def make_packet(self, query, ticket=None):
        merged_doc = Document()
        wip_doc = Document()
        assembly_doc = Document()
        if ticket:
            print(f'sorting by {ticket}')
            query.sort_df(ticket)
        else:
            query.sort_df("WIP")
        while True:
            self.print_current_progress(query)
            if not query.more_to_process(ticket):
                break  
            tkt = Ticket(query.get_ticket_info(ticket))
            doc = tkt.make_PDF()
            if self.mode == "GUESS":
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
        query = WOquery(self.file, self.mode)
        total = query.get_num_of_fgoods()
        print(f"There are {total} parts")
        if self.mode == "CSTMFLD":
            self.make_packet(query, "WIP")
            self.make_packet(query, "ASSEMBLY")
        else:
            self.make_packet(query)
        print("Process finished --- %s seconds ---" % (time.time() - start_time))

k = KanbanTicketer('KANBAN QUERY.csv')
k.run()
print('end')
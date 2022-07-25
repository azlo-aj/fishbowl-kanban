from WOquery import *
from Ticket import *
import time
import sys, os

class KanbanTicketer():
    def __init__(self, fileloc, separate=True):
        self.file = fileloc
        self.separate = separate # separate into "WIP" and "ASSEMBLY" tickets. Requires properly configured cf-category in Fishbowl
    
    def make_packet(self, query, ticket=None):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_dir = root_dir + '/PDFs/'
        if not os.path.isdir(pdf_dir):
            os.mkdir(pdf_dir, 0o0777)
        packet = None
        query.sort_df(ticket=ticket)
        while True:
            if not query.more_to_process(ticket=ticket):
                break
            tkt = Ticket(query.get_ticket_info(ticket=ticket))
            tkt.make_PDF(pdf_dir) # make into a PDF page
        return packet

    def run(self):
        start_time = time.time()
        query = WOquery(self.file, self.separate)
        if self.separate:
            self.make_packet(query, "ASSEMBLY")
            self.make_packet(query, "WIP")
            
        else:
            self.make_packet(query)
        print("Process finished --- %s seconds ---" % (time.time() - start_time))


k = KanbanTicketer('KANBAN QUERY.csv')
k.run()
print('end')
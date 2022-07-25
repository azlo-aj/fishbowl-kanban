import WOquery
import Ticket
import time

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
            tkt.make_PDF() # make into a PDF page
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
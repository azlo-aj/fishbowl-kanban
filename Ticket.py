from decimal import Decimal
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.pdf import PDF
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.page.page_size import PageSize
from borb.pdf.canvas.layout.page_layout.multi_column_layout import MultiColumnLayout
import pandas as pd
from table import *
from fixed_column_width_table import FixedColumnWidthTable

DRAW_BORDER=False
m: Decimal = Decimal(5)
RGOODS_ROW_PADDING = Decimal(8)

LETTER_WIDTH = PageSize.LETTER_PORTRAIT.value[0] 
LETTER_HEIGHT = PageSize.LETTER_PORTRAIT.value[1]

class Ticket():
    def __init__(self, ticket_info):
        self.fgood = ticket_info['fgoods']
        self.rgood = ticket_info['rgoods']
        self.ticket = ticket_info['ticket']
        
        self.doc: Document = Document()
        self.raws = []
        self.page = []
        self.split_rgood()
        for x in range(0, len(self.raws)):
            self.page += [Page(LETTER_WIDTH, LETTER_HEIGHT)]
            self.doc.add_page(self.page[x])
    
    @staticmethod
    def cover_page(date_range, mo_nums):
        '''
        returns a document listing all Manufacture Order numbers
        '''
        doc = Document()
        page = Page(LETTER_WIDTH, LETTER_HEIGHT)
        doc.add_page(page)
        layout = MultiColumnLayout(page,3)
        layout.add(Paragraph("DATE RANGE:",
                    margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                    padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
                    horizontal_alignment=Alignment.CENTERED,
                    font="Helvetica-Bold",
                    font_size=Decimal(14)
                ))
        layout.add(Paragraph(f"{date_range[0]} to {date_range[1]}",
                    margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                    padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
                    horizontal_alignment=Alignment.CENTERED,
                    font="Helvetica",
                    font_size=Decimal(14)
                ))
        layout.add(Paragraph("PO Numbers:",
                    margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                    padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
                    horizontal_alignment=Alignment.CENTERED,
                    font="Helvetica-Bold",
                    font_size=Decimal(14)
                ))
        
        for mo in mo_nums:
            layout.add(Paragraph(mo,
                    margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                    padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
                    horizontal_alignment=Alignment.CENTERED,
                    font="Helvetica",
                    font_size=Decimal(14)
                ))
        return doc
            
    @staticmethod
    def num_to_str(num, place=1):
        '''
        turns int/float into a string with an appropriate decimal precision
        '''
        if num < .01:
            num += 0.01
        if place==1:
            num = "{:.1f}".format(num)
            num = num.replace('.0','')
        elif place==2:
            num = "{:.2f}".format(num)
            num = num.replace('.00','')
        else:
            num = str(num)
        return num
        
    def get_ticket(self):
        return self.ticket
    
    def wo_is_001(self):
        '''
        typically, the first work order in a manufacture order is the finished product.
        we do not want the finish products in our assembly tickets, as finished products are listed in Sales Orders.
        therefore, when in "Guess" mode, we can assume ####:001 work orders need to be dropped.
        '''
        wo_nums = self.fgood['wo_nums']
        for num in wo_nums:
            wo = str(num).split(':', 1)[1]
            if "001" in wo:
                return True

    
    def split_rgood(self):
        '''
        only 10 raw good items can fit per page.
        if there are more than 10 items, this splits the dataframe every 10 rows.
        each dataframe section is added to a list self.raws
        '''
        rg = self.rgood
        items_per_page = 8
        num_of_rows = len(rg.index)
        start_pos = 0
        while start_pos < num_of_rows:
            if start_pos >= num_of_rows:
                break
            end_pos = start_pos + items_per_page
            self.raws += [rg.iloc[start_pos:end_pos]]
            start_pos += items_per_page + 1
     
    def generate_header(self, n):
        '''
        creates header that goes on page 1 of *
        '''
       # PART NUMBER
        header_pn = Paragraph(
            self.fgood['part_num'],
            margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
            padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
            font="Helvetica-Bold",
            # vertical_alignment=Alignment.TOP,
            font_size=Decimal(24)
        )
        # PART NUMBER (if not first page)
        header_pn_cont = Paragraph(
            self.fgood['part_num'] + " (cont)",
            margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
            padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
            font="Helvetica-Bold",
            # vertical_alignment=Alignment.CENTERED,
            font_size=Decimal(24)
        )
        # PART DESCRIPTION
        header_desc = Paragraph(
            self.fgood['description'],
            margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
            padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
            # vertical_alignment=Alignment.TOP,
            font_size=Decimal(14)
        )
        # FULFILLMENT DATE
        earliest_fulfillment = Paragraph(
            "Earliest Scheduled Fulfillment: " + self.fgood['earliest_date'],
            margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
            padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
            font="Helvetica",
            # vertical_alignment=Alignment.TOP,
            font_size=Decimal(12)
        )
        # FULFILLMENT DATE
        wonums_string = "Work Orders: "
        wonums_string += str(self.fgood['wo_nums'][0])
        for num in self.fgood['wo_nums'][1:]:
            wonums_string += f", {num}"
        wonums = Paragraph(
            wonums_string,
            margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
            padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
            font="Helvetica",
            font_size=Decimal(12)
        )
        # TOTAL QTY
        header_qty = Paragraph(
            self.num_to_str(self.fgood['total_qty']),
            margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
            padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
            horizontal_alignment=Alignment.RIGHT,
            font="Helvetica-Bold",
            font_size=Decimal(28)
        )
        # INVENTORY QTY
        subheader_qtyinv = Paragraph(
            "Inventory: " + self.num_to_str(self.fgood['inventory']),
            margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
            padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
            font="Helvetica",
            horizontal_alignment=Alignment.RIGHT,
            font_size=Decimal(12)
        )
    #------------------------ HEADER - TABLES ------------------------------#

        # TOP HEADER - LEFT SECTION
        header_left = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=2,
                ) \
        .add(header_pn) \
        .add(header_desc) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # TOP HEADER - RIGHT SECTION
        header_right = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=2,
                horizontal_alignment=Alignment.RIGHT,
                # vertical_alignment = Alignment.BOTTOM
                ) \
        .add(Paragraph("QTY", horizontal_alignment=Alignment.RIGHT)) \
        .add(header_qty) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # TOP HEADER SECTION DIVIDER
        header_divider = FixedColumnWidthTable(
                number_of_columns=2,
                number_of_rows=1,
                # adjust the ratios of column widths for this FixedColumnWidthTable
                column_widths=[Decimal(4), Decimal(1)],
                # background_color=HexColor("#86CD82")
                ) \
        .add(header_left) \
        .add(header_right) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # TOP HEADER
        top_header = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=1,
                column_widths=[Decimal(1)],
                background_color=HexColor("EBEBEB")
                ) \
        .add(header_divider) \
        .set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # SUB HEADER
        sub_header_top = FixedColumnWidthTable(
                number_of_columns=2,
                number_of_rows=1,
                column_widths=[Decimal(5), Decimal(2)],
                # background_color=HexColor("#86CD82")
                ) \
        .add(earliest_fulfillment) \
        .add(subheader_qtyinv) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # SUB HEADER
        sub_header_bottom = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=1,
                column_widths=[Decimal(1)],
                # background_color=HexColor("#86CD82")
                ) \
        .add(wonums) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # SUB HEADER
        sub_header = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=2,
                column_widths=[Decimal(1)],
                # background_color=HexColor("#86CD82")
                ) \
        .add(sub_header_top) \
        .add(sub_header_bottom) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        if n == 0:
            # HEADER
            header = FixedColumnWidthTable(
                    number_of_columns=1,
                    number_of_rows=2,
                    column_widths=[Decimal(1)],
                    # background_color=HexColor("#86CD82")
                    ) \
            .add(top_header) \
            .add(sub_header) \
            .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
            .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
        else:
            header = FixedColumnWidthTable(
                    number_of_columns=1,
                    number_of_rows=2,
                    column_widths=[Decimal(1)],
                    # background_color=HexColor("#86CD82")
                    ) \
            .add(header_pn_cont) \
            .add(sub_header) \
            .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
            .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
        
    #------------------------ HEADER CONTAINER ------------------------------#

        # HEADER RECTANGLE
        header_container: Rectangle = Rectangle(
            Decimal(59),                # x: 0 + page_margin
            Decimal(792 - 59 - 100),    # y: page_height - page_margin - height_of_textbox
            Decimal(612 - 59 * 2),      # width: page_width - 2 * page_margin
            Decimal(100),               # height
        )
        # fmt: on
        # page.add_annotation(SquareAnnotation(header_container, stroke_color=HexColor("#ff0000")))
        
        header.layout(self.page[n], header_container) 
        
    def generate_body(self, n):

        def add_row(table, line_item):
            return table.add(line_item)
    
        def close_table(table):
            return  table.set_padding_on_all_cells(RGOODS_ROW_PADDING/2, Decimal(0), RGOODS_ROW_PADDING/2, Decimal(0)) \
                    .set_borders_on_all_cells(True, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) \
                    .set_border_color_on_all_cells(HexColor("EBEBEB")) 

        def fill_blank_rows(table):
            return table.add(TableCell(Paragraph("Null", font_color=HexColor("FFFFFF")), border_color= HexColor("FFFFFF")))
        
        def tbl_qty_per_total(i, df):
            # QTY PER & QTY TOTAL
            qty_inv_per_total = FixedColumnWidthTable(
                    number_of_columns=2,
                    number_of_rows=1,
                    column_widths=[Decimal(1),Decimal(1)],
                    ) \
            .add(Paragraph("PER: " + self.num_to_str(df.at[i, 'per'], 2), \
                horizontal_alignment=Alignment.LEFT)) \
            .add(Paragraph("TOTAL: " + self.num_to_str(df.at[i, 'total'], 2), \
                horizontal_alignment=Alignment.RIGHT, font="Helvetica-Bold")) \
            .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
            .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
            return qty_inv_per_total
        
        def tbl_inv_scrapped(i, df):
            if df.at[i, 'inventory'] == 0:
                stock = "N/A"
            elif df.at[i, 'inventory'] > 99:
                stock = "99"
            else:
                stock = self.num_to_str(df.at[i, 'inventory'])
            # INVENTORY AND SCRAPPED
            inv_and_scrapped = FixedColumnWidthTable(
                    number_of_columns=2,
                    number_of_rows=1,
                    column_widths=[Decimal(1),Decimal(1)],
                    ) \
            .add(Paragraph("STOCK: " + stock, \
                horizontal_alignment=Alignment.LEFT)) \
            .add(Paragraph("SCRAP: ____", horizontal_alignment=Alignment.RIGHT)) \
            .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
            .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
            return inv_and_scrapped
        
        def tbl_line_item(i, df):
            # SETS UP A LINE ITEM - CONTAINS 4 CELLS TO DESCRIBE PART INFO
            line_item = FixedColumnWidthTable(
                    number_of_columns=2,
                    number_of_rows=2,
                    column_widths=[Decimal(6),Decimal(4)],
                    ) \
            .add(Paragraph(df.at[i, 'part_num'], font="Helvetica-Bold")) \
            .add(tbl_qty_per_total(i, df)) \
            .add(Paragraph(df.at[i, 'description'])) \
            .add(tbl_inv_scrapped(i, df)) \
            .set_padding_on_all_cells(Decimal(0), Decimal(0), m/2, m*2) \
            .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
            return line_item
        
        # SETS UP 10-LINE RAW GO0DS TABLE
        tbl_raw_goods = FixedColumnWidthTable(
            number_of_columns=1,
            number_of_rows=10,
            column_widths=[Decimal(1)],
            margin_top=None,
            )
        
        # RAW GOODS TITLE BAR
        raw_goods_bar = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=1,
                # adjust the ratios of column widths for this FixedColumnWidthTable
                column_widths=[Decimal(1)],
                background_color=HexColor("EBEBEB")
                ) \
        .add(Paragraph("RAW GOODS", font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED)) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), m, Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
        
        # PAGE BODY
        tbl_body = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=2,
                # adjust the ratios of column widths for this FixedColumnWidthTable
                column_widths=[Decimal(1)],
                
                ) \
        .add(raw_goods_bar) \
        .add(tbl_raw_goods) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER)
        
        # MAIN FUNCTION    
        current_row= 0
        df = self.raws[n]
        num_of_rows = len(df)
        # write each line item
        for i in df.index:
            add_row(tbl_raw_goods, tbl_line_item(i, df))
            current_row += 1
        # now that we've listed all items, "close" the table by applying the table formatting
        close_table(tbl_raw_goods)
        # determine how much room is left in the table and fill the rest with blank rows
        for _ in range(0, 10-num_of_rows):
            fill_blank_rows(tbl_raw_goods)
                
        #------------------------ RAW GOODS CONTAINER ------------------------------#
        raw_goods_container: Rectangle = Rectangle(
            Decimal(59),                            # x: 0 + page_margin
            Decimal(84 + 50),                      # y: bottom page margin + height of footer
            Decimal(612 - 59 * 2),                  # width: page_width - 2 * page_margin
            Decimal(792 - 59- (85+50) - 165),   # height: container height -margin -footer_height -header_height
        )
        # fmt: on
        # page.add_annotation(SquareAnnotation(raw_goods_container, stroke_color=HexColor("#ff0000")))
        
        tbl_body.layout(self.page[n], raw_goods_container)
        
    def generate_footer(self, n):
        num_of_pages = len(self.raws)
        
        def handle_sign_off(n):
            if not n == 0:
                return Paragraph("Null", font_color=HexColor("FFFFFF"))
            sign = Paragraph(
                    "FINISHED BY: _____________________________________________",
                    margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                    padding_top=m, padding_left=0, padding_bottom=m, padding_right=0,
                    font="Helvetica",
                    horizontal_alignment=Alignment.CENTERED,
                    font_size=Decimal(14)
                    )
            return sign
            
        # PAGE COUNTER
        page_counter = Paragraph(
                "Page " + str(n+1) + " of " + str(num_of_pages),
                margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
                padding_top=m, padding_left=0, padding_bottom=0, padding_right=0,
                font="Helvetica",
                horizontal_alignment=Alignment.CENTERED,
                font_size=Decimal(10)
            )
    #------------------------ FOOTER ------------------------------#
        # FOOTER
        footer = FixedColumnWidthTable(
                number_of_columns=1,
                number_of_rows=2,
                # adjust the ratios of column widths for this FixedColumnWidthTable
                column_widths=[Decimal(1)],
                # background_color=HexColor("#86CD82")
                ) \
        .add(handle_sign_off(n)) \
        .add(page_counter) \
        .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
        .set_borders_on_all_cells(DRAW_BORDER, DRAW_BORDER, DRAW_BORDER, DRAW_BORDER) 
    #------------------------ RAW GOODS CONTAINER ------------------------------#
        # HEADER RECTANGLE
        footer_container: Rectangle = Rectangle(
            Decimal(59),                            # x: 0 + page_margin
            Decimal(84),                            # y: bottom page margin
            Decimal(612 - 59 * 2),                  # width: page_width - 2 * page_margin
            Decimal(50),                               # height: bottom of header container - top of footer
        )
        # fmt: on
        # page.add_annotation(SquareAnnotation(footer_container, stroke_color=HexColor("#ff0000")))
        footer.layout(self.page[n], footer_container)     

    def make_PDF(self):
        '''
        makes a ticket (PDF document) for a finished good
        '''
        for n in range(0,len(self.raws)):
            self.generate_header(n)
            self.generate_body(n)
            self.generate_footer(n)
        return self.doc
    

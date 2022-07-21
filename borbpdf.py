from re import M
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.pdf import PDF
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.annotation.square_annotation import SquareAnnotation
from borb.pdf.canvas.color.color import X11Color, HexColor
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
# from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
# from table import *

from decimal import Decimal


# DRAW TABLE BORDERS FOR DEBUGGING
draw_border=False


def main():

    # create Document
    doc: Document = Document()

    # create Page
    page: Page = Page()

    # add Page to Document
    doc.add_page(page)
    
    # define the margin/padding
    m: Decimal = Decimal(5)


    
#------------------------ INPUT VARS ------------------------------#
    
    part_num = "DZ1353"
    part_desc = "TUBE 0.19 X 2.0 X 2.0 X 132.5 BEND DRILL MITER" 
    qty_total = 101
    qty_inv = 12
    date = "7/23/22"
    
############################## HEADER ######################################################################################################
#------------------------ HEADER - ITEMS ------------------------------#

    # PART NUMBER
    header_pn = Paragraph(
        part_num,
        margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
        padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
        font="Helvetica-Bold",
        # vertical_alignment=Alignment.TOP,
        font_size=Decimal(24)
    )
    # PART DESCRIPTION
    header_desc = Paragraph(
        part_desc,
        margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
        padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
        # vertical_alignment=Alignment.TOP,
        font_size=Decimal(14)
    )
    # FULFILLMENT DATE
    earliest_fulfillment = Paragraph(
        "Earliest Scheduled Fulfillment: " + date,
        margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
        padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
        font="Helvetica",
        # vertical_alignment=Alignment.TOP,
        font_size=Decimal(12)
    )
    # TOTAL QTY
    header_qty = Paragraph(
        str(qty_total),
        margin_top=m, margin_left=m, margin_bottom=m, margin_right=m,
        padding_top=0, padding_left=0, padding_bottom=m, padding_right=0,
        horizontal_alignment=Alignment.RIGHT,
        font="Helvetica-Bold",
        font_size=Decimal(28)
    )
    # INVENTORY QTY
    subheader_qtyinv = Paragraph(
        "Inventory: " + str(qty_inv),
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
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
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
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
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
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # TOP HEADER
    top_header = FixedColumnWidthTable(
            number_of_columns=1,
            number_of_rows=1,
            column_widths=[Decimal(1)],
            background_color=HexColor("EBEBEB")
            ) \
    .add(header_divider) \
    .set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # SUB HEADER
    sub_header = FixedColumnWidthTable(
            number_of_columns=2,
            number_of_rows=1,
            column_widths=[Decimal(5), Decimal(2)],
            # background_color=HexColor("#86CD82")
            ) \
    .add(earliest_fulfillment) \
    .add(subheader_qtyinv) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
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
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
#------------------------ HEADER CONTAINER ------------------------------#

    # HEADER RECTANGLE
    header_container: Rectangle = Rectangle(
        Decimal(59),                # x: 0 + page_margin
        Decimal(848 - 84 - 100),    # y: page_height - page_margin - height_of_textbox
        Decimal(595 - 59 * 2),      # width: page_width - 2 * page_margin
        Decimal(100),               # height
    )
    # fmt: on
    # page.add_annotation(SquareAnnotation(header_container, stroke_color=HexColor("#ff0000")))
    
    header.layout(page, header_container)


############################ RAW GOODS ######################################################################################################
#------------------------ RAW GOODS ------------------------------#

    # def make_raw_goods_table(*rgoods):
    #     num_of_rows = len(rgoods)
        
    #     raw_goods_rows = FixedColumnWidthTable(
    #             number_of_columns=2,
    #             number_of_rows=num_of_rows,
    #             # adjust the ratios of column widths for this FixedColumnWidthTable
    #             column_widths=[Decimal(1)],
    #             background_color=HexColor("D9D9D9")
    #             ) \
    #     .add(Paragraph("RAW GOODS", font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED)) \
    #     .set_padding_on_all_cells(Decimal(0), Decimal(0), m, Decimal(0)) \
    #     .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # def add_row (obj):
    #     return obj.add(row_info)
    
    # INVENTORY QTY
    raw_good_entry = Paragraph(
        "Inventory: " + str(qty_inv),
        margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
        padding_top=0, padding_left=0, padding_bottom=0, padding_right=0,
        font="Helvetica",
        horizontal_alignment=Alignment.RIGHT,
        font_size=Decimal(12)
    )
    # QTY PER & QTY TOTAL
    qty_per_total = FixedColumnWidthTable(
            number_of_columns=2,
            number_of_rows=1,
            column_widths=[Decimal(1),Decimal(1)],
            ) \
    .add(Paragraph("PER: 0", horizontal_alignment=Alignment.LEFT)) \
    .add(Paragraph("TOTAL: 0", horizontal_alignment=Alignment.RIGHT)) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # SETS UP A LINE ITEM - CONTAINS 4 CELLS TO DESCRIBE PART INFO
    line_item = FixedColumnWidthTable(
            number_of_columns=2,
            number_of_rows=2,
            column_widths=[Decimal(2),Decimal(1)],
            ) \
    .add(Paragraph("RAW GOOD NUMBER", font="Helvetica-Bold")) \
    .add(qty_per_total) \
    .add(Paragraph("RAW GOOD DESCRIPTION")) \
    .add(Paragraph("SCRAPPED: ____________")) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), m, Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # SETS UP ROWS - EACH ROW CONTAINS INFO FOR A RAW GOOD
    raw_good_rows = FixedColumnWidthTable(
            number_of_columns=1,
            number_of_rows=10,
            column_widths=[Decimal(1)],
            ) \
    .add(line_item) \
        .add(line_item) \
            .add(line_item) \
                .add(line_item) \
                    .add(line_item) \
                        .add(line_item) \
                            .add(line_item) \
                                .add(line_item) \
                                    .add(line_item) \
                                        .add(line_item) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(8), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 


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
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    # RAW GOODS 
    raw_goods = FixedColumnWidthTable(
            number_of_columns=1,
            number_of_rows=2,
            # adjust the ratios of column widths for this FixedColumnWidthTable
            column_widths=[Decimal(1)],
            
            ) \
    .add(raw_goods_bar) \
    .add(raw_good_rows) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 

    
#------------------------ RAW GOODS CONTAINER ------------------------------#

    # HEADER RECTANGLE
    raw_goods_container: Rectangle = Rectangle(
        Decimal(59),                            # x: 0 + page_margin
        Decimal(84 + 50),                      # y: bottom page margin + height of footer
        Decimal(595 - 59 * 2),                  # width: page_width - 2 * page_margin
        Decimal((848 - 84 - 100) - (85+50)),   # height: bottom of header container - top of footer
    )
    # fmt: on
    # page.add_annotation(SquareAnnotation(raw_goods_container, stroke_color=HexColor("#ff0000")))
    
    raw_goods.layout(page, raw_goods_container) 
    
############################ FOOTER ######################################################################################################

    # FINISHED BY
    finished_by = Paragraph(
            "FINISHED BY: _____________________________________________",
            margin_top=0, margin_left=0, margin_bottom=0, margin_right=0,
            padding_top=m, padding_left=0, padding_bottom=m, padding_right=0,
            font="Helvetica",
            horizontal_alignment=Alignment.CENTERED,
            font_size=Decimal(14)
        )
    
    
    # PAGE COUNTER
    page_counter = Paragraph(
            "Page " + "1" + " of " + "1",
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
    .add(finished_by) \
    .add(page_counter) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 

    
#------------------------ RAW GOODS CONTAINER ------------------------------#

    # HEADER RECTANGLE
    footer_container: Rectangle = Rectangle(
        Decimal(59),                            # x: 0 + page_margin
        Decimal(84),                            # y: bottom page margin
        Decimal(595 - 59 * 2),                  # width: page_width - 2 * page_margin
        Decimal(50),                               # height: bottom of header container - top of footer
    )
    # fmt: on
    # page.add_annotation(SquareAnnotation(footer_container, stroke_color=HexColor("#ff0000")))
    
    footer.layout(page, footer_container)     
    
    
    
############################ save ##################################

    with open("output.pdf", "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)


if __name__ == "__main__":
    main()
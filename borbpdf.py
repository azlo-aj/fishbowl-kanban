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
from table import *

from decimal import Decimal


# DRAW TABLE BORDERS FOR DEBUGGING
draw_border=True 



def main():
    # create Document
    doc: Document = Document()

    # create Page
    page: Page = Page()
    
    layout: PageLayout = SingleColumnLayout(page)

    # add Page to Document
    doc.add_page(page)
    
    # define the margin/padding
    m: Decimal = Decimal(5)

    # define layout rectangle
    # fmt: off
    header_container: Rectangle = Rectangle(
        Decimal(59),                # x: 0 + page_margin
        Decimal(848 - 84 - 100),    # y: page_height - page_margin - height_of_textbox
        Decimal(595 - 59 * 2),      # width: page_width - 2 * page_margin
        Decimal(100),               # height
    )
    # fmt: on

    

    # the next line of code uses absolute positioning
    part_num = Paragraph(
        "PART NUM",
        # margin
        margin_top=m,
        margin_left=m,
        margin_bottom=m,
        margin_right=m,
        # padding
        padding_top=0,
        padding_left=0,
        padding_bottom=0,
        padding_right=0,
        vertical_alignment=Alignment.TOP,
        # border_top=True,
        # border_right=True,
        # border_bottom=True,
        # border_left=True,
        font_size=Decimal(24)
    )
    
    part_desc = Paragraph(
        "TUBE 0.19 X 2.0 X 2.0 X 132.5 BEND DRILL MITER",
        # margin
        margin_top=m,
        margin_left=m,
        margin_bottom=m,
        margin_right=m,
        # padding
        padding_top=0,
        padding_left=0,
        padding_bottom=0,
        padding_right=0,
        vertical_alignment=Alignment.TOP,
        # border_top=True,
        # border_right=True,
        # border_bottom=True,
        # border_left=True,
        font_size=Decimal(14)
    )
    
    
    header_left = FixedColumnWidthTable(
            number_of_columns=1,
            number_of_rows=2,

            ) \
    .add(part_num) \
    .add(part_desc) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    
    
    header = FixedColumnWidthTable(
            number_of_columns=2,
            number_of_rows=1,
            # adjust the ratios of column widths for this FixedColumnWidthTable
            column_widths=[Decimal(4), Decimal(1)],
            # background_color=HexColor("#86CD82")
            ) \
    .add(header_left) \
    .add(Paragraph("Ipsum")) \
    .set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0)) \
    .set_borders_on_all_cells(draw_border, draw_border, draw_border, draw_border) 
    

    
    
    
    
    
    
    header.layout(page, header_container)
    # para.layout(page, header_container)
    
    
    

    # # this is a quick hack to easily get a rectangle on the page
    # # which can be very useful for debugging
    # page.add_annotation(SquareAnnotation(header_container, stroke_color=HexColor("#ff0000")))

    # store
    with open("output.pdf", "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)


if __name__ == "__main__":
    main()
from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import SingleColumnLayout
from borb.pdf import Paragraph
from borb.pdf import PDF

TEXT = '123456789'

# create an empty Document
pdf = Document()

# add an empty Page
page = Page()
pdf.add_page(page)

# use a PageLayout (SingleColumnLayout in this case)
layout = SingleColumnLayout(page)

# add a Paragraph object
layout.add(Paragraph(TEXT, font="Times-roman"))



# store the PDF
with open('output.pdf', "wb") as pdf_file_handle:
    PDF.dumps(pdf_file_handle, pdf)

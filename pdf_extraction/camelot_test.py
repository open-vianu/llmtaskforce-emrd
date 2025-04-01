# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "camelot",
# ]
# ///
import ghostscript
import camelot
from pandas.conftest import skipna
from pdfminer.high_level import extract_text

def page_searcher(file:str):
    keywords = ["steps taken for the assessment of the product", '2. scientific discussion']  # start & end of section

    # Extract text from PDF
    file = './documents/EU-1-19-1357_public-assessment-report_20190426_20190426_kromeya-epar-public-assessment-report.pdf'
    pdf_text = extract_text(file).lower().replace('  ', ' ')  # extract text, all lower cases replace double spaces
    pages = pdf_text.split("\f")  # Pages are separated by '\f'

    # Identify the start and end pages of the steps taken for the assessment of the product
    relevant_pages = []
    last_page = None
    toc = None
    for i, page in enumerate(pages):
        if keywords[0] in page:  # if keyword on page
            if not toc:  # skip the table of contents
                toc=1
                continue
            relevant_pages.append(i + 1)  # Page numbers are 1-based in Camelot
        if keywords[1] in page:
            relevant_pages.append(i+1)
            break

    # convert to string for camelot
    s=','.join(str(x) for x in relevant_pages)
    return s

def table_reader(file):
    s = page_searcher(file)
    # read tables
    tables = camelot.read_pdf(file, pages=s)
    return tables
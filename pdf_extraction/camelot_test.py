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

def page_searcher(filepath:str):
    """

    Parameters
    ----------
    filepath: the path to the EPAR file

    Returns
    -------
    s: a string of page numbers separated by comma: "1,2,6,8"
    """
    keywords = ["steps taken for the assessment of the product", '2. scientific discussion']  # start & end of section

    # Extract text from PDF, split pages
    pdf_text = extract_text(filepath).lower().replace('  ', ' ')  # extract text, all lower cases replace double spaces
    pages = pdf_text.split("\f")  # Pages are separated by '\f'

    # Identify the start and end pages of the steps taken for the assessment of the product
    relevant_pages = []
    toc = None # table of contents
    for i, page in enumerate(pages):
        if keywords[0] in page:  # if keyword on page
            # skip the table of contents where sections are mentioned. These are always found first!
            if not toc:
                toc=1
                continue
            relevant_pages.append(i + 1)  # Append list with tables
        # if end of section (2. scientific discussion starts): break loop.
        if keywords[1] in page:
            relevant_pages.append(i+1)
            break

    # convert to string for camelot
    s=','.join(str(x) for x in relevant_pages)
    return s

def table_reader(filepath):
    """

    Parameters
    ----------
    filepath: the path to the EPAR file

    Returns
    -------
    tables: list of tables that are relevant
    """
    # Search relevant pages
    s = page_searcher(filepath)
    # Read tables using the relevant page numbers
    tables = camelot.read_pdf(filepath, pages=s)
    return tables
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
import glob
from pathlib import Path

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

def save_output(inputdir:str, outputdir:str):
    """

    Parameters
    ----------
    inputdir: The directory in which the EPARs were saved
    outputdir: The directory in which the output should be saved

    Returns
    -------
    # Nothing, just saves the output in outputs/camelot_tables
    """
    # Extract filepath
    paths = glob.glob(f"{inputdir}/*.pdf")
    # Extract filename
    files = [Path(f).name for f in glob.glob(f"{inputdir}/*.pdf")]
    # go through EPARs
    for i, f in enumerate(paths):
        tablestrings = []
        # For each EPAR extract relevant tables
        tables = table_reader(f)
        # Convert each table to strings and place in list
        for t in tables:
            tablestrings.append(t.df.to_string(index=False))
        # Convert list to string, separated by newline
        tablestring = '\n'.join(tablestrings)

        # Save
        with open(f"{outputdir}/{files[i]}.txt", "w") as outputfile:
            outputfile.write(tablestring)

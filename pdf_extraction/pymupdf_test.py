from pathlib import Path
from tqdm import tqdm


import pymupdf
import pymupdf4llm
import pandas as pd


def pymupdf_to_text(filepath: str | Path) -> str | None:
    with pymupdf.open(filepath) as pdf_document:
        try:
            text = ""
            for page in pdf_document:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error: {e}")
            return None


def pymupdf4llm_to_md(filepath: str | Path) -> str | None:
    try:
        return pymupdf4llm.to_markdown(filepath)
    except Exception as e:
        print(f"Error: {e}")
        return None


def table_extractor(
    filepath: str | Path, *args, **kwargs
) -> list[pymupdf.table.Table] | list | None:
    """
    Extract all PyMuPDF Table Objects from a PDF file using pymupdf

    Parameters
    ----------
    filepath: str
        Path to the PDF file
    *args, **kwargs:
        Arguments to be passed to the find_tables method

    Returns
    -------
    list
        List of PyMuPDF Table Objects
    """
    try:
        with pymupdf.open(filepath) as pdf_document:
            tables = []
            for page in pdf_document:
                results = page.find_tables(*args, **kwargs)
                if results.tables:
                    tables.extend(results.tables)
            return tables
    except Exception as e:
        print(f"Table extractor error: {e}")
        return None


def table_writer(tables: list[pymupdf.table.Table], out_name: str | Path):
    """
    Write all tables taken from one file to csv and markdown files

    Parameters
    ----------
    tables: list
        List of PyMuPDF Table Objects
    out_name: str
        Name of the output files

    Returns
    -------
    None
    """
    for i, table in enumerate(tables):
        df = table.to_pandas()
        df.to_csv(f"{out_name}_{i}.csv", index=False)
        md = table.to_markdown()
        with open(f"{out_name}_{i}.md", "w") as f:
            f.write(md)


def try_all(documents: str | Path, out_folder: str | Path) -> None:
    """
    Extract text and tables from all PDF files in a folder, using all available methods

    Parameters
    ----------
    documents: str
        Path to the folder containing the PDF files
    out_folder: str
        Path to the folder where the extracted text and tables should be saved

    Returns
    -------
    None
    """
    Path(out_folder).mkdir(exist_ok=True)
    Path(f"{out_folder}/p_txt").mkdir(exist_ok=True)
    Path(f"{out_folder}/p4_md").mkdir(exist_ok=True)

    for filepath in tqdm(
        Path(documents).glob("*.pdf"), total=len(list(Path(documents).glob("*.pdf")))
    ):
        outputs = {
            "p_txt": pymupdf_to_text(filepath),
            "p4_md": pymupdf4llm_to_md(filepath),
        }

        for key, output in outputs.items():
            if not output:
                with open(f"{out_folder}/error.log", "a") as f:
                    f.write(f"Error: {key} - {filepath}\n")
                continue
            with open(
                f"{out_folder}/{key}/{filepath.stem}.{key.split('_')[-1]}", "w"
            ) as f:
                f.write(output)


def main():
    input_folder = Path(__file__).parent.parent / "documents"
    output_folder = Path(__file__).parent.parent / "outputs"
    try_all(input_folder, output_folder)


if __name__ == "__main__":
    main()

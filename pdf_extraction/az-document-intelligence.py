import os
import fitz  # PyMuPDF for splitting large PDFs
import logging
import click
import json
from tqdm import tqdm
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

MAX_SIZE_MB = 50  # Azure Document Intelligence maximum file size limit
MAX_PAGES_PER_SPLIT = 10  # Number of pages per split for large PDFs

AZURE_DI_KEY=os.getenv("AZURE_DI_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AzureDocumentExtractor:
    def __init__(self, endpoint: str, key: str, model_id: str = "prebuilt-read"):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        self.model_id = model_id

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        with open(pdf_path, "rb") as file:
            poller = self.client.begin_analyze_document(
                model_id=self.model_id, document=file
            )
        result = poller.result()

        text = ""
        for paragraph in result.paragraphs:
            text += paragraph.content + "\n\n"
        return text

    def split_large_pdf(self, pdf_path: str, output_folder: str) -> list:
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count

        splits = []
        for start_page in range(0, total_pages, MAX_PAGES_PER_SPLIT):
            end_page = min(start_page + MAX_PAGES_PER_SPLIT - 1, total_pages - 1)
            split_pdf_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(pdf_path))[0]}_pages_{start_page + 1}_{end_page + 1}.pdf",
            )

            split_doc = fitz.open()
            split_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            split_doc.save(split_pdf_path)
            split_doc.close()

            splits.append(split_pdf_path)

        doc.close()
        return splits

    def extract_folder_to_markdown(
        self, input_folder: str, output_folder: str, temp_folder: str, force: bool = True
    ):
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(temp_folder, exist_ok=True)

        pdf_files = [
            os.path.join(input_folder, file)
            for file in os.listdir(input_folder)
            if file.lower().endswith(".pdf")
        ]

        errors = []

        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            filename = os.path.splitext(os.path.basename(pdf_file))[0] + ".md"
            output_path = os.path.join(output_folder, filename)

            if not force and os.path.exists(output_path):
                logging.info(f"Skipping already processed file: {os.path.basename(pdf_file)}")
                continue

            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            logging.info(f"Processing {os.path.basename(pdf_file)} (size: {file_size_mb:.2f} MB)...")

            texts = []

            try:
                doc = fitz.open(pdf_file)
                if file_size_mb > MAX_SIZE_MB or doc.page_count > MAX_PAGES_PER_SPLIT:
                    logging.info(f"Splitting large PDF: {os.path.basename(pdf_file)}")
                    split_pdfs = self.split_large_pdf(pdf_file, temp_folder)

                    for split_pdf in split_pdfs:
                        split_size_mb = os.path.getsize(split_pdf) / (1024 * 1024)
                        if split_size_mb <= MAX_SIZE_MB:
                            texts.append(self.extract_text_from_pdf(split_pdf))
                        else:
                            logging.warning(f"Skipped split part {split_pdf} due to exceeding size limit.")
                        os.remove(split_pdf)  # Clean up split PDF
                else:
                    texts.append(self.extract_text_from_pdf(pdf_file))
                doc.close()

                with open(output_path, "w", encoding="utf-8") as md_file:
                    md_file.write(f"# {os.path.basename(pdf_file)}\n\n")
                    md_file.write("\n".join(texts))

            except Exception as e:
                logging.error(f"Error processing {os.path.basename(pdf_file)}: {e}")
                errors.append({"file": os.path.basename(pdf_file), "error": str(e)})

        if errors:
            with open(os.path.join(output_folder, "error_report.json"), "w") as error_file:
                json.dump(errors, error_file, indent=2)


@click.command()
@click.option("--endpoint", default="https://auzre-di-emdr.cognitiveservices.azure.com/", help="Azure Document Intelligence endpoint.")
@click.option("--key", default=AZURE_DI_KEY, help="Azure Document Intelligence key.")
@click.option("--input_folder", default="documents", help="Input PDF folder.")
@click.option("--output_folder", default="outputs/az-di", help="Output Markdown folder.")
@click.option("--temp_folder", default="./tmp", help="Temporary folder for split PDFs.")
@click.option("--force", is_flag=True, help="Force reprocessing all PDFs.")
def main(endpoint, key, input_folder, output_folder, temp_folder, force):
    extractor = AzureDocumentExtractor(endpoint, key)
    extractor.extract_folder_to_markdown(input_folder, output_folder, temp_folder, force=force)


if __name__ == "__main__":
    main()
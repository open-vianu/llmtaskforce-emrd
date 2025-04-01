import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class AzureDocumentExtractor:
    def __init__(
        self, endpoint: str, key: str, model_id: str = "prebuilt-read"
    ):
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
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"
        return text

    def extract_folder_to_markdown(
        self, input_folder: str, output_folder: str
    ):
        os.makedirs(output_folder, exist_ok=True)

        pdf_files = [
            os.path.join(input_folder, file)
            for file in os.listdir(input_folder)
            if file.lower().endswith(".pdf")
        ]

        for pdf_file in pdf_files:
            filename = os.path.splitext(os.path.basename(pdf_file))[0] + ".md"
            output_path = os.path.join(output_folder, filename)

            print(f"Extracting {os.path.basename(pdf_file)} to {filename}...")

            text = self.extract_text_from_pdf(pdf_file)

            with open(output_path, "w", encoding="utf-8") as md_file:
                md_file.write(f"# {os.path.basename(pdf_file)}\n\n")
                md_file.write(text)


# Example usage:
if __name__ == "__main__":
    endpoint = "https://ayd-document-intelligence.cognitiveservices.azure.com/"
    key = "6BwB4qFcMtk1o6oOSXM78nAwT956IA0WRdhcyw85kbtyiRQSQZvuJQQJ99BAACI8hq2XJ3w3AAALACOGhZUO"

    extractor = AzureDocumentExtractor(endpoint, key)

    input_folder = "testing-input"
    output_folder = "testing-output"

    extractor.extract_folder_to_markdown(input_folder, output_folder)

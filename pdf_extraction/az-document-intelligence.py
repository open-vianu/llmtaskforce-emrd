import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class AzureDocumentExtractor:
    def __init__(self, endpoint: str, key: str, model_id: str = "prebuilt-read"):
        self.endpoint = endpoint
        self.key = key
        self.model_id = model_id
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

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

    def extract_text_from_folder(self, folder_path: str) -> dict:
        pdf_files = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith(".pdf")
        ]

        extracted_data = {}
        for pdf_file in pdf_files:
            print(f"Extracting {os.path.basename(pdf_file)}...")
            text = self.extract_text_from_pdf(pdf_file)
            extracted_data[os.path.basename(pdf_file)] = text

        return extracted_data


# Example usage
if __name__ == "__main__":
    endpoint = "https://<your-resource-name>.cognitiveservices.azure.com/"
    key = "<your-document-intelligence-key>"

    extractor = AzureDocumentExtractor(endpoint, key)

    folder = "path/to/your/pdf/folder"
    extracted_texts = extractor.extract_text_from_folder(folder)

    for filename, text in extracted_texts.items():
        print(f"\n===== Extracted from {filename} =====\n")
        print(text[:1000])  # Printing the first 1000 characters

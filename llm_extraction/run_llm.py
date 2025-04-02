import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
from langchain_openai import AzureChatOpenAI
import random
import click

# Load environment variables
_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))

GPT_ACCESS_KEY = os.getenv('GPT_ACCESS_KEY')
GPT_ACCESS_ENDPOINT = os.getenv('GPT_ACCESS_ENDPOINT')
GPT_ACCESS_DEPLOYMENT_NAME = os.getenv('GPT_ACCESS_DEPLOYMENT_NAME', '')
GPT_ACCESS_API_VERSION = os.getenv('GPT_ACCESS_API_VERSION', '')

llm = AzureChatOpenAI(
    deployment_name=GPT_ACCESS_DEPLOYMENT_NAME,
    api_key=GPT_ACCESS_KEY,
    azure_endpoint=GPT_ACCESS_ENDPOINT,
    api_version='2024-06-01'
)

@click.command()
@click.option('--input-path', type=str, required=True, help='Path to the input directory containing documents.')
@click.option('--output-path', type=str, required=True, help='Path to save the output CSV file.')
def process_documents(input_path, output_path):
    # Read selected codes from the file
    with open('outputs/selected_codes.txt', 'r') as file:
        selected_codes = file.read().splitlines()
        random.shuffle(selected_codes)

    selected_codes = [code.replace('/', '-') for code in selected_codes]
    print(f"Selected codes: {selected_codes}")
    print(len(selected_codes))

    doc_path = []
    code_output = []
    chmp_output = []
    prime_output = []

    for filename in os.listdir(input_path):
        code = filename.split('_')[0]
        if code in selected_codes:
            print(f"Code: {code}")

            with open('llm_extraction/prompts/chmp.txt', 'r') as file:
                chmp_prompt = file.read()

            with open('llm_extraction/prompts/prime.txt', 'r') as file:
                prime_prompt = file.read()

            if filename.endswith('.txt') or filename.endswith('.md'):
                with open(os.path.join(input_path, filename), 'r') as file:
                    sample_text = file.read()

                try:
                    chmp_prompt = chmp_prompt.replace("{sample text}", sample_text)
                    response = llm(chmp_prompt)
                    print("Response:")
                    print(response.content)
                    chmp_output.append(response.content)

                    prime_prompt = prime_prompt.replace("{sample text}", sample_text)
                    response = llm(prime_prompt)
                    print("Response:")
                    print(response.content)
                    prime_output.append(response.content)

                    code_output.append(code)
                    doc_path.append(filename)
                except Exception as e:
                    print(f"Skipping file {filename}: {e}")
                    continue

    print(len(doc_path), len(code_output), len(chmp_output), len(prime_output))

    df = pd.DataFrame({
        'doc_path': doc_path,
        'code': code_output,
        'chmp_output': chmp_output,
        'prime_output': prime_output
    })
    print(df)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Save the DataFrame to the specified output path
    df.to_csv(output_path, index=False)
    print(f"Output saved to {output_path}")

if __name__ == '__main__':
    process_documents()
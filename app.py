import os
import tempfile
import gradio as gr
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
import random
import time

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

def process_and_download(file_paths):
    logs = []

    if not file_paths or len(file_paths) == 0:
        return "❌ No files selected.", "Please upload at least one file.", "", None

    doc_path, code_output, chmp_output, prime_output = [], [], [], []

    try:
        with open('outputs/selected_codes.txt', 'r') as file:
            selected_codes = file.read().splitlines()
            selected_codes = [code.replace('/', '-') for code in selected_codes]
            random.shuffle(selected_codes)
        logs.append(f"📄 Loaded {len(selected_codes)} selected codes.")
    except Exception as e:
        return "❌ Error loading codes", str(e), "", None

    try:
        with open('llm_extraction/prompts/chmp.txt', 'r') as f:
            chmp_template = f.read()
        with open('llm_extraction/prompts/prime.txt', 'r') as f:
            prime_template = f.read()
        logs.append("📜 Loaded prompt templates.")
    except Exception as e:
        return "❌ Error loading prompts", str(e), "", None

    for i, file_path in enumerate(file_paths):
        filename = os.path.basename(file_path)
        code = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
        logs.append(f"🔍 [{i+1}/{len(file_paths)}] {filename} (code: {code})")

        if code in selected_codes and (filename.endswith('.txt') or filename.endswith('.md')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample_text = f.read()

                if not sample_text.strip():
                    logs.append(f"⚠️ Skipping {filename}: empty content.")
                    continue

                # CHMP
                try:
                    chmp_prompt = chmp_template.replace("{sample text}", sample_text)
                    chmp_response = llm.invoke(chmp_prompt).content.strip()
                except Exception as e:
                    chmp_response = "CHMP error"
                    logs.append(f"⚠️ CHMP error in {filename}: {e}")

                # PRIME
                try:
                    prime_prompt = prime_template.replace("{sample text}", sample_text)
                    prime_response = llm.invoke(prime_prompt).content.strip()
                except Exception as e:
                    prime_response = "PRIME error"
                    logs.append(f"⚠️ PRIME error in {filename}: {e}")

                code_output.append(code)
                doc_path.append(filename)
                chmp_output.append(chmp_response)
                prime_output.append(prime_response)
                logs.append(f"✅ Processed: {filename}")

            except Exception as e:
                logs.append(f"❌ Error reading {filename}: {e}")
        else:
            logs.append(f"⛔ Skipped {filename}: Code not in selected codes.")

    if not doc_path:
        return "❌ No matching documents processed.", "Selected codes didn't match any uploaded files.", "\n".join(logs), None

    df = pd.DataFrame({
        'doc_path': doc_path,
        'code': code_output,
        'chmp_output': chmp_output,
        'prime_output': prime_output
    })

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        df.to_csv(tmp.name, index=False)
        logs.append(f"📁 CSV saved: {tmp.name}")
        return "✅ Processing complete!", "", "\n".join(logs), tmp.name

# Gradio UI (no .stream, compatible across versions)
with gr.Blocks() as demo:
    gr.Markdown("# 📄 Document Processing App")
    gr.Markdown("⬆️ **Select `.txt` or `.md` files. Wait for upload to finish before processing.**")

    input_files = gr.File(label="Select Files", file_count="multiple", type="filepath")
    process_button = gr.Button("🚀 Process Documents")

    status_message = gr.Textbox(label="Status", interactive=False)
    error_message = gr.Textbox(label="Error Message", interactive=False)
    log_output = gr.Textbox(label="Processing Log", lines=20, interactive=False, show_copy_button=True)
    output_file = gr.File(label="Download CSV")

    process_button.click(
        fn=process_and_download,
        inputs=[input_files],
        outputs=[status_message, error_message, log_output, output_file]
    )

demo.launch(debug=True)

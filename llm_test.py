from dotenv import load_dotenv, find_dotenv
import os 

_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))

GPT_ACCESS_KEY = os.getenv('GPT_ACCESS_KEY')
GPT_ACCESS_ENDPOINT = os.getenv('GPT_ACCESS_ENDPOINT')
GPT_ACCESS_MODEL_NAME = os.getenv('GPT_ACCESS_MODEL_NAME', '')
GPT_ACCESS_DEPLOYMENT_NAME = os.getenv('GPT_ACCESS_DEPLOYMENT_NAME', '')
GPT_ACCESS_API_VERSION = os.getenv('GPT_ACCESS_API_VERSION', '')
SEED = int(os.getenv('INITIAL_SEED', 400))

from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    deployment_name = GPT_ACCESS_DEPLOYMENT_NAME, 
    api_key = GPT_ACCESS_KEY, 
    azure_endpoint = GPT_ACCESS_ENDPOINT,
    api_version = '2024-06-01'
    )



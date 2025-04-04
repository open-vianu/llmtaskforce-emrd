import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os 
from langchain_openai import AzureChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
import random

_ = load_dotenv(find_dotenv(raise_error_if_not_found=True))

GPT_ACCESS_KEY = os.getenv('GPT_ACCESS_KEY')
GPT_ACCESS_ENDPOINT = os.getenv('GPT_ACCESS_ENDPOINT')
GPT_ACCESS_MODEL_NAME = os.getenv('GPT_ACCESS_MODEL_NAME', '')
GPT_ACCESS_DEPLOYMENT_NAME = os.getenv('GPT_ACCESS_DEPLOYMENT_NAME', '')
GPT_ACCESS_API_VERSION = os.getenv('GPT_ACCESS_API_VERSION', '')
SEED = int(os.getenv('INITIAL_SEED', 400))


llm = AzureChatOpenAI(
    deployment_name = GPT_ACCESS_DEPLOYMENT_NAME, 
    api_key = GPT_ACCESS_KEY, 
    azure_endpoint = GPT_ACCESS_ENDPOINT,
    api_version = '2024-06-01'
    )

with open('outputs/selected_codes.txt', 'r') as file:
    selected_codes = file.read().splitlines()
    random.shuffle(selected_codes)    

selected_codes = [code.replace('/', '-') for code in selected_codes]
print (f"Selected codes: {selected_codes}")
print (len(selected_codes))

document_path = 'outputs/p4_md/'

response_schema_date = [
    ResponseSchema(name="date", description="Specify the date here the positive opinion for granting a Marketing Authorisation was issued in the format YYYY-MM-DD", type="date")]

response_schema_prime = [
    ResponseSchema(name="prime", description="Specify whether the medicine is prime or not. The allowed outputs are 'True', 'False' or 'Value not reported (available for medicines authorised from 2016-03-01 onwards)'.", type="string")]

parser_date = StructuredOutputParser.from_response_schemas(response_schema_date)
parser_prime = StructuredOutputParser.from_response_schemas(response_schema_prime)

format_instructions_date = parser_date.get_format_instructions()
format_instructions_prime = parser_prime.get_format_instructions()
print (format_instructions_date)


doc_path = []
code_output = []
chmp_output = []
prime_output = []

for filename in os.listdir(document_path):

    code = filename.split('_')[0]
    if code in selected_codes:
        print (f"Code: {code}")

        with open('llm_extraction/prompts/chmp.txt', 'r') as file:
            chmp_prompt = file.read()

        with open('llm_extraction/prompts/prime.txt', 'r') as file:
            prime_prompt = file.read()

        if filename.endswith('.txt') or filename.endswith('.md'):
            with open(os.path.join(document_path, filename), 'r') as file:
                sample_text = file.read()
                print (f"Processing file: {filename}")


    #         chmp_prompt = ChatPromptTemplate(
    #                 messages=[
    #                     SystemMessagePromptTemplate.from_template(
    #                         chmp_prompt + "\n"
    #                         "text: {input}\n"
    #                         "{format_instructions}\n"
    #                     )
    #                 ],
    #                 input_variables=["sample_text"],
    #                 partial_variables={"format_instructions": format_instructions_date}
    #             )

    # #         prompt = ChatPromptTemplate(
    # #             messages=[
    # #                 SystemMessagePromptTemplate.from_template(
    # #                     "Interprete the text and evaluate the text. "
    # #                     "sentiment: is the text in a positive, neutral or negative sentiment? "
    # #                     "subject: What subject is the text about? Use exactly one word. "
    # #                     "Just return the JSON, do not add ANYTHING, NO INTERPRETATION! "
    # #                     "text: {input}\n"
    # #                     "{format_instructions}\n"
    # #                 )
    # #             ],
    # #             input_variables=["chmp_prompt"],
    # #             partial_variables={"format_instructions": format_instructions_date},
    # )

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
            except:
                continue
        
print (len(doc_path), len(code_output), len(chmp_output), len(prime_output))

df = pd.DataFrame({
    'doc_path': doc_path,
    'code': code_output,
    'chmp_output': chmp_output,
    'prime_output': prime_output
})
print(df)

# save the dataframe to csv
df.to_csv('outputs/p4_md/selected_codes_p4md.csv', index=False)

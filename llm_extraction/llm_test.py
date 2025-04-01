import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os 
from langchain_openai import AzureChatOpenAI
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


#### With use of sample texts

# ## EU-1-09-531
# sample_text_chmp = """Steps taken for the assessment of the product
# The Rapporteur and Co-Rapporteur appointed by the CHMP were:
# Rapporteur: Tomas Salmonson Co-Rapporteur: Barbara van Zwieten-Boot
#  The application was received by the EMA on 4 May 2011.
#  Accelerated Assessment procedure was agreed-upon by CHMP on 14 April 2011.
#  The procedure started on 25 May 2011.
#  The Rapporteur's first Assessment Report was circulated to all CHMP members on 12 August 2011.
# The Co-Rapporteur's first Assessment Report was circulated to all CHMP members on 15 August

# 2011. In accordance with Article 6(3) of Regulation (EC) No 726/2004, the Rapporteur and Co-
# Rapporteur declared that they had completed their assessment report in less than 80 days.

#  During the meeting on 19-22 September 2011, the CHMP agreed on the consolidated List of
# Questions to be sent to the applicant. The final consolidated List of Questions was sent to the
# applicant on 22 September 2011.
#  The applicant submitted the responses to the CHMP consolidated List of Questions on 14 October
# 2011.
#  The Rapporteurs circulated the Joint Assessment Report on the applicant’s responses to the List of
# Questions to all CHMP members on 2 November 2011.
#  During the CHMP meeting on 14-17 November 2011, the CHMP agreed on a list of outstanding
# issues to be addressed in writing by the applicant.
#  The applicant submitted the responses to the CHMP List of Outstanding Issues on 24 November
# 2011.
#  The Rapporteurs circulated the Joint Assessment Report on the applicant’s responses to the List of
# Outstanding Issues to all CHMP members on 9 December 2011.
#  During the meeting on 12-15 December 2011, the CHMP, in the light of the overall data submitted
# and the scientific discussion within the Committee, issued a positive opinion for granting a
# Marketing Authorisation to Zelboraf on 15 December 2011."""

# with open('llm_extraction/EU-1-09-531_public-assessment-report_20090730_20090730_instanyl-epar-public-assessment-report.txt', 'r') as file:
#     sample_text_prime = file.read()

# with open('llm_extraction/EU-1-20-1496_public-assessment-report_20201125_20201125_oxlumo-epar-public-assessment-report.txt', 'r') as file:
#     sample_text_prime = file.read()

### Using text extracted from documents

with open('outputs/selected_codes.txt', 'r') as file:
    selected_codes = file.read().splitlines()
    random.shuffle(selected_codes)    

selected_codes = [code.replace('/', '-') for code in selected_codes]
print (f"Selected codes: {selected_codes}")


document_path = 'outputs/p_txt/'

# c = 0
doc_path = []
code_output = []
chmp_output = []
prime_output = []

for filename in os.listdir(document_path):

    # split the filename to get the code 
    code = filename.split('_')[0]
    if code in selected_codes:
        print (f"Code: {code}")

    code_output.append(code)

    doc_path.append(filename)

    # read the prompt file
    with open('llm_extraction/prompts/chmp.txt', 'r') as file:
        chmp_prompt = file.read()

    with open('llm_extraction/prompts/prime.txt', 'r') as file:
        prime_prompt = file.read()

    if filename.endswith('.txt'):
        with open(os.path.join(document_path, filename), 'r') as file:
            sample_text = file.read()
            print (f"Processing file: {filename}")

    
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
        
    #     c += 1

    # if c > 2:
    #     break

# create a dataframe with the results

df = pd.DataFrame({
    'doc_path': doc_path,
    'code': code_output,
    'chmp_output': chmp_output,
    'prime_output': prime_output
})
print(df)
# save the dataframe to csv
df.to_csv('outputs/p_txt/selected_codes_ptxt.csv', index=False)

# chmp_prompt = chmp_prompt.replace("{sample text}", sample_text_chmp)
# response = llm(chmp_prompt)
# print("Response:")
# print(response.content)

# prime_prompt = prime_prompt.replace("{sample text}", sample_text_prime)

# response = llm(prime_prompt)

# print("Response:")
# print(response.content)



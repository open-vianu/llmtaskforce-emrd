from dotenv import load_dotenv, find_dotenv
import os 
from langchain_openai import AzureChatOpenAI

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

## EU-1-09-531
sample_text = """Steps taken for the assessment of the product
The Rapporteur and Co-Rapporteur appointed by the CHMP were:
Rapporteur: Tomas Salmonson Co-Rapporteur: Barbara van Zwieten-Boot
 The application was received by the EMA on 4 May 2011.
 Accelerated Assessment procedure was agreed-upon by CHMP on 14 April 2011.
 The procedure started on 25 May 2011.
 The Rapporteur's first Assessment Report was circulated to all CHMP members on 12 August 2011.
The Co-Rapporteur's first Assessment Report was circulated to all CHMP members on 15 August

2011. In accordance with Article 6(3) of Regulation (EC) No 726/2004, the Rapporteur and Co-
Rapporteur declared that they had completed their assessment report in less than 80 days.

 During the meeting on 19-22 September 2011, the CHMP agreed on the consolidated List of
Questions to be sent to the applicant. The final consolidated List of Questions was sent to the
applicant on 22 September 2011.
 The applicant submitted the responses to the CHMP consolidated List of Questions on 14 October
2011.
 The Rapporteurs circulated the Joint Assessment Report on the applicant’s responses to the List of
Questions to all CHMP members on 2 November 2011.
 During the CHMP meeting on 14-17 November 2011, the CHMP agreed on a list of outstanding
issues to be addressed in writing by the applicant.
 The applicant submitted the responses to the CHMP List of Outstanding Issues on 24 November
2011.
 The Rapporteurs circulated the Joint Assessment Report on the applicant’s responses to the List of
Outstanding Issues to all CHMP members on 9 December 2011.
 During the meeting on 12-15 December 2011, the CHMP, in the light of the overall data submitted
and the scientific discussion within the Committee, issued a positive opinion for granting a
Marketing Authorisation to Zelboraf on 15 December 2011."""


prompt = f"""
You are a medical expert. Please find the date of where the positive opinion for granting a
Marketing Authorisation was issued. {sample_text}

Example 1:
Text: During the meeting on 26- 29 May 2009, the CHMP, in the light of the overall data submitted
and the scientific discussion within the Committee, issued a positive opinion for granting a Marketing Authorisation to Samsca on 28 May 2009. The applicant provided the letter of undertaking on the follow-up measures to be fulfilled post-authorisation on 20 May 2009.
Date: 2009-05-28

Example 2:
Text: During the meeting on 22 – 25 June 2009, the CHMP, in the light of the overall data submitted and the scientific discussion within the Committee, issued a positive opinion for granting a Marketing Authorisation to Topotecan Teva on 25 June 2009.
Date: 2009-06-25

Example 3:
Text: During the meeting on 20-23 July 2009, the CHMP, in the light of the overall data submitted and the scientific discussion within the Committee, issued a positive opinion for granting a Marketing Authorisation to ILARIS on 23 July 2009. The applicant provided the letter of undertaking on the specific obligations and follow-up measures to be fulfilled post-authorisation on 23 July 2009.
Date: 2009-07-23

Print only the date in YYYY-MM-DD format. Do not include any other text or explanation.
"""
response = llm(prompt)

print("Response:")
print(response.content)


import os
import pdfplumber
import openai

import pandas as pd
from pdfplumber.utils import extract_text, get_bbox_overlap, obj_to_bbox

AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2023-09-15-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-test")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://tek-internal-openai-service.openai.azure.com")
api_version = os.getenv("API_VERSION", "2023-09-15-preview")
api_key = os.getenv("API_KEY")
 



def generate_text_from_pdf(pdfname):
    print("Processing PDF: ", pdfname)
    # Open the PDF and extract pages
    textfinal = ""
    fintabledata = ""
    try:
        with pdfplumber.open(os.path.join('Upload_here', pdfname)) as pdf:
            for page in pdf.pages:
                num = page.page_number
                text = page.extract_text()  # Extract plain text
                table = page.extract_table()  # Extract tables

                cleaned_table = ""
            # Clean the table for missing values and prepare the input
                if table:
                    cleaned_table = [row for row in table if row]

                # Sending to Azure OpenAI for text generation
                    prompt = f"Convert the following table into a readable text:{cleaned_table}"

                    client = openai.AzureOpenAI(
                        api_version=api_version,
                        api_key=api_key,
                        azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    )
                    completion = client.chat.completions.create(
                        model=AZURE_OPENAI_DEPLOYMENT,
                        temperature=0.5,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                    )
                    response = completion.choices[0].message.content
                    if fintabledata == "":
                        fintabledata = response + "\n"
                    else:
                        fintabledata = fintabledata + response + "\n"
                if textfinal == "":
                    textfinal = text
                else:
                    textfinal = textfinal + text

        output_filename = os.path.join('srts', pdfname.replace('.pdf', '.txt'))
        # Move the PDF file to the 'srts' directory
        os.rename(os.path.join('Upload_here', pdfname), os.path.join('srts', pdfname))
        with open(output_filename, 'w', encoding="utf-8") as output_file:
            output_file.write(textfinal)  # Write non-table text
            output_file.write('\n\n--- Table Summary ---\n')
            output_file.write(fintabledata)  # Write table summary from Azure OpenAI

    except Exception as e:
        print(pdfname,"not a valid pdf")

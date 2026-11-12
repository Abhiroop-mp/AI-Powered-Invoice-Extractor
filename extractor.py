import pdfplumber


def extract_invoice(file):
    full_text = ""
    all_tables = []
    with pdfplumber.open(file) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text+=f'\n---Page Number {page_number}---\n'
                full_text+=text
                # print(text)
            
            tables = page.extract_tables()
            for table in tables:
                if table:
                    all_tables.append(table)
    return {
        "text": full_text,
        "tables": all_tables
    }



from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.anyapi.ai/v1"
)


def extract_details(invoice_text):
    prompt = f"""You are an AI invoice extractor, you
                 have to extract the valuable informations from the invoice.
                 You are mainly focused on the important informations including 
                 numerical values and also others.
                 please use the strict json format
                 Invoice text: 
                 {invoice_text}"""
    response = client.chat.completions.create(
        model = "google/gemini-2.5-flash-lite",#Model Name
        messages= [
            {
                "role": "user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":

    file_path = r"invoice.pdf" #Path to the PDF
    extraction = extract_invoice(file_path)

    ai_results = extract_details(
        extraction['text']
    )


    print(ai_results)
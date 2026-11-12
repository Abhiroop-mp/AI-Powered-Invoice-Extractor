import json
import os

from openpyxl import Workbook, load_workbook
from extractor import extract_invoice, extract_details

file_path = r"invoice.pdf" #Path to the PDF


data = extract_invoice(file_path)

ai_response = extract_details(data["text"])

def clean_ai_response(ai_result):

    ai_result = ai_result.strip()

    if ai_result.startswith("```json"):
        ai_result = ai_result[7:]

    elif ai_result.startswith("```"):
        ai_result = ai_result[3:]

    if ai_result.endswith("```"):
        ai_result = ai_result[:-3]

    return ai_result.strip()


clean_response = clean_ai_response(ai_response)

print("----- Response -----")
print(clean_response)


invoice_json = json.loads(clean_response)


def flatten_json(data, parent_key="", separator="_"):

    flattened = {}

    for key, value in data.items():

        if parent_key:
            new_key = f"{parent_key}{separator}{key}"
        else:
            new_key = key

        if isinstance(value, dict):

            flattened.update(
                flatten_json(
                    value,
                    new_key,
                    separator
                )
            )

        elif isinstance(value, list):
            flattened[new_key] = json.dumps(value)
        else:
            flattened[new_key] = value
    return flattened


def save_to_excel(invoice_data, file_name="invoice_data.xlsx"):
    flat_data = flatten_json(invoice_data)
    new_invoice_number = flat_data.get(
        "invoice_details_invoice_number"
    )

    if os.path.exists(file_name):
        workbook = load_workbook(file_name)
        sheet = workbook["Invoice Data"]
        headers = [
            cell.value
            for cell in sheet[1]
        ]

        invoice_column = None
        for index, header in enumerate(headers, start=1):
            if header == "invoice_details_invoice_number":
                invoice_column = index
                break

        if invoice_column and new_invoice_number:
            for row in range(2, sheet.max_row + 1):
                existing_invoice_number = sheet.cell(
                    row=row,
                    column=invoice_column
                ).value

                if existing_invoice_number == new_invoice_number:
                    print(
                        f"\nInvoice {new_invoice_number} "
                        f"already exists. Not added again."
                    )
                    return

    else:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Invoice Data"
        headers = list(flat_data.keys())
        sheet.append(headers)

    values = [
        flat_data.get(header)
        for header in headers
    ]
    sheet.append(values)
    workbook.save(file_name)
    print(
        f"\nInvoice {new_invoice_number} "
        f"saved successfully to {file_name}"
    )

save_to_excel(
    invoice_json,
    "invoice_data.xlsx"
)
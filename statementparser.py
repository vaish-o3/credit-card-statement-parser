import os
import pdfplumber
import pandas as pd
import re
import json

def extract_details(text):
    patterns = {
        "Cardholder Name": r"Name\s*[:\-]?\s*([A-Za-z\s]+)",
        "Card Last 4 Digits": r"Card\s*(?:Number|No\.?)\s*(?:X{4,}-?)*(\d{4})",
        "Billing Period": r"(?:Statement|Billing)\s*(?:Period|Cycle)\s*[:\-]?\s*([A-Za-z0-9\s\-]+)",
        "Payment Due Date": r"Payment\s*Due\s*Date\s*[:\-]?\s*(\d{1,2}\s*\w+\s*\d{4})",
        "Total Amount Due": r"Total\s*Amount\s*(?:Due|Payable)\s*[:\-]?\s*[₹Rs\.]?\s*([\d,]+\.\d{2})"
    }
    data = {}
    for key, pattern in patterns.items():
        data[key] = extract_field(pattern, text)
    return data

def extract_field(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"

folder_path = "statements"
pdf_files = [file for file in os.listdir(folder_path) if file.lower().endswith(".pdf")]

all_data = []
for file in pdf_files:
    filepath = os.path.join(folder_path, file)
    with pdfplumber.open(filepath) as pdf:
        text = "".join([page.extract_text() or "" for page in pdf.pages])
        data = extract_details(text)
        data["File Name"] = file
        all_data.append(data)
        print(f"Processed: {file}")

# Save to CSV
df = pd.DataFrame(all_data)
df.to_csv("output.csv", index=False)
print("CSV file saved as output.csv")

# Save to JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)
print("JSON file saved as output.json")

# Print summary
num_pdfs = len(all_data)
print(f"\nSummary:")
print(f"Total PDFs processed: {num_pdfs}")
for item in all_data:
    if "Not Found" in item.values():
        print(f"Missing data in: {item['File Name']}")
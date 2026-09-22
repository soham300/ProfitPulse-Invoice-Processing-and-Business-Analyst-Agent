from openai import AzureOpenAI
from DocumentInteligence import readthepdf
import sqlite3
import json
from dotenv import find_dotenv, load_dotenv
import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


# ---------------------------------------------------------
# 1. THE SHOPKEEPER CHOOSES THE BILL TYPE
# ---------------------------------------------------------
print("What kind of bill are you uploading?")
print("1. Purchase Bill (I bought inventory)")
print("2. Sales Bill (I sold items to a customer)")
user_choice = input("Enter 1 or 2: ")

if user_choice == "1":
    shopkeeper_direction = "INBOUND_PURCHASE"
    print("-> Got it. We will save this to the PURCHASES database.")
else:
    shopkeeper_direction = "OUTBOUND_SALE"
    print("-> Got it. We will save this to the SALES database.")

# ---------------------------------------------------------
# 2. SETUP BRAIN
# ---------------------------------------------------------


client = AzureOpenAI(
    azure_endpoint=os.environ.get("BRAIN_ENDPOINT"),
    api_key=os.environ.get("BRAIN_KEY"),
    api_version="2024-02-01" 
)

# ---------------------------------------------------------
# 3. SCAN DOCUMENT
# ---------------------------------------------------------
print("\nScanning document... (This takes a few seconds)")
result = readthepdf()

# ---------------------------------------------------------
# 4. INSTRUCTIONS (We tell the AI what the shopkeeper chose!)
# ---------------------------------------------------------
my_instructions = f"""
You are an expert financial auditor and data extractor for Indian Tax Invoices.
IMPORTANT: The shopkeeper has explicitly marked this document as an: {shopkeeper_direction}.
If it is an INBOUND_PURCHASE, extract the company selling the goods as the Vendor.
If it is an OUTBOUND_SALE, extract the person buying the goods as the Customer.

Carefully extract the data from the provided raw OCR text and return it EXACTLY in this JSON format.

the thing should be added as you it should like the data should be added like a date stored in sqlite3 so everything is stored in sqlite3 so put the data in the json that way not the string 


when ever there is a integer value present  in the data then you have to give that in that integer in the json in response like 
if this is present ₹ 25,000 then you have to put in the json 25000 reomve the string content and just put the integer content
### JSON SCHEMA TEMPLATE (Return ONLY this format):
{{
  "invoice_metadata": {{
    "invoice_number": null,
    "invoice_date": null,
    "due_date": null,
    "invoice_type": null
  }},
  "vendor_details": {{
    "name": null,
    "gstin": null,
    "location_state": null
  }},
  "customer_details": {{
    "name": null,
    "gstin": null,
    "location_state": null
  }},
  "line_items": [
    {{
      "product_id": null,
      "description": null,
      "hsn_code": null,
      "mrp": null,
      "quantity": null,
      "taxable_value": null,
      "gst_percentage": null,
      "tax_amount": null,
      "total_amount": null
    }}
  ],
  "financial_summary": {{
    "total_taxable_amount": null,
    "total_cgst": null,
    "total_sgst": null,
    "total_igst": null,
    "grand_total": null
  }}
}}

Here is the raw data from the document scanner:
"""

final_prompt = my_instructions + str(result)


print("Sending data to the AI Brain for formatting...")
response = client.chat.completions.create(
    model="gpt-4.1-mini",  
    messages=[{"role": "user", "content": final_prompt}]
)





print("\n--- SAVING TO DATABASE ---")

try:
    raw_text = response.choices[0].message.content
    clean_text = raw_text.replace("```json\n", "").replace("\n```", "")
    invoice_data = json.loads(clean_text)
except Exception as e:
    print("Error parsing JSON:", e)
    exit()

conn = sqlite3.connect("business_data.db")
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS Purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Invoice Meta
    invoice_number INTEGER,
    invoice_date DATE,
    due_date DATE,
    invoice_type TEXT,
    
    -- Vendor Details (Who you bought from)
    vendor_name TEXT,
    
    -- Line Item Details
    product_id INTEGER,
    description TEXT,
    mrp INTEGER,
    quantity INTEGER,
    taxable_value INTEGER,
    gst_percentage INTEGER,
    tax_amount INTEGER,
    total_amount INTEGER
    
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS  Sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Invoice Meta
    invoice_number INTEGER,
    invoice_date DATE,
    
    
    -- Customer Details (Who you sold to)
    customer_name TEXT,
    customer_address TEXT,
    
    -- Line Item Details
    product_id INTEGER,
    description TEXT,
    mrp INTEGER,
    quantity INTEGER,
    taxable_value INTEGER,
    gst_percentage INTEGER,
    tax_amount INTEGER,
    total_amount INTEGER
)
''')


conn.commit()


# 1. Extract Invoice Metadata safely
meta = invoice_data.get("invoice_metadata", {})
inv_number = meta.get("invoice_number")
inv_date = meta.get("invoice_date")
due_date = meta.get("due_date")
inv_type = meta.get("invoice_type")

line_items = invoice_data.get("line_items", [])

for item in line_items:
    # 2. Extract Line Item Data
    prod_id = item.get("product_id")
    desc = item.get("description")
    mrp = int(item.get("mrp"))
    qty = int(item.get("quantity"))
    taxable_value = int(item.get("taxable_value"))
    gst_pct = int(item.get("gst_percentage"))
    tax_amount = int(item.get("tax_amount"))
    total_amount = int(item.get("total_amount"))
    
    # 3. Route to the correct table based on Shopkeeper's choice
    if shopkeeper_direction == "INBOUND_PURCHASE":
        vendor = invoice_data.get("vendor_details", {}).get("name")
        
        # Insert 13 values into Purchases
        cursor.execute('''
            INSERT INTO Purchases 
            (invoice_number, invoice_date, due_date, invoice_type, vendor_name, 
             product_id, description, mrp, quantity, taxable_value, gst_percentage, tax_amount, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inv_number, inv_date, due_date, inv_type, vendor, 
              prod_id, desc, mrp, qty, taxable_value, gst_pct, tax_amount, total_amount))
        
        print(f"Saved Purchase: {qty}x {desc} (Total: ₹{total_amount})")
        
    elif shopkeeper_direction == "OUTBOUND_SALE":
        customer_info = invoice_data.get("customer_details", {})
        customer_name = customer_info.get("name")
        # Grab location_state and save it in the customer_address column
        customer_address = customer_info.get("location_state", "Unknown")
        
        # Insert 12 values into Sales
        cursor.execute('''
            INSERT INTO Sales 
            (invoice_number, invoice_date, customer_name, customer_address, 
             product_id, description, mrp, quantity, taxable_value, gst_percentage, tax_amount, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inv_number, inv_date, customer_name, customer_address, 
              prod_id, desc, mrp, qty, taxable_value, gst_pct, tax_amount, total_amount))
        
        print(f"Saved Sale: {qty}x {desc} (Total: ₹{total_amount})")


conn.commit()
conn.close()
print("Success! The bill was saved to the exact table you selected.")
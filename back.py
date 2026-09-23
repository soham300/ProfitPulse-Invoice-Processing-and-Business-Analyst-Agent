from flask import Flask, render_template, request, jsonify, send_file
import os
import sqlite3
import json
from datetime import datetime   
from dotenv import find_dotenv, load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from DocumentInteligence import readthepdf

path_enev = find_dotenv()
load_dotenv(path_enev)

app = Flask(__name__)

# --- AGENT SETUP ---
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME")

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

openai = project.get_openai_client(
    agent_name=AGENT_NAME
)
# Global conversation so it remembers history
conversation = openai.conversations.create()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the Drag & Drop PDF upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    invoice_type = request.form.get('invoice_type') 
    
    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)
    
    client = AzureOpenAI(
        azure_endpoint=os.environ.get("BRAIN_ENDPOINT"),
        api_key=os.environ.get("BRAIN_KEY"),
        api_version="2024-02-01" 
    )

    result = readthepdf(filepath)

    my_instructions = f"""
        You are an expert financial auditor and data extractor for Indian Tax Invoices.
        IMPORTANT: The shopkeeper has explicitly marked this document as an: {invoice_type}.
        If it is an INBOUND_PURCHASE, extract the company selling the goods as the Vendor.
        If it is an OUTBOUND_SALE, extract the person buying the goods as the Customer.

        Carefully extract the data from the provided raw OCR text and return it EXACTLY in this JSON format.
        When ever there is a integer value present in the data then you have to give that in that integer in the json in response like 
        if this is present ₹ 25,000 then you have to put in the json 25000 reomve the string content and just put the integer content
        ### JSON SCHEMA TEMPLATE (Return ONLY this format):
        {{
        "invoice_metadata": {{ "invoice_number": null, "invoice_date": null, "due_date": null, "invoice_type": null }},
        "vendor_details": {{ "name": null, "gstin": null, "location_state": null }},
        "customer_details": {{ "name": null, "gstin": null, "location_state": null }},
        "line_items": [ {{ "product_id": null, "description": null, "hsn_code": null, "mrp": null, "quantity": null, "taxable_value": null, "gst_percentage": null, "tax_amount": null, "total_amount": null }} ],
        "financial_summary": {{ "total_taxable_amount": null, "total_cgst": null, "total_sgst": null, "total_igst": null, "grand_total": null }}
        }}"""

    final_prompt = my_instructions + str(result)

    response = client.chat.completions.create(
            model="gpt-4.1-mini",  
            messages=[{"role": "user", "content": final_prompt}]
    )   
    
    try:
        raw_text = response.choices[0].message.content
        clean_text = raw_text.replace("```json\n", "").replace("\n```", "")
        invoice_data = json.loads(clean_text)
    except Exception as e:
        print("Error parsing JSON:", e)
        return jsonify({"error": "Failed to parse JSON."})

    conn = sqlite3.connect("business_data.db")
    cursor = conn.cursor()

    # Create Tables (Unchanged, exactly as you wrote it!)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number INTEGER, invoice_date DATE, due_date DATE, invoice_type TEXT, vendor_name TEXT,
        product_id INTEGER, description TEXT, mrp INTEGER, quantity INTEGER, taxable_value INTEGER,
        gst_percentage INTEGER, tax_amount INTEGER, total_amount INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number INTEGER, invoice_date DATE, customer_name TEXT, customer_address TEXT,
        product_id INTEGER, description TEXT, mrp INTEGER, quantity INTEGER, taxable_value INTEGER,
        gst_percentage INTEGER, tax_amount INTEGER, total_amount INTEGER
    )''')
    conn.commit()

    meta = invoice_data.get("invoice_metadata", {})
    inv_number = meta.get("invoice_number")
    inv_date = meta.get("invoice_date")
    due_date = meta.get("due_date")
    inv_type = meta.get("invoice_type")

    line_items = invoice_data.get("line_items", [])

    for item in line_items:
        prod_id, desc, mrp, qty = item.get("product_id"), item.get("description"), int(item.get("mrp", 0)), int(item.get("quantity", 0))
        taxable_value, gst_pct = int(item.get("taxable_value", 0)), int(item.get("gst_percentage", 0))
        tax_amount, total_amount = int(item.get("tax_amount", 0)), int(item.get("total_amount", 0))
        
        if invoice_type == "INBOUND_PURCHASE":
            vendor = invoice_data.get("vendor_details", {}).get("name")
            cursor.execute('''INSERT INTO Purchases (invoice_number, invoice_date, due_date, invoice_type, vendor_name, product_id, description, mrp, quantity, taxable_value, gst_percentage, tax_amount, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (inv_number, inv_date, due_date, inv_type, vendor, prod_id, desc, mrp, qty, taxable_value, gst_pct, tax_amount, total_amount))
            
        elif invoice_type == "OUTBOUND_SALE":
            customer_info = invoice_data.get("customer_details", {})
            customer_name = customer_info.get("name")
            customer_address = customer_info.get("location_state", "Unknown")
            cursor.execute('''INSERT INTO Sales (invoice_number, invoice_date, customer_name, customer_address, product_id, description, mrp, quantity, taxable_value, gst_percentage, tax_amount, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (inv_number, inv_date, customer_name, customer_address, prod_id, desc, mrp, qty, taxable_value, gst_pct, tax_amount, total_amount))

    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Successfully processed {invoice_type} invoice!"})

@app.route('/chat', methods=['POST'])
def chat():
    """Handles messages from the chatbot interface"""
    user_message = request.json.get("message")
    generated_file = None
    
    print(f"User: {user_message}")
    print("Agent is thinking...")
    
    # 1. Send user message to Agent (OUTER WHILE LOOP REMOVED!)
    response = openai.responses.create(
        conversation=conversation.id,
        input=user_message
    )
    agent_text = response.output_text

    # --- THE AUTOMATIC PROCESSING LOOP ---
    while True:
        # SCENARIO 1: SAVE FILE
        if "SAVE_FILE:" in agent_text:
            report_text = agent_text.split("SAVE_FILE:")[1].strip()
            today = datetime.now()
            filename = f"SalesReport_{today.strftime('%Y-%m-%d')}.txt"
            
            # SAVING TO DOWNLOADS FOLDER SO BROWSER CAN GET IT
            os.makedirs("downloads", exist_ok=True)
            path = os.path.join("downloads", filename)
            
            print(f"\n[Intern is creating {filename} on your laptop...]")
            with open(path, "w", encoding="utf-8") as file:
                file.write(report_text)
                
            generated_file = filename
            follow_up_message = f"I successfully saved {filename} to the computer. Please tell the user to click the download button below."
            
            agent_text = openai.responses.create(
                conversation=conversation.id,
                input=follow_up_message
            ).output_text

        # SCENARIO 2: SQL QUERY
        elif "{" in agent_text and "QUERY" in agent_text:
            start_index = agent_text.find('{')
            end_index = agent_text.rfind('}')
            
            if start_index != -1 and end_index != -1:
                clean_json = agent_text[start_index : end_index + 1]
                try:
                    sql_code = json.loads(clean_json)["QUERY"]
                    print(f"[Intern is running query on laptop...]")
                    conn = sqlite3.connect("business_data.db")
                    cursor = conn.cursor()
                    cursor.execute(sql_code)
                    db_result = str(cursor.fetchall())
                    conn.close()
                    
                    follow_up_message = f"I ran your query. The database returned exactly this data: {db_result}. Please give the user a friendly final answer or generate the report."
                except Exception as e:
                    follow_up_message = f"System Error: {e}. Please fix your query or JSON syntax and try again."
            else:
                follow_up_message = "System Error: I could not find the JSON block. Please output exactly { \"QUERY\": \"...\" }"
                
            agent_text = openai.responses.create(
                conversation=conversation.id,
                input=follow_up_message
            ).output_text

        # SCENARIO 3: Normal Chat
        else:
            print("\nAgent:", agent_text)
            break # Breaks the inner loop, server returns the answer!

    return jsonify({"reply": agent_text, "file_ready": generated_file})

@app.route('/download/<filename>')
def download_file(filename):
    """Sends the saved file to the user's browser for download"""
    path = os.path.join("downloads", filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
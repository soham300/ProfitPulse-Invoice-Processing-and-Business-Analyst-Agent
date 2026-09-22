from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os

# 1. SETUP SCANNER (Document Intelligence)
# IMPORTANT: You MUST get this Key from the "UnderstandInvoicetoJson" page in the standard Azure Portal.
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


document_analysis_client = DocumentAnalysisClient(
    endpoint=os.environ.get("SCANNER_ENDPOINT"),
    credential=AzureKeyCredential(os.environ.get("SCANNER_KEY"))
)

def readthepdf():
    # Make sure you have a file named exactly "sample_tax_invoice.pdf" in the exact same folder!
    with open("ChatGPT Image Sep 22, 2026, 04_49_06 PM.pdf", "rb") as my_file:
        task = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-invoice",
            document=my_file
        )
    
    result = task.result()
    return result


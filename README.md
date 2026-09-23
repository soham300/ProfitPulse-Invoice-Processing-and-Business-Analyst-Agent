🧾 InvoiceAI — Smart Business & Invoice Processing Agent
InvoiceAI is an end-to-end, AI-powered web application designed to act as a Virtual Financial Analyst for small businesses. It automates the tedious process of manual data entry by extracting structured data from invoice PDFs and stores it securely in a local database.

Beyond data extraction, InvoiceAI features an intelligent Chatbot that allows business owners to ask complex financial questions in plain English, interact with dynamic UI popups, and generate downloadable CSV reports.

✨ Key Features
📄 Automated Data Extraction: Drag and drop sales or purchase invoices. The app uses Azure Document Intelligence (OCR) to extract line items, taxes, vendor names, and totals directly into a relational SQLite database.
💬 Conversational Analytics (Text-to-SQL): Ask the AI questions like "What is my total profit?" The Agent dynamically writes and executes SQL queries against your local database to provide mathematically accurate answers based on your real data.
🎯 Dynamic UI Interception (The Carousel): If a user's question is vague, the AI outputs structured JSON. The frontend automatically intercepts this JSON and instantly renders a beautiful, step-by-step multiple-choice popup wizard on the screen.
📊 1-Click CSV Reports: Ask the AI to "Generate a sales report for my CA". The AI will compile the data from the database and trigger a downloadable .csv Excel file directly inside the chat window.
🛠️ Technology Stack
Frontend: HTML5, Vanilla JavaScript, Tailwind CSS (Featuring a modern Dark-mode Glassmorphism UI)
Backend: Python, Flask, SQLite3
AI & Cloud Services:
Azure AI Document Intelligence (For robust OCR Invoice parsing)
Azure AI Foundry (Using gpt-4.1-mini for Reasoning, Text-to-SQL, and JSON generation)
🚀 Getting Started
Prerequisites
Python 3.8+
An active Microsoft Azure account with endpoints configured for Document Intelligence and Azure OpenAI/Foundry.
Installation
Clone the repository

bash


git clone https://github.com/yourusername/InvoiceAI.git
cd InvoiceAI
Install required Python packages

bash


pip install flask python-dotenv azure-identity azure-ai-projects azure-ai-formrecognizer azure-core openai
Environment Variables Configuration Create a .env file in the root directory of the project and add your Azure credentials:

env


# Azure AI Foundry / Agent Settings
PROJECT_ENDPOINT="your_foundry_project_endpoint"
AGENT_NAME="your_agent_name"
BRAIN_ENDPOINT="your_openai_endpoint"
BRAIN_KEY="your_openai_api_key"
# Azure Document Intelligence (Scanner) Settings
SCANNER_ENDPOINT="your_document_intelligence_endpoint"
SCANNER_KEY="your_document_intelligence_key"
Initialize the Database You do not need to manually create the database. The application will automatically create business_data.db and the required Sales and Purchases tables upon your very first invoice upload.

Run the Application

bash


python app.py
Open your browser and navigate to http://localhost:5000.

💡 Usage Guide
Upload an Invoice: Drag a PDF or image into the dropzone, select whether it is a Sales or Purchase invoice, and click Process with AI Agent.
Chat with your Data: Ask the Assistant questions like "Who is my top vendor?" or "Analyze my recent sales."
Interact with Popups: If the AI needs clarification, simply answer the Multiple Choice popup that automatically appears on your screen.
Download Reports: Type "Build a sales file and save it". A download button will appear allowing you to instantly grab the .csv file for your accountant.
📝 License
This project was built for educational and demonstration purposes. Feel free to use and modify it for your own business needs!
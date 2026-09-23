# 🧾 InvoiceAI — Smart Business & Invoice Processing Agent

InvoiceAI is an end-to-end, AI-powered web application designed to act as a **Virtual Financial Analyst** for small businesses. It automates the tedious process of manual data entry by extracting structured data from invoice PDFs and storing it in a local database.

Beyond data extraction, InvoiceAI features an intelligent chatbot that allows business owners to ask complex financial questions in plain English, interact with dynamic UI popups, and generate downloadable reports.

## ✨ Key Features

### 📄 Automated Data Extraction
Drag and drop sales or purchase invoices. The application uses **Azure AI Document Intelligence (OCR)** to extract invoice information such as line items, taxes, vendor/customer details, and totals, then stores the structured data in a relational **SQLite** database.

### 💬 Conversational Analytics (Text-to-SQL)
Ask the AI questions such as:

> "What is my total profit?"

The agent dynamically generates SQL queries and executes them against the local business database to provide answers based on the stored invoice data.

### 🎯 Dynamic UI Interception (The Carousel)
If a user's question is vague or requires clarification, the AI can return structured JSON. The frontend intercepts this response and renders a step-by-step **multiple-choice popup wizard** so the user can clarify what they mean before the query is processed.

### 📊 One-Click Reports
Ask the AI to generate a business report, such as:

> "Generate a sales report for my CA."

The application retrieves the required information from the database and provides a downloadable report directly through the chat interface.

## 🛠️ Technology Stack

### Frontend
- HTML5
- Vanilla JavaScript
- Tailwind CSS
- Modern dark-mode Glassmorphism UI

### Backend
- Python
- Flask
- SQLite3

### AI & Cloud Services
- **Azure AI Document Intelligence** — invoice OCR and document analysis
- **Microsoft Azure AI Foundry** — AI agent and conversational analytics
- **GPT-4.1-mini** — reasoning, Text-to-SQL, structured JSON generation, and business insights

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- An active Microsoft Azure account
- Azure AI Document Intelligence resource with the required endpoint/key
- Azure AI Foundry project/agent configuration
- Azure OpenAI configuration required by the application

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/InvoiceAI.git
cd InvoiceAI
```

#### 2. Create and activate a virtual environment (recommended)

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install required Python packages

```bash
pip install flask python-dotenv azure-identity azure-ai-projects azure-ai-formrecognizer azure-core openai
```

## 🔐 Environment Variables

Create a `.env` file in the root directory of the project and add your Azure configuration:

```env
# Azure AI Foundry / Agent Settings
PROJECT_ENDPOINT="your_foundry_project_endpoint"
AGENT_NAME="your_agent_name"
BRAIN_ENDPOINT="your_openai_endpoint"
BRAIN_KEY="your_openai_api_key"

# Azure Document Intelligence (Scanner) Settings
SCANNER_ENDPOINT="your_document_intelligence_endpoint"
SCANNER_KEY="your_document_intelligence_key"
```

> **Security:** Never commit your `.env` file, API keys, or other Azure secrets to GitHub.

## 🗄️ Database Initialization

You do not need to manually create the database. The application automatically creates `business_data.db` and the required **Sales** and **Purchases** tables when invoice data is first processed.

## ▶️ Run the Application

```bash
python app.py
```

Then open your browser and navigate to:

**http://localhost:5000**

## 💡 Usage Guide

### 1. Upload an Invoice

Drag a PDF or supported image into the upload area, select whether it is a **Sales** or **Purchase** invoice, and process it with the AI agent.

### 2. Chat with Your Data

Ask the assistant questions such as:

- "Who is my top vendor?"
- "Analyze my recent sales."
- "What is my total profit?"

### 3. Interact with the Carousel

When the AI needs clarification, a multiple-choice popup appears automatically. Select the relevant options and submit your answers to continue the analysis.

### 4. Download Reports

Ask the assistant to build a business report. When a report is generated, a download option appears inside the chat interface.

## 🔄 Application Workflow

```text
Invoice Upload
      ↓
Azure AI Document Intelligence
      ↓
Structured Invoice Data
      ↓
SQLite Database
      ↓
Microsoft Foundry AI Agent
      ↓
Natural-Language Question
      ↓
Clarification Carousel (when required)
      ↓
Text-to-SQL Query
      ↓
Database Result
      ↓
AI-Generated Business Insight / Report
```

## 📝 License

This project was built for **educational and demonstration purposes**. Feel free to use and modify it for your own business needs.
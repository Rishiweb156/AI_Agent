# Multi-Agent AI System for Document Processing

This project implements a multi-agent AI system that accepts input in PDF, JSON, or Email (text) format, classifies the format and intent, and routes it to the appropriate agent. The system maintains a shared context to enable chaining and traceability.

## System Overview

The system consists of:

1.  **Classifier Agent**:
    * Receives raw file/email/JSON.
    * Classifies format (PDF / JSON / Email) and intent (Invoice, RFQ, Complaint, etc.) using heuristics and an LLM.
    * Routes to the correct specialized agent.
    * Logs its findings to shared memory.
2.  **JSON Agent**:
    * Accepts structured JSON payloads.
    * Extracts/reformats data based on a target schema (defined for some intents).
    * Flags anomalies or missing fields.
3.  **Email Agent**:
    * Accepts email content (as text).
    * Extracts sender, refines intent, and estimates urgency (using LLM/heuristics).
    * Formats extracted information for CRM-style usage (LLM-powered extraction for specific details).
4.  **Shared Memory Module**:
    * A lightweight in-memory store (Python dictionary in this version).
    * Stores source, type, timestamp, extracted values, and a unique processing ID for each input.
    * Accessible across agents for context and logging.

## Folder Structure

multi_agent_system/
│
├── agents/                 # Core agent logic
│   ├── __init__.py
│   ├── classifier_agent.py
│   ├── json_agent.py
│   └── email_agent.py



│
├── memory/                 # Shared memory module
│   ├── __init__.py
│   └── shared_memory.py
│


├── llm_utils/              # Utilities for LLM interaction
│   ├── __init__.py
│   └── llm_client.py
│


├── input_samples/          # Sample input files (create this directory)
│   ├── invoice_sample.json
│   ├── rfq_sample.eml
│   ├── complaint_sample.txt
│   └── sample.pdf          # (You need to add an actual PDF here)
│


├── main.py                 # Main script to run the system/demo
├── requirements.txt        # Python dependencies
└── README.md               # This file

## Prerequisites

* Python new versio
* An OpenAI API key (if using the OpenAI LLM client). Set the `OPENAI_API_KEY` environment variable.
* Deleted .env file in that file we can have the openai key 
    ```bash
    export OPENAI_API_KEY="your_actual_api_key"
    ```
The current LLM calls are **placeholders** and need to be fully implemented.

## Setup
1.  **Clone the repository (or create files locally):**
    ```bash
    # git clone ... 
    # Or manually create the directory structure and files.
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd multi_agent_system
    ```
3.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    You might need to install `python-magic` dependency separately depending on your OS (e.g., `sudo apt-get install libmagic1` on Debian/Ubuntu). For Windows, `pip install python-magic-bin` might work.

5.  **Add Sample Files:**
    Create an `input_samples` directory within `multi_agent_system` and add your sample files:
    * `invoice_sample.json`
    * `rfq_sample.eml` (or `.txt`)
    * `complaint_sample.txt`
    * `sample.pdf` (any text-based PDF)
    The `main.py` script will attempt to create minimal versions of some of these if they are missing, but a real `sample.pdf` is required.

## How to Run
Execute the main script:
```bash
python main.py

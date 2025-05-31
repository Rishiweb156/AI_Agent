import os
import json 
from agents.classifier_agent import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent
from memory.shared_memory import shared_memory_instance 
def main():
    print("--- Multi-Agent AI System Demo ---")

    # Initialize agents (they use global instances of LLM client and memory for simplicity here)
    classifier = ClassifierAgent()
    json_agent = JSONAgent()
    email_agent = EmailAgent()

    #Directory for sample inputs
    sample_dir = "input_samples"

    #If input_samples directory does not exists,informs the user.
    if not os.path.exists(sample_dir):
        print(f"Error: The '{sample_dir}' directory does not exist.")
        print("Please create this directory and place your sample files (invoice_sample.json, rfq_sample.eml, complaint_sample.txt, sample.pdf) inside it.")
        return # Exit if the directory isn't there

    print(f"Using sample files from: {sample_dir}\n")

    # --- Define Inputs ---

    inputs_to_process = [
        (os.path.join(sample_dir, "invoice_sample.json"), "Invoice File"),
        (os.path.join(sample_dir, "rfq_sample.eml"), "RFQ Email File"),
        (os.path.join(sample_dir, "complaint_sample.txt"), "Complaint Text File"),
        # Example of raw JSON string input:
        ('{"order_id": "ORD-XYZ", "customer_details": {"name": "Raw JSON Test Inc.", "email": "test@raw.com"}, "items_ordered": [{"sku": "SKU005", "quantity": 1}], "status": "Pending Review"}', "Raw JSON Order Data"),
        # Example of raw email string input:
        ("From: noreply@example.com\nSubject: General Inquiry\n\nHello, I have a question about your services. Can you tell me more about topic Z?", "Raw Email Inquiry"),
        (os.path.join(sample_dir, "sample.pdf"), "PDF Document File") 
    ]

    all_processing_ids = []

    for input_data, source_hint in inputs_to_process:
        print(f"\n--- Processing Input: {source_hint} ---")
        if isinstance(input_data, str) and os.path.exists(input_data):
            print(f"File: {input_data}")
        elif isinstance(input_data, str):
            print(f"Raw Content Preview: {input_data[:100]}...")


        # 1. Classifier Agent
        processing_id, detected_format, classified_intent, content_or_path = classifier.classify_and_route(input_data, source_hint)
        all_processing_ids.append(processing_id)

        print(f"Classifier Output - ID: {processing_id}, Format: {detected_format}, Intent: {classified_intent}")

        if not detected_format or not classified_intent:
            print("Classifier failed to determine format or intent. Skipping further processing for this input.")
            continue

        # 2. Route to appropriate agent
        if detected_format == "JSON":
            json_content_str = ""
            if os.path.exists(str(content_or_path)):
                try:
                    with open(content_or_path, 'r', encoding='utf-8') as f:
                        json_content_str = f.read()
                except Exception as e:
                    print(f"Error reading JSON file {content_or_path} for JSON agent: {e}")
                    shared_memory_instance.update_entry(processing_id, "JSONAgent", {"status": "Error - File Read", "error": str(e)})
                    continue
            else:
                json_content_str = content_or_path

            if json_content_str:
                extracted_json_data, anomalies = json_agent.process(processing_id, json_content_str, classified_intent)
            else:
                print("No content to provide to JSON agent.")


        elif detected_format == "Email":
            email_text = ""
            if os.path.exists(str(content_or_path)):
                try:
                    with open(content_or_path, 'r', encoding='utf-8') as f:
                        email_text = f.read()
                except Exception as e:
                    print(f"Error reading email file {content_or_path} for Email agent: {e}")
                    shared_memory_instance.update_entry(processing_id, "EmailAgent", {"status": "Error - File Read", "error": str(e)})
                    continue
            else:
                email_text = content_or_path

            if email_text:
                crm_output = email_agent.process(processing_id, email_text, classified_intent)
            else:
                print("No content to provide to Email agent.")

        elif detected_format == "PDF":
            print(f"PDF '{source_hint}' classified with intent '{classified_intent}'. "
                    "Further PDF-specific data extraction agent not implemented in this demo beyond text for intent.")
            shared_memory_instance.update_entry(processing_id, "PDFAgent_Placeholder", {
                "status": "Classified (No dedicated processing agent)",
                "notes": "PDF content was used by Classifier for intent. Add PDF Agent for more."
            })
        else:
            print(f"No specialized agent available for format: {detected_format}")
            shared_memory_instance.update_entry(processing_id, "Router", {
                "status": "No Agent",
                "notes": f"Format {detected_format} does not have a dedicated agent."
            })
        print("--- End Processing Input ---")

    # 3. Displays Shared Memory contents 
    print("\n\n--- Shared Memory Log ---")
    for pid in all_processing_ids:
        entry = shared_memory_instance.get_entry(pid)
        if entry:
            print(f"\nProcessing ID: {entry['processing_id']}")
            print(f"   Input Source: {entry['input_source']}")
            print(f"   Entry Time: {entry['timestamp_entry']}")
            print(f"   Detected Format: {entry['detected_format']}")
            print(f"   Classified Intent: {entry['classified_intent']}")
            print(f"   Classifier Status: {entry['status_classifier']}")
            print(f"   Last Updated: {entry['last_updated_timestamp']}")
            print( "   Agent Stages:")
            for agent_name, stage_data in entry.get("stages", {}).items():
                print(f"     Agent: {agent_name}")
                for key, value in stage_data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        print(f"       {key}:")
                        print(json.dumps(value, indent=8).replace('\\n', '\n'))
                    else:
                        print(f"       {key}: {str(value)[:200] + '...' if len(str(value)) > 200 else value}")
        else:
            print(f"\nEntry with ID {pid} not found in shared memory (this shouldn't happen).")

    print("\n--- Demo Finished ---")

if __name__ == "__main__":
    main()
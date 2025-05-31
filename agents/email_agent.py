import re
from llm_utils.llm_client import llm_client_instance # Use the global instance
from memory.shared_memory import shared_memory_instance

# For more robust email parsing, Python's 'email' module would be better
# from email.parser import Parser

class EmailAgent:
    def __init__(self, llm_client=llm_client_instance, memory=shared_memory_instance):
        self.llm_client = llm_client
        self.memory = memory
        print("EmailAgent: Initialized.")

    def _extract_sender_basic(self, email_content):
        """Basic sender extraction using regex. For real .eml files, use email.parser."""
        match = re.search(r"From:\s*([^\n<]+)", email_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r"From:\s*.*?<(.*?)>", email_content, re.IGNORECASE) # Try to get email address if name is complex
        if match:
            return match.group(1).strip()
        return "Unknown Sender"

    def process(self, processing_id, email_content, intent):
        """
        Processes email content.
        """
        agent_name = "EmailAgent"
        log_data = {"status": "Processing", "intent_received": intent}
        self.memory.update_entry(processing_id, agent_name, log_data)

        sender = self._extract_sender_basic(email_content)
        urgency = self.llm_client.determine_urgency(email_content) # Can be keyword-based too

        print(f"EmailAgent: Attempting to extract details for intent '{intent}' from email by '{sender}'.")
        extracted_details_llm = self.llm_client.extract_email_details(email_content, intent)

        # Format for CRM-style usage
        crm_formatted_output = {
            "source_email_sender": sender,
            "detected_intent": intent,
            "assessed_urgency": urgency,
            "extracted_information": extracted_details_llm,
            "full_email_preview": email_content[:500] + "..." # Truncate for logging
        }

        log_data.update({
            "status": "Processed",
            "sender": sender,
            "urgency": urgency,
            "llm_extracted_details": extracted_details_llm,
            "crm_style_output": crm_formatted_output
        })
        self.memory.update_entry(processing_id, agent_name, log_data)

        print(f"EmailAgent: Processed ID {processing_id}. Sender: {sender}, Urgency: {urgency}")
        return crm_formatted_output
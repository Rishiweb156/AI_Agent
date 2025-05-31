import os
import json
import magic
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from llm_utils.llm_client import LLMClient
from memory.shared_memory import shared_memory_instance

class ClassifierAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.memory = shared_memory_instance
        print("ClassifierAgent: Initialized.")

    def _detect_format(self, input_data):
        # PRIORITY 1: Check if input_data is a path to an existing file
        if os.path.exists(input_data):
            # First, check by file extension (most reliable for common types)
            if input_data.lower().endswith(".json"):
                print(f"ClassifierAgent: Detected JSON format for {input_data} by extension.")
                return "JSON"
            elif input_data.lower().endswith(".pdf"):
                print(f"ClassifierAgent: Detected PDF format for {input_data} by extension.")
                return "PDF"
            elif input_data.lower().endswith((".eml", ".txt")): # Handle common email/text extensions
                print(f"ClassifierAgent: Detected Email/Text format for {input_data} by extension.")
                return "Email"
            
            # Fallback to python-magic for other or less common file types if extension check fails
            try:
                mime_type = magic.Magic(mime=True).from_file(input_data)
                if 'json' in mime_type: # Redundant but good as a double-check if extension failed
                    print(f"ClassifierAgent: Detected JSON format for {input_data} via magic (fallback).")
                    return "JSON"
                elif 'pdf' in mime_type: # Redundant but good as a double-check if extension failed
                    print(f"ClassifierAgent: Detected PDF format for {input_data} via magic (fallback).")
                    return "PDF"
                elif 'text' in mime_type or 'message' in mime_type:
                    print(f"ClassifierAgent: Detected Email/Text format for {input_data} via magic (fallback).")
                    return "Email"
                else:
                    print(f"ClassifierAgent: Detected unknown format for {input_data}: {mime_type} via magic.")
                    return "Other"
            except Exception as e:
                print(f"ClassifierAgent: Error using python-magic for {input_data}: {e}. Falling back to 'Other'.")
                return "Other"
        # PRIORITY 2: If not a file, assume it's raw string content
        elif isinstance(input_data, str):
            try:
                json.loads(input_data)
                print("ClassifierAgent: Detected JSON format from raw string input.")
                return "JSON"
            except json.JSONDecodeError:
                print("ClassifierAgent: Assuming Email format from raw string input (not valid JSON).")
                return "Email"
        return "Unknown" # Fallback if none of the above

    # Rest of the ClassifierAgent class remains the same from the last successful update
    # ... (_extract_text_from_pdf, _extract_content_for_llm, classify_and_route methods) ...

    def _extract_text_from_pdf(self, pdf_path):
        text_content = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            print(f"ClassifierAgent: Successfully extracted text from PDF {pdf_path}.")
            return text_content, None
        except PdfReadError as e:
            error_msg = f"PDF read error: {e}"
            print(f"ClassifierAgent: Error extracting text from PDF {pdf_path}: {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred extracting text from PDF {pdf_path}: {e}"
            print(f"ClassifierAgent: {error_msg}")
            return None, error_msg

    def _extract_content_for_llm(self, input_data, detected_format):
        content = None
        error_details = None

        if detected_format == "PDF": # Now this branch will be correctly hit for PDF files
            content, pdf_error = self._extract_text_from_pdf(input_data)
            if pdf_error:
                error_details = {"pdf_extraction_error": pdf_error}
        elif os.path.exists(input_data): # Handles JSON, EML, TXT files
            try:
                with open(input_data, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                error_details = {"file_read_error": str(e)}
                print(f"ClassifierAgent: Error reading file {input_data}: {e}")
        else: # Raw string content
            content = input_data
        return content, error_details

    def classify_and_route(self, input_data, source_hint):
        processing_id = self.memory.create_entry(source_hint)

        detected_format = self._detect_format(input_data)

        content_for_llm, extraction_error_details = self._extract_content_for_llm(input_data, detected_format)

        classified_intent = "Unknown"
        status_classifier = "Format Detected"

        if extraction_error_details:
            status_classifier = "Content Extraction Failed (No Intent)"
            print(f"ClassifierAgent: Could not extract content for intent classification. Details: {extraction_error_details}. Skipping intent classification.")
        elif content_for_llm:
            print(f"ClassifierAgent: Sending content for intent classification (format: {detected_format})...")
            classified_intent = self.llm_client.classify_intent(content_for_llm)
            status_classifier = "Classified"
        else:
            status_classifier = "No Content For Intent"
            print("ClassifierAgent: Input had no content for intent classification. Skipping intent classification.")

        classifier_stage_data = {
            "status_classifier": status_classifier,
            "input_source": source_hint,
            "detected_format": detected_format,
            "classified_intent": classified_intent,
            "raw_content_preview": (content_for_llm[:200] + '...' if content_for_llm and len(content_for_llm) > 200 else content_for_llm) if content_for_llm else "N/A",
            "text_used_for_intent": content_for_llm if content_for_llm else "N/A"
        }
        if extraction_error_details:
            classifier_stage_data["notes_or_errors"] = extraction_error_details

        self.memory.update_entry(processing_id, "ClassifierAgent", classifier_stage_data)

        return processing_id, detected_format, classified_intent, input_data
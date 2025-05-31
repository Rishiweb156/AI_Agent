import json
from memory.shared_memory import shared_memory_instance

# Example Schemas (can be loaded from files or defined more robustly)
SCHEMAS = {
    "Invoice": {
        "required_fields": ["invoice_id", "vendor_name", "customer_name", "total_amount", "issue_date"],
        "optional_fields": ["due_date", "items", "tax_amount"],
        "item_schema": {"item_name": str, "quantity": int, "unit_price": float} # Example item structure
    },
    "RFQ": {
        "required_fields": ["rfq_id", "requester_contact", "requested_items", "submission_deadline"],
        "optional_fields": ["project_name", "delivery_address"],
        "item_schema": {"product_id": str, "description": str, "quantity": int}
    }
    # Add more schemas as needed
}


class JSONAgent:
    def __init__(self, memory=shared_memory_instance):
        self.memory = memory
        print("JSONAgent: Initialized.")

    def process(self, processing_id, json_payload_str, intent):
        """
        Processes a JSON payload according to its intent and schema.
        """
        agent_name = "JSONAgent"
        log_data = {"status": "Processing", "intent_received": intent}
        self.memory.update_entry(processing_id, agent_name, log_data)

        extracted_data = {}
        anomalies = []

        try:
            payload = json.loads(json_payload_str)
        except json.JSONDecodeError as e:
            anomalies.append(f"Invalid JSON format: {e}")
            log_data.update({"status": "Error - Invalid JSON", "error": str(e), "anomalies": anomalies})
            self.memory.update_entry(processing_id, agent_name, log_data)
            return extracted_data, anomalies

        schema = SCHEMAS.get(intent)
        if not schema:
            anomalies.append(f"No schema defined for intent: {intent}. Performing generic extraction.")
            # Generic extraction: just take all top-level keys
            extracted_data = {k: v for k, v in payload.items()}
        else:
            # Field Extraction based on schema
            for field in schema.get("required_fields", []):
                if field in payload:
                    extracted_data[field] = payload[field]
                else:
                    anomalies.append(f"Missing required field: {field}")

            for field in schema.get("optional_fields", []):
                if field in payload:
                    extracted_data[field] = payload[field]

            # Example: Basic validation for items if schema defines it
            if "items" in payload and "item_schema" in schema:
                item_schema_fields = schema["item_schema"]
                valid_items = []
                # invalid_item_indices = [] # Not used, but you could keep it for more detailed logging
                for i, item in enumerate(payload["items"]): # Iterate over original payload's items
                    is_item_valid = True
                    if not isinstance(item, dict):
                        anomalies.append(f"Item at index {i} is not a dictionary.")
                        is_item_valid = False
                    else: # if it's a dict, check its fields
                        temp_item = {} # Store validated/extracted item data
                        for key, expected_type in item_schema_fields.items():
                            if key not in item:
                                anomalies.append(f"Item at index {i} missing field: {key}")
                                is_item_valid = False
                            # Basic type check (can be more robust)
                            elif not isinstance(item[key], expected_type):
                                anomalies.append(f"Item at index {i}, field '{key}': Expected type {expected_type.__name__}, got {type(item[key]).__name__}")
                                is_item_valid = False
                            else:
                                temp_item[key] = item[key]
                    if is_item_valid:
                        valid_items.append(temp_item) # Add the processed item
                    # else:
                        # invalid_item_indices.append(i) # Log invalid item index if needed
                extracted_data["items"] = valid_items # Update extracted_data with validated items


        status = "Processed"
        if anomalies:
            status = "Processed with anomalies"

        log_data.update({
            "status": status,
            "extracted_fields": extracted_data,
            "anomalies_or_missing_fields": anomalies
        })
        self.memory.update_entry(processing_id, agent_name, log_data)

        print(f"JSONAgent: Processed ID {processing_id}. Extracted: {len(extracted_data)} fields. Anomalies: {len(anomalies)}")
        return extracted_data, anomalies
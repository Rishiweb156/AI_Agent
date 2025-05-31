import datetime
import uuid

class SharedMemory:
    def __init__(self):
        # Using a simple in-memory dictionary for this example.
        # For persistence, consider SQLite or Redis.
        self._store = {}
        print("SharedMemory: Initialized (In-Memory Dictionary).")

    def _generate_id(self):
        return str(uuid.uuid4())

    def create_entry(self, input_source):
        """
        Creates a new entry in the shared memory.
        Returns the unique processing ID for this entry.
        """
        processing_id = self._generate_id()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._store[processing_id] = {
            "processing_id": processing_id,
            "timestamp_entry": timestamp,
            "last_updated_timestamp": timestamp,
            "input_source": input_source,
            "detected_format": None,
            "classified_intent": None,
            "status_classifier": "Pending",
            "stages": {} # To store agent-specific logs and data
        }
        print(f"SharedMemory: Created entry ID {processing_id} for source '{input_source}'.")
        return processing_id

    def update_entry(self, processing_id, agent_name, data_to_log):
        """
        Updates an existing entry with data from a specific agent/stage.
        `data_to_log` should be a dictionary.
        """
        if processing_id not in self._store:
            print(f"SharedMemory: Error - Attempted to update non-existent entry ID {processing_id}.")
            return False

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._store[processing_id]["last_updated_timestamp"] = timestamp

        if agent_name not in self._store[processing_id]["stages"]:
            self._store[processing_id]["stages"][agent_name] = {}

        self._store[processing_id]["stages"][agent_name].update(data_to_log)
        self._store[processing_id]["stages"][agent_name]["timestamp"] = timestamp # Add timestamp to agent stage

        # Update top-level convenience fields if provided in data_to_log
        if "detected_format" in data_to_log:
            self._store[processing_id]["detected_format"] = data_to_log["detected_format"]
        if "classified_intent" in data_to_log:
            self._store[processing_id]["classified_intent"] = data_to_log["classified_intent"]
        if "status_classifier" in data_to_log: # Example of agent-specific status
            self._store[processing_id]["status_classifier"] = data_to_log["status_classifier"]


        print(f"SharedMemory: Updated entry ID {processing_id} by agent '{agent_name}'.")
        return True

    def get_entry(self, processing_id):
        """
        Retrieves an entry by its processing ID.
        """
        entry = self._store.get(processing_id)
        if entry:
            print(f"SharedMemory: Retrieved entry ID {processing_id}.")
        else:
            print(f"SharedMemory: Entry ID {processing_id} not found.")
        return entry

    def get_all_entries(self):
        """
        Retrieves all entries in the memory.
        """
        print(f"SharedMemory: Retrieved all {len(self._store)} entries.")
        return self._store

# Global shared memory instance (can be managed better)
shared_memory_instance = SharedMemory()